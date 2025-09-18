import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    from . import routes
    app.register_blueprint(routes.bp)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "service": "summarization-service"}, 200

    return app
