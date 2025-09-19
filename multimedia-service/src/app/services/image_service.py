import os
import uuid
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

class EnhancedImageService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.output_dir = os.path.join(base_dir, "app", "static", "images")
        os.makedirs(self.output_dir, exist_ok=True)

    def _save_image(self, img: Image.Image, prefix: str) -> Tuple[str, str]:
        """Save image to static/images and return (filename, path)."""
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.png"
        image_path = os.path.join(self.output_dir, filename)
        img.save(image_path)
        return filename, f"/static/images/{filename}"

    def generate_image_with_clear_text(self, prompt: str, method: str = "auto") -> Optional[Tuple[str, str]]:
        """Generate a simple placeholder image with text drawn on it."""
        try:
            img = Image.new("RGB", (512, 512), color="white")
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.load_default()
            except Exception:
                font = None

            text = f"Generated: {prompt}"
            draw.text((10, 10), text, fill="black", font=font)

            return self._save_image(img, "generated")
        except Exception:
            return None

    def generate_image(self, prompt: str, image_type: str = "general") -> Optional[Tuple[str, str]]:
        """Wrapper to handle different image types."""
        if image_type == "flowchart":
            return self.generate_image_with_clear_text(f"Flowchart: {prompt}")
        return self.generate_image_with_clear_text(prompt)

# ✅ singleton instance
image_service = EnhancedImageService()
