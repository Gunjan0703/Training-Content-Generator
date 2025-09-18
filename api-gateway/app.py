import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Service URLs (use docker-compose/k8s service names)
SERVICE_URLS = {
    "content": os.getenv("CONTENT_SERVICE_URL", "http://localhost:5001"),
    "assessment": os.getenv("ASSESSMENT_SERVICE_URL", "http://localhost:5002"),
    "personalization": os.getenv("PERSONALIZATION_SERVICE_URL", "http://localhost:5003"),
    "summarization": os.getenv("SUMMARIZATION_SERVICE_URL", "http://localhost:5004"),
    "multimedia": os.getenv("MULTIMEDIA_SERVICE_URL", "http://localhost:5005"),
    "translation": os.getenv("TRANSLATION_SERVICE_URL", "http://localhost:5006"),
}

DEFAULT_TIMEOUT = int(os.getenv("GATEWAY_TIMEOUT_SECONDS", "180"))

def _forward_json(service_key: str, endpoint: str):
    if service_key not in SERVICE_URLS:
        return jsonify({"error": f"Unknown service '{service_key}'"}), 400
    url = f"{SERVICE_URLS[service_key].rstrip('/')}/{endpoint.lstrip('/')}"
    try:
        r = requests.post(url, json=(request.get_json(silent=True) or {}), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        # Return JSON transparently
        return jsonify(r.json()), r.status_code
    except requests.exceptions.HTTPError as he:
        # Proxy backend error payload if present
        try:
            return jsonify(r.json()), r.status_code
        except Exception:
            return jsonify({"error": "backend_error", "details": str(he)}), r.status_code if r else 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "service_unavailable", "details": str(e)}), 503

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "service": "api-gateway"}, 200

# ---------- Content ----------
@app.route("/api/create-curriculum", methods=["POST"])
def create_curriculum():
    return _forward_json("content", "/create-curriculum")

@app.route("/api/create-curriculum-agent", methods=["POST"])
def create_curriculum_agent():
    return _forward_json("content", "/create-curriculum-agent")

# ---------- Assessment ----------
@app.route("/api/create-assessment", methods=["POST"])
def create_assessment():
    return _forward_json("assessment", "/create-assessment")

@app.route("/api/create-assessment-agent", methods=["POST"])
def create_assessment_agent():
    return _forward_json("assessment", "/create-assessment-agent")

# ---------- Personalization ----------
@app.route("/api/personalize-content", methods=["POST"])
def personalize_content():
    return _forward_json("personalization", "/personalize-content")

@app.route("/api/personalize-content-agent", methods=["POST"])
def personalize_content_agent():
    return _forward_json("personalization", "/personalize-content-agent")

# ---------- Summarization ----------
@app.route("/api/summarize-text", methods=["POST"])
def summarize_text():
    return _forward_json("summarization", "/summarize-text")

# ---------- Translation ----------
@app.route("/api/localize-text", methods=["POST"])
def localize_text():
    return _forward_json("translation", "/localize-text")

@app.route("/api/localize-text-agent", methods=["POST"])
def localize_text_agent():
    return _forward_json("translation", "/localize-text-agent")

# ---------- Multimedia ----------
@app.route("/api/generate-image", methods=["POST"])
def generate_image():
    return _forward_json("multimedia", "/generate-image")

# Stream media bytes via the gateway so frontend does not call internal service directly
@app.route("/api/media/<int:media_id>", methods=["GET"])
def media_proxy(media_id: int):
    base = SERVICE_URLS["multimedia"].rstrip("/")
    url = f"{base}/media/{media_id}"
    try:
        # Stream response to client; exclude hop-by-hop headers
        with requests.get(url, stream=True, timeout=60) as r:
            headers = {
                k: v for k, v in r.headers.items()
                if k.lower() not in ("content-encoding", "content-length", "transfer-encoding", "connection")
            }
            return Response(r.iter_content(chunk_size=64 * 1024), status=r.status_code, headers=headers)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "service_unavailable", "details": str(e)}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("API_GATEWAY_PORT", "5000")), debug=True)
