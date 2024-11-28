import os

# Configuration settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
