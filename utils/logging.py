import logging
import os
from logging.handlers import RotatingFileHandler
from flask import current_app, request
from werkzeug.local import LocalProxy

def get_log_dir():
    """
    Iegūst log direktoriju no Flask  konfigurācijas.
    Ja nav pieejams, atgriež noklusējuma 'logs' direktoriju.
    """
    try:
        return current_app.config.get('LOG_DIR', 'logs')
    except RuntimeError:
        # Atgriež noklusējumu, ja ārpus lietojumprogrammas konteksta
        return 'logs'

class RequestFormatter(logging.Formatter):
    """
    Pielāgots log formatētājs, kas pievieno pieprasījuma attālo adresi žurnāla ierakstam.
    """
    def format(self, record):
        record.remote_addr = request.remote_addr if request else 'N/A'
        return super().format(record)

def setup_logging():
    """
    Iestata log veidošanu.
    Ietver log direktorijas izveidi, log formatētāju un apstrādātāju konfigurēšanu,
    un līmeņa iestatīšanu logā.
    """
    # Iegūst žurnālu direktoriju no konfigurācijas vai noklusējuma
    log_dir = get_log_dir()
    
    # Izveido žurnālu direktoriju, ja tas nepastāv
    os.makedirs(log_dir, exist_ok=True)
    
    # Konfigurē žurnālu veidošanu
    formatter = RequestFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(remote_addr)s - %(message)s'
    )
    
    # Iestata failu apstrādātāju
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'api.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Iestata konsoles apstrādātāju
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Konfigurē saknes žurnālu
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Noņem esošos apstrādātājus, ja tādi ir
    root_logger.handlers.clear()
    
    # Pievieno apstrādātājus
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Apspiež werkzeug žurnālu veidošanu
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    return root_logger