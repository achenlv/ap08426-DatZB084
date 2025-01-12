import ipaddress
from typing import Union, Optional
import csv
import os

def validate_ip(ip: str) -> Optional[str]:
  """Validē IP vai CIDR adreses formātu"""
  try:
    # Mēģina parsēt kā IP adresi
    ipaddress.ip_address(ip)
    return ip
  except ValueError:
    try:
      # Mēģina parsēt kā CIDR tīklu
      ipaddress.ip_network(ip, strict=False)
      return ip
    except ValueError:
      return None

# def validate_csv_file(filepath: str) -> bool:
#   """Validē, vai fails pastāv un ir derīgs CSV"""
#   if not os.path.exists(filepath):
#     return False
    
#   try:
#     with open(filepath, 'r') as f:
#       csv.Sniffer().sniff(f.read(1024))
#     return True
#   except csv.Error:
#     return False

# def validate_fail2ban_file(filepath: str) -> bool:
#   """Validē, vai fails pastāv un tam ir fail2ban formāts"""
#   if not os.path.exists(filepath):
#     return False
    
#   try:
#     with open(filepath, 'r') as f:
#       # Pārbauda pirmās dažas rindas fail2ban formāta indikatoriem
#       for _ in range(5):
#         line = f.readline()
#         if 'fail2ban' in line.lower():
#           return True
#     return False
#   except:
#     return False

def parse_ip_range(ip_range: str) -> list[str]:
  """Parsē IP adreses no CIDR diapazona"""
  network = ipaddress.ip_network(ip_range, strict=False)
  return [str(ip) for ip in network.hosts()]