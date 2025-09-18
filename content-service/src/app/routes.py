from flask import Blueprint, request, jsonify
from .services import agent_service
from .agents.graph import build_graph

bp = Blueprint("content_service", __name__)


@bp.route("/create-curriculum", methods=["POST"])
def create_curriculum_legacy():
    """
    Legacy endpoint using agent_service.
    Expects JSON: { "topic": "Some Training Topic" }
    """
    data = request.get_json(silent=True) or {}
    topic = data.get("topic")
    if not topic:
        return jsonify({"error": "topic is required"}), 400
    try:
        out = agent_service.create_full_curriculum(topic)
        return jsonify(out), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/create-curriculum-agent", methods=["POST"])
def create_curriculum_agent():
    """
    New endpoint using LangGraph pipeline.
    Expects JSON: { "topic": "Some Training Topic" }
    """
    data = request.get_json(silent=True) or {}
    topic = data.get("topic")
    if not topic:
        return jsonify({"error": "topic is required"}), 400

    try:
        graph = build_graph()   # returns compiled StateGraph
        result = graph.invoke({
            "topic": topic,
            "modules": [],
            "drafts": {},
            "final": "",
            "errors": []
        })
        return jsonify({
            "topic": topic,
            "modules": result.get("modules", []),
            "curriculum": result.get("final", ""),
            "errors": result.get("errors", [])
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
