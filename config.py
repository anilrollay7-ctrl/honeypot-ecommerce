"""
Configuration file for the Honeypot Dashboard
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'honeypot_db')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Cowrie Configuration
    COWRIE_LOG_PATH = os.getenv('COWRIE_LOG_PATH', './cowrie/var/log/cowrie')
    COWRIE_JSON_LOG = os.path.join(COWRIE_LOG_PATH, 'cowrie.json')
    
    # Dashboard Configuration
    DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', 5000))
    DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    
    # Collections
    COLLECTION_SESSIONS = 'sessions'
    COLLECTION_AUTH_ATTEMPTS = 'auth_attempts'
    COLLECTION_COMMANDS = 'commands'
    COLLECTION_DOWNLOADS = 'downloads'
    COLLECTION_STATS = 'stats'
