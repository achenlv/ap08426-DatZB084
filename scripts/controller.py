#!/usr/bin/env python3
import requests
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import time
from typing import Optional
import schedule
from datetime import datetime
from config.settings import ControllerSettings

# Load settings
settings = ControllerSettings()

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

def import_from_source(source: str, data: Optional[dict] = None) -> Optional[requests.Response]:
  """Import IPs from specified source"""
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
      f"{settings.CONTROLLER_API_URL}/import/{source}",
      json=data if data else {},
      headers=headers,
      timeout=300  # 5 minute timeout for imports
    )
    
    if response.status_code == 201:
      result = response.json()
      logger.info(f"Successfully imported from {source}: {result['message']}")
      return response
    else:
      logger.error(f"Failed to import from {source}: {response.text}")
      return None
      
  except requests.exceptions.RequestException as e:
    logger.error(f"Request failed for {source}: {str(e)}")
    return None
  except Exception as e:
    logger.error(f"Error importing from {source}: {str(e)}")
    return None

def add_to_whitelist(ip: str, reason: str):
  """Add IP to whitelist"""
  try:
    data = {
      'ip': ip,
      'type': 'whitelist',
      'source': 'controller',
      'reason': reason,
      'comment': f'Added by controller on {datetime.now()}'
    }
    
    response = requests.post(
      f"{settings.CONTROLLER_API_URL}/import/single",
      json=data,
      timeout=30
    )
    
    if response.status_code == 201:
      logger.info(f"Successfully whitelisted IP {ip}")
    else:
      logger.error(f"Failed to whitelist IP {ip}: {response.text}")
      
  except Exception as e:
    logger.error(f"Error whitelisting IP {ip}: {str(e)}")

def run_imports():
  """Run all configured imports"""
  try:
    logger.info("Starting scheduled import run")
    
    # Import from blocklist.de
    import_from_source('blocklist_de')
    
    # Import from elastiflow
    import_from_source('elastiflow')
    
    # Import from fail2ban
    import_from_source('fail2ban')
    
    logger.info("Completed scheduled import run")
    
  except Exception as e:
    logger.error(f"Error during import run: {str(e)}")

def main():
  logger.info("Starting controller script")
  
  # Schedule imports
  schedule.every(settings.SCAN_INTERVAL).seconds.do(run_imports)
  
  # Run initial import
  run_imports()
  
  try:
    # Keep running
    while True:
      schedule.run_pending()
      time.sleep(1)
      
  except Exception as e:
    logger.error(f"Controller script error: {str(e)}")
    sys.exit(1)
  finally:
    logger.info("Shutting down controller script")

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    logger.info("Received shutdown signal")
    sys.exit(0)
  except Exception as e:
    logger.error(f"Fatal error: {str(e)}")
    sys.exit(1)