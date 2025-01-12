from flask import Flask
from app.routes import export, import_routes
from config.settings import APISettings
from db.database import init_db
from utils.logging import setup_logging

def create_app():
  """Initializē Flask app"""
  app = Flask(__name__)
  app.config.from_object(APISettings())
  
  with app.app_context():
    setup_logging()
    init_db()

    app.register_blueprint(export.bp)
    app.register_blueprint(import_routes.bp)
  
  return app

if __name__ == '__main__':
  app = create_app()
  print(f"Debug mode is {'on' if app.config['DEBUG'] else 'off'}")
  app.run(
    host=app.config['API_HOST'],
    port=app.config['API_PORT'],
    debug=app.config['DEBUG']
  )