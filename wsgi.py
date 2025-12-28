import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, '/home/your-username/VRChat-Memory-Keeper')

# Set the Flask application
from app import app as application

# Make sure the instance folder exists
instance_path = '/home/your-username/VRChat-Memory-Keeper/instance'
if not os.path.exists(instance_path):
    os.makedirs(instance_path)