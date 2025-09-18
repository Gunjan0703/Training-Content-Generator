from flask import Flask
from dotenv import load_dotenv
from .db import init_schema

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Ensure schema exists at startup
    init_schema()

    from . import routes
    app.register_blueprint(routes.bp)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "service": "multimedia-service"}, 200

    return app
