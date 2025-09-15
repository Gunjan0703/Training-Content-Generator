from flask import Blueprint, request, jsonify
from .services import localization_service
from .agents.graph import build_graph

bp = Blueprint("translation_service", __name__)
graph = build_graph()

@bp.route("/localize-text", methods=["POST"])
def localize_text():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    target_language = data.get("target_language")
    glossary = data.get("glossary")  # dict term->approved translation
    localize = data.get("localize", False)

    if not text or not target_language:
        return jsonify({"error": "text and target_language are required"}), 400

    try:
        result = localization_service.localize_text(text, target_language, glossary, localize)
        return jsonify({"localized_text": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/localize-text-agent", methods=["POST"])
def localize_text_agent():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    target_language = data.get("target_language")
    glossary = data.get("glossary")
    localize = data.get("localize", False)
    style = data.get("style", "neutral")  # optional style guide hint

    if not text or not target_language:
        return jsonify({"error": "text and target_language are required"}), 400

    init = {
        "text": text,
        "target_language": target_language,
        "glossary": glossary or {},
        "localize": bool(localize),
        "style": style,
        "draft": "",
        "qa_notes": "",
        "final": "",
        "errors": []
    }
    try:
        result = graph.invoke(init)
        return jsonify({
            "localized_text": result.get("final") or result.get("draft", ""),
            "qa_notes": result.get("qa_notes", ""),
            "errors": result.get("errors", [])
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
