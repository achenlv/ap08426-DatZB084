import sqlite3
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager
from flask import current_app
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_db():
  """
  Izveido savienojumu ar datubāzi un nodrošina, ka tas tiek aizvērts pēc lietošanas.
  """
  db = sqlite3.connect(current_app.config['DATABASE_PATH'])
  db.row_factory = sqlite3.Row
  try:
    yield db
  finally:
    db.close()

def init_db():
  """
  Inicializē datubāzi, izveidojot nepieciešamās tabulas, ja tās nepastāv.
  """
  with get_db() as db:
    db.execute('''
      CREATE TABLE IF NOT EXISTS blacklist (
        ip TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        added_at TIMESTAMP NOT NULL,
        reason TEXT,
        comment TEXT
      )
    ''')
    
    db.execute('''
      CREATE TABLE IF NOT EXISTS whitelist (
        ip TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        added_at TIMESTAMP NOT NULL,
        reason TEXT,
        comment TEXT
      )
    ''')
    db.commit()

def add_to_blacklist(ip: str, source: str, reason: Optional[str], comment: Optional[str]) -> str:
  """
  Pievieno vienu IP melnajam sarakstam.
  Ja IP jau pastāv melnajā sarakstā, atgriež brīdinājuma ziņojumu.
  """
  with get_db() as db:
    try:
      db.execute('''
        INSERT INTO blacklist (ip, source, added_at, reason, comment)
        VALUES (?, ?, ?, ?, ?)
      ''', (ip, source, datetime.now(), reason, comment))
      db.commit()
      message = f"Added {ip} to blacklist from source {source}"
      logger.info(message)
      return message
    except sqlite3.IntegrityError:
      message = f"IP {ip} already exists in blacklist"
      logger.warning(message)
      return message

def add_to_whitelist(ip: str, source: str, reason: Optional[str], comment: Optional[str]) -> str:
  """
  Pievieno vienu IP baltajam sarakstam.
  Ja IP jau pastāv baltajā sarakstā, atgriež brīdinājuma ziņojumu.
  """
  with get_db() as db:
    try:
      db.execute('''
        INSERT INTO whitelist (ip, source, added_at, reason, comment)
        VALUES (?, ?, ?, ?, ?)
      ''', (ip, source, datetime.now(), reason, comment))
      db.commit()
      message = f"Added {ip} to whitelist from source {source}"
      logger.info(message)
      return message
    except sqlite3.IntegrityError:
      message = f"IP {ip} already exists in whitelist"
      logger.warning(message)
      return message

def get_list(source: Optional[str] = None, list_type: str = 'blacklist') -> List[dict]:
  """
  Iegūst IP sarakstu no norādītā saraksta veida (melnā/baltā saraksta).
  Ja norādīts avots, filtrē pēc avota.
  """
  with get_db() as db:
    query = f'SELECT * FROM {list_type}'
    params = []
    
    if source:
      query += ' WHERE source = ?'
      params.append(source)
    
    rows = db.execute(query, params).fetchall()
    return [dict(row) for row in rows]

def get_blacklist(source: Optional[str] = None) -> List[dict]:
  """
  Iegūst melno sarakstu, izņemot IP, kas atrodas baltajā sarakstā.
  Ja norādīts avots, filtrē pēc avota.
  """
  with get_db() as db:
    query = '''
      SELECT * FROM blacklist 
      WHERE ip NOT IN (SELECT ip FROM whitelist)
    '''
    params = []

    if source:
      query += ' AND source = ?'
      params.append(source)
      
    rows = db.execute(query, params).fetchall()
    return [dict(row) for row in rows]

def get_whitelist(source: Optional[str] = None) -> List[dict]:
  """
  Iegūst balto sarakstu.
  Ja norādīts avots, filtrē pēc avota.
  """
  with get_db() as db:
    query = 'SELECT * FROM whitelist'
    params = []
    
    if source:
      query += ' WHERE source = ?'
      params.append(source)
    
    rows = db.execute(query, params).fetchall()
    return [dict(row) for row in rows]

def bulk_add(entries: List[tuple], list_type: str, source: Optional[str] = None) -> str:
  """
  Masveidā pievieno IP norādītajam saraksta veidam (melnā/baltā saraksta).
  """
  with get_db() as db:
    db.executemany(f'''
      INSERT OR IGNORE INTO {list_type} (ip, source, added_at, reason, comment)
      VALUES (?, ?, ?, ?, ?)
    ''', entries)
    db.commit()
    logger.info(f"Added {len(entries)} IPs to {list_type}")
  return f'Added {len(entries)} IPs to {list_type}'

def bulk_add_to_blacklist(entries: List[tuple], source: Optional[str] = None):
  """
  Masveidā pievieno IP melnajam sarakstam.
  """
  with get_db() as db:
    db.executemany('''
      INSERT OR IGNORE INTO blacklist (ip, source, added_at, comment)
      VALUES (?, ?, ?, ?)
    ''', entries)
    db.commit()
    logger.info(f"Added {len(entries)} IPs to blacklist")

def bulk_add_to_whitelist(entries: List[tuple], source: Optional[str] = None):
  """
  Masveidā pievieno IP baltajam sarakstam.
  """
  with get_db() as db:
    db.executemany('''
      INSERT OR IGNORE INTO whitelist (ip, source, added_at, reason, comment)
      VALUES (?, ?, ?, ?, ?)
    ''', entries)
    db.commit()
    logger.info(f"Added {len(entries)} IPs to whitelist")