import base64
from .storage_db import save_media

def generate_image_bytes_with_bedrock(prompt: str) -> bytes:
    """
    Replace this stub with the actual Bedrock Titan Image Generator call.
    For now, return a 1x1 PNG pixel so the pipeline works end-to-end.
    """
    # 1x1 transparent PNG
    return base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=")

def generate_and_store_image(prompt: str) -> int:
    img_bytes = generate_image_bytes_with_bedrock(prompt)
    media_id = save_media(filename="generated.png", mimetype="image/png", data=img_bytes)
    return media_id
