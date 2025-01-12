#!/usr/bin/env python3
import requests
import subprocess
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import time
from typing import List, Set, Optional
import json
from config.settings import HostSettings

# Load settings
settings = HostSettings()

# Setup logging
def setup_logging():
  os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
  
  formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )
  
  file_handler = RotatingFileHandler(
    settings.LOG_FILE,
    maxBytes=10485760,  # 10MB
    backupCount=5
  )
  file_handler.setFormatter(formatter)
  
  console_handler = logging.StreamHandler()
  console_handler.setFormatter(formatter)
  
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  logger.addHandler(file_handler)
  logger.addHandler(console_handler)
  
  return logger

logger = setup_logging()

def setup_base_rules():
  """Setup basic IPFW rules to ensure we don't lock ourselves out"""
  try:
    # First, ensure our base rules are in place (before any blocking rules)
    base_rules = [
      # Allow loopback traffic
      (100, "allow ip from any to any via lo0"),
      # Allow established connections
      (200, "allow ip from any to any established"),
      # Allow outgoing traffic
      (300, "allow ip from any to any out keep-state"),
      # Allow DNS
      (400, "allow udp from any to any 53 keep-state"),
      # Allow SSH (adjust port if needed)
      (500, "allow tcp from any to any 22 keep-state"),
      # Add other necessary services here
      # The main blocking rule will be at settings.IPFW_RULE (default 1035)
    ]
    
    for rule_num, rule in base_rules:
      result = subprocess.run(
        ['ipfw', 'show', str(rule_num)],
        capture_output=True,
        text=True
      )
      
      if "65535" not in result.stdout:  # Rule doesn't exist
        subprocess.run(
          ['ipfw', 'add', str(rule_num), rule],
          check=True,
          capture_output=True
        )
        logger.info(f"Added base rule {rule_num}: {rule}")
    
    # Add our table-based blocking rule if it doesn't exist
    block_rule = f"deny ip from table({settings.IPFW_TABLE}) to any"
    result = subprocess.run(
      ['ipfw', 'show', str(settings.IPFW_RULE)],
      capture_output=True,
      text=True
    )
    
    if "65535" not in result.stdout:  # Rule doesn't exist
      subprocess.run(
        ['ipfw', 'add', str(settings.IPFW_RULE), block_rule],
        check=True,
        capture_output=True
      )
      logger.info(f"Added blocking rule {settings.IPFW_RULE}: {block_rule}")
    
    # Add final default allow rule if not present
    result = subprocess.run(
      ['ipfw', 'show', '65534'],
      capture_output=True,
      text=True
    )
    
    if "65535" not in result.stdout:  # Rule doesn't exist
      subprocess.run(
        ['ipfw', 'add', '65534', 'allow ip from any to any'],
        check=True,
        capture_output=True
      )
      logger.info("Added default allow rule")
      
  except subprocess.CalledProcessError as e:
    logger.error(f"Error setting up base rules: {e.stderr}")
    raise
  except Exception as e:
    logger.error(f"Unexpected error setting up base rules: {str(e)}")
    raise

def get_current_ipfw_ips() -> Set[str]:
  """Get currently blocked IPs from IPFW table"""
  try:
    result = subprocess.run(
      ['ipfw', 'table', str(settings.IPFW_TABLE), 'list'],
      capture_output=True,
      text=True
    )
    
    if result.returncode != 0:
      logger.error(f"Failed to get IPFW table: {result.stderr}")
      return set()
      
    return {line.split()[0] for line in result.stdout.splitlines() if line}
    
  except Exception as e:
    logger.error(f"Error getting IPFW table: {str(e)}")
    return set()

def update_ipfw_table(ips_to_add: Set[str], ips_to_remove: Set[str], verify_access: Optional[str] = None):
  """
  Update IPFW table with new IPs
  
  Args:
      ips_to_add: Set of IPs to add to the block list
      ips_to_remove: Set of IPs to remove from the block list
      verify_access: Optional IP to verify access after update (e.g., API server IP)
  """
  try:
    # First ensure base rules are in place
    setup_base_rules()
    
    # Remove IPs
    for ip in ips_to_remove:
      result = subprocess.run(
        ['ipfw', 'table', str(settings.IPFW_TABLE), 'delete', ip],
        capture_output=True
      )
      if result.returncode != 0:
        logger.error(f"Failed to remove IP {ip}: {result.stderr}")
    
    # Add IPs
    for ip in ips_to_add:
      # Don't block the API server
      if verify_access and ip == verify_access:
        logger.warning(f"Skipping blocking API server IP: {ip}")
        continue
        
      result = subprocess.run(
        ['ipfw', 'table', str(settings.IPFW_TABLE), 'add', ip],
        capture_output=True
      )
      if result.returncode != 0:
        logger.error(f"Failed to add IP {ip}: {result.stderr}")
    
    # Verify we can still reach the API server if specified
    if verify_access:
      try:
        response = requests.get(f"{settings.HOST_API_URL}/health", timeout=5)
        if response.status_code != 200:
          logger.error("Lost access to API server after update!")
          # Could implement rollback here if needed
      except requests.exceptions.RequestException as e:
        logger.error(f"Cannot reach API server after update: {str(e)}")
    
  except Exception as e:
    logger.error(f"Error updating IPFW table: {str(e)}")

def sync_with_api():
  """Sync local IPFW table with API blacklist"""
  try:
    # Extract API server IP from HOST_API_URL
    api_server = settings.HOST_API_URL.split('://')[1].split(':')[0]
    
    # Get blacklist from API
    response = requests.get(f"{settings.HOST_API_URL}/export/iptables")
    if response.status_code != 200:
      logger.error(f"Failed to get blacklist: {response.text}")
      return
      
    api_ips = set(response.json()['ips'])
    current_ips = get_current_ipfw_ips()
    
    # Calculate differences
    ips_to_add = api_ips - current_ips
    ips_to_remove = current_ips - api_ips
    
    if ips_to_add or ips_to_remove:
      update_ipfw_table(ips_to_add, ips_to_remove, verify_access=api_server)
      logger.info(f"Added {len(ips_to_add)} IPs, removed {len(ips_to_remove)} IPs")
    else:
      logger.info("No updates needed")
    
  except Exception as e:
    logger.error(f"Sync failed: {str(e)}")

def main():
  logger.info("Starting host sync script")
  
  # Ensure base rules are setup on startup
  setup_base_rules()
  
  while True:
    sync_with_api()
    time.sleep(60)  # Sync every minute

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    logger.info("Shutting down host sync script")
    sys.exit(0)