from flask import Blueprint, request, jsonify
from .services import generator

# Create a Blueprint for the routes
bp = Blueprint('main', __name__)

@bp.route('/create-assessment', methods=['POST'])
def create_assessment_route():
    """
    API endpoint to generate an assessment.
    Expects JSON with 'content' and 'assessment_type'.
    """
    data = request.json
    content = data.get('content')
    assessment_type = data.get('assessment_type', 'multiple_choice') # Default to multiple_choice

    if not content:
        return jsonify({"error": "Content is required to generate an assessment"}), 400

    try:
        # Call the core logic from the service layer
        result = generator_service.create_advanced_assessment(content, assessment_type)
        return jsonify(result)
    except Exception as e:
        # Return a generic error message if something goes wrong
        return jsonify({"error": "Failed to generate assessment", "details": str(e)}), 500
