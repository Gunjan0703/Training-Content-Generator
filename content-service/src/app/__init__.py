import os
from flask import Flask
from dotenv import load_dotenv

# Load env variables for local/dev
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Register blueprints
    from . import routes
    app.register_blueprint(routes.bp)

    # Basic health endpoint
    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "service": "content-service"}, 200

    return app
