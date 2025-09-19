from flask import Blueprint, request, jsonify, send_from_directory
from .services.image_service import image_service
import traceback

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

        # ✅ use correct entrypoint
        result = image_service.generate_image_with_clear_text(prompt, method="auto")

        if not result:
            return jsonify({"error": "Image generation failed"}), 500

        filename, image_url = result

        return jsonify({
            "image_url": image_url,
            "message": f"{'Flow chart' if image_type == 'flowchart' else 'Image'} generated successfully",
            "filename": filename
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ✅ expose generated images to frontend
@routes_bp.route("/generated_images/<filename>")
def serve_image(filename):
    return send_from_directory(image_service.output_dir, filename)
