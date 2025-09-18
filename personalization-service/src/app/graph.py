import os
from app.routes import personalize_content,personalize_content_agent
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Import and register routes blueprint
    from . import routes
    app.register_blueprint(routes.bp, url_prefix="/api")

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "service": "personalization-service"}, 200

    return app
