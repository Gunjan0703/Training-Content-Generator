from flask import Blueprint, request, jsonify, send_from_directory
from .services.image_service import multimedia_service
import traceback

routes_bp = Blueprint('routes', __name__)

@routes_bp.route("/")
def root():
    return jsonify({"message": "Multimedia Service API"})

@routes_bp.route("/generate-image", methods=["POST"])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        image_type = data.get("image_type", "image")
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # This will work with the backward compatibility method
        result = multimedia_service.generate_output(prompt, output_type=image_type)
        
        if result:
            filename, image_url = result
            return jsonify({
                "image_url": image_url,
                "message": f"{'Flowchart' if image_type == 'flowchart' else 'Image'} generated successfully",
                "filename": filename
            })
        else:
            return jsonify({"error": "Image generation failed"}), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Serve generated images - this route should match the URL pattern in image_url
@routes_bp.route("/static/images/<filename>")
def serve_image(filename):
    """Serve generated images with correct MIME types."""
    try:
        # Determine the correct MIME type based on the file extension
        if filename.endswith(".svg"):
            mimetype = "image/svg+xml"
        elif filename.endswith(".png"):
            mimetype = "image/png"
        elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
            mimetype = "image/jpeg"
        else:
            mimetype = None  # Let Flask guess the mimetype
        
        return send_from_directory(multimedia_service.output_dir, filename, mimetype=mimetype)
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Image not found"}), 404