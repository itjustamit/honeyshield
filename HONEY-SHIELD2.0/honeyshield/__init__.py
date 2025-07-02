from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///honeyshield.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import routes after app initialization to avoid circular imports
from honeyshield import routes 