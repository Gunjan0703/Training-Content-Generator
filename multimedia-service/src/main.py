import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from app.routes import routes_bp

# Create Flask app
app = Flask(__name__, static_folder='static')

# Configure CORS
CORS(app)

# Configure the directory where images are saved
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "images"), exist_ok=True)

# Register blueprints
app.register_blueprint(routes_bp)

# Add a route to serve static images from the correct directory
@app.route('/static/images/<path:filename>')
def serve_static_images(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)