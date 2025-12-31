# This file contains the WSGI configuration required to serve up your Flask app.
# It should be placed at /var/www/kktime2024_pythonanywhere_com_wsgi.py
# on your PythonAnywhere account.

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, '/home/KKTIME2024/AS-2')

# Set the Flask application
from app import app as application

# Make sure the instance folder exists
instance_path = os.path.join('/home/KKTIME2024/AS-2', 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Set environment variables if needed
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-production-secret-key-here'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/KKTIME2024/AS-2/instance/vrchat_memories.db'
