from flask import Blueprint, request, jsonify
from .services import summarizer_service

bp = Blueprint("summarization_service", __name__)

@bp.route("/summarize-text", methods=["POST"])
def summarize_text():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    format_type = data.get("format_type", "bulleted list")
    length = data.get("length", "medium")

    if not text:
        return jsonify({"error": "text is required"}), 400

    try:
        summary = summarizer_service.summarize_text_custom(text, format_type, length)
        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
