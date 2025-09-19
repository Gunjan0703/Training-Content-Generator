from flask import Blueprint, request, jsonify, send_from_directory
from .services.image_service import image_service
import os

routes_bp = Blueprint('routes', __name__)

@routes_bp.route("/")
def root():
    return jsonify({"message": "Multimedia Service API"})

@routes_bp.route("/generate-image", methods=['POST'])
def generate_image():
    """Generate any type of image including flowcharts."""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        image_type = data.get('image_type', 'general')  # Default to general if not specified
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
            
        filename, image_path = image_service.generate_and_store_image(prompt, image_type)
        return jsonify({
            "image_url": f"/static/{filename}",
            "message": f"{'Flow chart' if image_type == 'flowchart' else 'Image'} generated successfully",
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
