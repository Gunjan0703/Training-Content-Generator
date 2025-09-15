from flask import Blueprint, request, jsonify
from .services import generator_service
from .agents.graph import build_graph

bp = Blueprint("assessment_service", __name__)
graph = build_graph()

@bp.route("/create-assessment", methods=["POST"])
def create_assessment_legacy():
    data = request.get_json(silent=True) or {}
    content = data.get("content")
    assessment_type = data.get("assessment_type", "multiple_choice")
    if not content:
        return jsonify({"error": "content is required"}), 400
    try:
        result = generator_service.create_advanced_assessment(content, assessment_type)
        return jsonify({"assessment": result, "type": assessment_type}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/create-assessment-agent", methods=["POST"])
def create_assessment_agent():
    data = request.get_json(silent=True) or {}
    content = data.get("content")
    if not content:
        return jsonify({"error": "content is required"}), 400
    try:
        state = {"content": content, "choice": "", "output": ""}
        result = graph.invoke(state)
        return jsonify({"assessment": result["output"], "type": result["choice"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
