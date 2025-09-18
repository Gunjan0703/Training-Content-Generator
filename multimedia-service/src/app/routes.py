from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from .services.image_service import generate_and_store_image
from .services.storage_db import fetch_media

bp = Blueprint("multimedia_service", __name__)

@bp.route("/generate-image", methods=["POST"])
def generate_image():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    try:
        media_id = generate_and_store_image(prompt)
        return jsonify({"media_id": media_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/media/<int:media_id>", methods=["GET"])
def get_media(media_id: int):
    row = fetch_media(media_id)
    if not row:
        return jsonify({"error": "not found"}), 404
    filename, mimetype, size_bytes, data = row
    return send_file(BytesIO(bytes(data)), mimetype=mimetype, as_attachment=False, download_name=filename)
