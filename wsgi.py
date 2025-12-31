from app import app as application
import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set the Flask application

# Make sure the instance folder exists
instance_path = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)
