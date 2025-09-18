from flask import Blueprint, request, jsonify
from .services import rag_service, vector_store_pg
from .agents.vector import build_graph

bp = Blueprint("personalization_service", __name__)
graph = build_graph()

# -------------------------
# Vector Store Endpoints
# -------------------------
@bp.route("/weakness", methods=["POST"])
def create_weakness():
    """Create a new weakness entry for a user."""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    weakness_text = data.get("weakness_text")
    
    if not user_id or not weakness_text:
        return jsonify({"error": "user_id and weakness_text are required"}), 400
    
    try:
        result = vector_store_pg.save_user_weakness(user_id, weakness_text)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/weakness/<int:weakness_id>", methods=["PUT"])
def update_weakness(weakness_id):
    """Update an existing weakness entry."""
    data = request.get_json(silent=True) or {}
    weakness_text = data.get("weakness_text")
    
    if not weakness_text:
        return jsonify({"error": "weakness_text is required"}), 400
    
    try:
        result = vector_store_pg.update_user_weakness(weakness_id, weakness_text)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/weakness/<int:weakness_id>", methods=["DELETE"])
def delete_weakness(weakness_id):
    """Delete a specific weakness entry."""
    try:
        if vector_store_pg.delete_user_weakness(weakness_id):
            return "", 204
        return jsonify({"error": "Weakness not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/weakness/user/<string:user_id>", methods=["GET"])
def get_user_weaknesses(user_id):
    """Get all weaknesses for a specific user."""
    try:
        weaknesses = vector_store_pg.get_user_weaknesses(user_id)
        return jsonify(weaknesses), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/weakness/similar", methods=["POST"])
def find_similar_weaknesses():
    """Find similar weaknesses using vector similarity."""
    data = request.get_json(silent=True) or {}
    query_text = data.get("query_text")
    limit = data.get("limit", 5)
    
    if not query_text:
        return jsonify({"error": "query_text is required"}), 400
    
    try:
        similar = vector_store_pg.find_similar_weaknesses(query_text, limit)
        return jsonify(similar), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# Personalization Endpoints
# -------------------------
@bp.route("/personalize-content", methods=["POST"])
def personalize_content():
    """Generate personalized content using RAG service."""
    data = request.get_json(silent=True) or {}
    topic = data.get("topic")
    user_id = data.get("user_id")
    user_role = data.get("user_role", "employee")

    if not topic or not user_id:
        return jsonify({"error": "topic and user_id are required"}), 400

    try:
        result = rag_service.generate_adaptive_content(topic, user_id, user_role)
        safe_result = {
            "personalized_content": str(result.get("personalized_content", "")),
            "weakness_context_used": bool(result.get("weakness_context_used", False))
        }
        return jsonify(safe_result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/personalize-content-agent", methods=["POST"])
def personalize_content_agent():
    """Generate personalized content using LangGraph agent."""
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
            "errors": [],
            "pretest": ""
        }

        result = graph.invoke(init)

        safe_result = {
            "decision": str(result.get("decision", "")),
            "weaknesses": str(result.get("weaknesses", "")),
            "pretest": str(result.get("pretest", "")),
            "personalized_content": str(getattr(result.get("draft", ""), "content", result.get("draft", ""))),
            "errors": [str(e) for e in result.get("errors", [])]
        }

        print(f"[DEBUG] Agent result: {safe_result}")

        return jsonify(safe_result), 200

    except Exception as e:
        return jsonify({
            "error": "Unable to serialize graph result",
            "details": str(e)
        }), 500
