import os

DB_USER = os.environ.get('DB_USER', 'root')
DB_NAME = os.environ.get('DB_NAME', 'project3510')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

APP_HOST = os.environ.get('APP_HOST', '127.0.0.1')
APP_PORT = int(os.environ.get('APP_PORT', 5001))
APP_DEBUG = os.environ.get('APP_DEBUG', 'True') == 'True'