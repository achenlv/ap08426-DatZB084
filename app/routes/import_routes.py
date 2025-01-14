from flask import Blueprint, jsonify, request
from db.database import add_to_blacklist, add_to_whitelist, bulk_add, bulk_add_to_blacklist, bulk_add_to_whitelist
from app.models.schemas import IPEntry, BulkImportRequest
from utils.validators import validate_ip, parse_ip_range
import os
import csv
import requests
import logging
from datetime import datetime

bp = Blueprint('import', __name__, url_prefix='/import')
logger = logging.getLogger(__name__)

@bp.route('/single', methods=['GET','POST'])
def import_single():
  """Importē vienu IP adresi melnajā vai baltajā sarakstā"""
  try:
    data = request.get_json()
    ip = validate_ip(data.get('ip'))
    if not ip:
      return jsonify({'error': 'Invalid IP address'}), 400
      
    list_type = data.get('type', 'blacklist')
    entry = IPEntry(
      ip=ip,
      source=data.get('source', 'manual'),
      comment=data.get('comment'),
      reason=data.get('reason')
    )
    
    if list_type == 'blacklist':
      message = add_to_blacklist(
        ip=str(entry.ip),
        source=entry.source,
        reason=entry.reason,
        comment=entry.comment
      )
    else:
      message = add_to_whitelist(
        ip=str(entry.ip),
        source=entry.source,
        reason=entry.reason,
        comment=entry.comment
      )
    
    return jsonify({'message': message}), 201
    
  except Exception as e:
    logger.error(f"Single import failed: {str(e)}")
    return jsonify({'error': str(e)}), 400

@bp.route('/bulk', methods=['POST'])
def import_bulk():
  """Importē vairākas IP adreses melnajā vai baltajā sarakstā"""
  try:
    data = request.get_json()
    list_type = data.get('type', 'blacklist') 
    source = data.get('source', 'bulk-import')
    entries = []

    for ip in data['ips']:
      validated_ip = validate_ip(ip)
      if validated_ip:
        if '/' in validated_ip:
          ip_list = parse_ip_range(validated_ip)
          entries.extend([
            (
              ip, 
              source, 
              datetime.now(), 
              data.get('reason'), 
              data.get('comment')
            )
            for ip in ip_list
          ])
        else:
          entries.append(
            (
              validated_ip, 
              source, 
              datetime.now(), 
              data.get('reason'), 
              data.get('comment')
            )
          )
    
    if not entries:
      return jsonify({'error': 'No valid IPs provided'}), 400

    message = bulk_add(entries, list_type, source)
    
    return jsonify({'message': message}), 201
    
  except Exception as e:
    logger.error(f"Bulk import failed: {str(e)}")
    return jsonify({'error': str(e)}), 400

@bp.route('/blocklist_de', methods=['GET','POST'])
def import_blocklist_de():
  """Importē IP adreses no blocklist.de"""
  try:
    response = requests.get('https://api.blocklist.de/getlast.php?time=3600')
    if response.status_code != 200:
      return jsonify({'error': 'Failed to fetch from blocklist.de'}), 500
      
    ips = response.text.strip().split('\n')
    entries = [
      (ip, 'blocklist.de', datetime.now(), None, None, 'Imported from blocklist.de')
      for ip in ips if validate_ip(ip)
    ]
    
    bulk_add_to_blacklist(entries)
    return jsonify({'message': f'Added {len(entries)} IPs from blocklist.de'}), 201
    
  except Exception as e:
    logger.error(f"Blocklist.de import failed: {str(e)}")
    return jsonify({'error': str(e)}), 400
