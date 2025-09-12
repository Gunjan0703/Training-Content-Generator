from flask import Flask
from dotenv import load_dotenv

# Load environment variables from a .env file (for AWS credentials)
load_dotenv()

def create_app():
    """Application factory function."""
    app = Flask(__name__)

    # Import and register the routes from the routes.py file
    from . import routes
    app.register_blueprint(routes.bp)

    return app
