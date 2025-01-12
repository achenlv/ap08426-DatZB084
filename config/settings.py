import os
from dataclasses import dataclass

@dataclass
class APISettings:
  API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
  API_PORT: int = int(os.getenv('API_PORT', 5000))
  DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'saraksts.db')
  ELASTIFLOW_DIR: str = os.getenv('ELASTIFLOW_DIR', 'data/elastiflow')
  FAIL2BAN_DIR: str = os.getenv('FAIL2BAN_DIR', 'data/fail2ban')
  LOG_DIR: str = os.getenv('LOG_DIR', 'logs')
  DEBUG: bool = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')

@dataclass
class HostSettings:
  HOST_API_URL: str = os.getenv('HOST_API_URL', 'http://localhost:5000')
  IPFW_TABLE: int = int(os.getenv('IPFW_TABLE', 2))
  IPFW_RULE: int = int(os.getenv('IPFW_RULE', 1035))
  LOG_FILE: str = os.getenv('HOST_LOG_FILE', 'logs/host.log')

@dataclass
class ControllerSettings:
  CONTROLLER_API_URL: str = os.getenv('CONTROLLER_API_URL', 'http://localhost:5000')
  SCAN_INTERVAL: int = int(os.getenv('SCAN_INTERVAL', 300))
  LOG_FILE: str = os.getenv('CONTROLLER_LOG_FILE', 'logs/controller.log')