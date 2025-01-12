from flask import Blueprint, jsonify, request, send_file, current_app
from db.database import get_blacklist, get_whitelist
from app.models.schemas import ExportFilter
import csv
import io
import logging

bp = Blueprint('export', __name__, url_prefix='/export')
logger = logging.getLogger(__name__)

@bp.route('/blacklist', methods=['GET'])
def export_blacklist():
  """Eksportē melno sarakstu CSV or JSON"""
  # Get query parameters
  export_format = request.args.get('format', 'json')
  source = request.args.get('source')
  
  try:
    # Get blacklist
    logger.info("Called /export/blacklist endpoint")
    blacklist = get_blacklist(source=source)
    
    if export_format == 'csv':
      # Create CSV in memory
      output = io.StringIO()
      writer = csv.DictWriter(output, fieldnames=['ip', 'source', 'added_at', 'reason', 'comment'])
      writer.writeheader()
      writer.writerows(blacklist)
      
      # Create response
      output.seek(0)
      return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='blacklist.csv'
      )
    else:
      return jsonify(blacklist)
      
  except Exception as e:
    logger.error(f"Blacklist export failed: {str(e)}")
    return jsonify({'error': str(e)}), 400

@bp.route('/whitelist', methods=['GET'])
def export_whitelist():
  """Eksportē balto sarakstu CSV or JSON"""
  # Get query parameters
  export_format = request.args.get('format', 'json')
  source = request.args.get('source')
  
  try:
    # Get whitelist
    logger.info("Called /export/whitelist endpoint")
    whitelist = get_whitelist(source=source)
    
    if export_format == 'csv':
      # Create CSV in memory
      output = io.StringIO()
      writer = csv.DictWriter(output, fieldnames=['ip', 'source', 'added_at', 'reason', 'comment'])
      writer.writeheader()
      writer.writerows(whitelist)
      
      # Create response
      output.seek(0)
      return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='whitelist.csv'
      )
    else:
      return jsonify(whitelist)
      
  except Exception as e:
    logger.error(f"Whitelist export failed: {str(e)}")
    return jsonify({'error': str(e)}), 400

@bp.route('/iptables', methods=['GET'])
def export_iptables():
  """Eksportē aktīvo melno sarkastu JSON"""
  try:
    # Get current blacklist excluding expired entries
    logger.info("Called /export/iptables endpoint")
    blacklist = get_blacklist()
    
    # Extract just the IPs
    ips = [entry['ip'] for entry in blacklist]
    
    return jsonify({
      'count': len(ips),
      'ips': ips,
      'format': 'plain'
    })
    
  except Exception as e:
    logger.error(f"Iptables export failed: {str(e)}")
    return jsonify({'error': str(e)}), 400

@bp.route('/iptables/rules', methods=['GET'])
def export_iptables_rules():
  """Eksportē aktīvo melno sarkastu iptables komandu formātā"""
  try:
    logger.info("Called /export/iptables/rules endpoint")
    blacklist = get_blacklist()
    rules = []
    for entry in blacklist:
      rules.append(
        f"iptables -A INPUT -s {entry['ip']} -j DROP # {entry['source']}"
      )
    
    return jsonify({
      'count': len(rules),
      'rules': rules,
      'format': 'iptables'
    })
    
  except Exception as e:
    logger.error(f"Iptables rules export failed: {str(e)}")
    return jsonify({'error': str(e)}), 400