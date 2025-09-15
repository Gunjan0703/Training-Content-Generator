from flask import Blueprint, request, jsonify
from .services import rag_service
from .agents.graph import build_graph

bp = Blueprint("personalization_service", __name__)
graph = build_graph()

@bp.route("/personalize-content", methods=["POST"])
def personalize_content():
    data = request.get_json(silent=True) or {}
    topic = data.get("topic")
    user_id = data.get("user_id")
    user_role = data.get("user_role", "employee")

    if not topic or not user_id:
        return jsonify({"error": "topic and user_id are required"}), 400

    try:
        result = rag_service.generate_adaptive_content(topic, user_id, user_role)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/personalize-content-agent", methods=["POST"])
def personalize_content_agent():
    data = request.get_json(silent=True) or {}
    topic = data.get("topic")
    user_id = data.get("user_id")
    user_role = data.get("user_role", "employee")

    if not topic or not user_id:
        return jsonify({"error": "topic and user_id are required"}), 400

    try:
        init = {
            "topic": topic,
            "user_id": user_id,
            "user_role": user_role,
            "decision": "direct",
            "weaknesses": "",
            "draft": "",
            "errors": []
        }
        result = graph.invoke(init)
        return jsonify({
            "decision": result.get("decision"),
            "weaknesses": result.get("weaknesses", ""),
            "personalized_content": result.get("draft", ""),
            "errors": result.get("errors", [])
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
