import os
import uuid
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import base64
import io
 
try:
    import boto3
    import json
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    print("AWS SDK not available. Install with: pip install boto3")
 
class EnhancedImageService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.output_dir = os.path.join(base_dir, "static", "images")
        os.makedirs(self.output_dir, exist_ok=True)
        try:
            self.font = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            self.font = ImageFont.load_default()
        self.bedrock_runtime = None
        if AWS_AVAILABLE:
            self._initialize_bedrock_client()
 
    def _initialize_bedrock_client(self):
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            if not credentials:
                print("AWS credentials not found. Please configure AWS:")
                print("export AWS_ACCESS_KEY_ID=your_key")
                print("export AWS_SECRET_ACCESS_KEY=your_secret")
                print("export AWS_REGION=us-east-1")
                return
            region = os.environ.get('AWS_REGION', 'us-east-1')
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name=region
            )
        except Exception as e:
            print(f"Error initializing Bedrock client: {e}")
            self.bedrock_runtime = None
 
    def _save_image(self, img: Image.Image, prefix: str) -> Tuple[str, str]:
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.png"
        image_path = os.path.join(self.output_dir, filename)
        img.save(image_path)
        return filename, f"/static/images/{filename}"
 
    def _create_titan_prompt(self, prompt: str, image_type: str) -> str:
        """Create a concise prompt for Titan that stays within character limits."""
        base_style = "Style: professional, clean, minimalist."
       
        if image_type == "flowchart":
            if len(prompt.split()) <= 3:
                return f"Flowchart diagram: process of {prompt}. Clear boxes, arrows. {base_style}"
            return f"Flowchart diagram showing: {prompt}. {base_style}"
        else:
            if len(prompt.split()) <= 3:
                return f"Professional visualization of {prompt}. {base_style}"
            return f"Professional image showing: {prompt}. {base_style}"
 
    def generate_image(self, prompt: str, image_type: str = "general") -> Optional[Tuple[str, str]]:
        """Generate an image using AWS Bedrock Titan Image Generator v2."""
        if self.bedrock_runtime:
            try:
                titan_prompt = self._create_titan_prompt(prompt, image_type)
               
                payload = {
                    "taskType": "TEXT_IMAGE",
                    "textToImageParams": {
                        "text": titan_prompt[:512],
                        "negativeText": "blurry, low quality, distorted, text artifacts"
                    },
                    "imageGenerationConfig": {
                        "numberOfImages": 1,
                        "quality": "premium",
                        "height": 1024,
                        "width": 1024,
                        "cfgScale": 8.5,
                        "seed": 42
                    }
                }
               
                print(f"Generating with Titan: {titan_prompt}")
                response = self.bedrock_runtime.invoke_model(
                    body=json.dumps(payload),
                    modelId='amazon.titan-image-generator-v2:0',
                    contentType='application/json',
                    accept='application/json'
                )
               
                response_body = json.loads(response['body'].read())
                if 'images' in response_body and response_body['images']:
                    base64_data = response_body['images'][0]
                    image_bytes = base64.b64decode(base64_data)
                    image_stream = io.BytesIO(image_bytes)
                    img = Image.open(image_stream)
                    prefix = "bedrock_flowchart" if image_type == "flowchart" else "bedrock_generated"
                    return self._save_image(img, prefix)
            except Exception as e:
                print(f"Bedrock generation failed: {e}")
 
        # Fallback to basic PIL diagrams
        try:
            img = Image.new("RGB", (1200, 800), color="#f8f9fa")
            draw = ImageDraw.Draw(img)
           
            title_text = f"{image_type.upper()}: {prompt[:50]}{'...' if len(prompt) > 50 else ''}"
            draw.rectangle([0, 0, 1200, 80], fill="#2563eb")
            title_bbox = draw.textbbox((0, 0), title_text, font=self.font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (1200 - title_width) // 2
            draw.text((title_x, 25), title_text, fill="white", font=self.font)
 
            if image_type == "flowchart":
                steps = prompt.split(",") if "," in prompt else ["Start", "Process", "Decision", "End"]
                y_pos = 150
                prev_x, prev_y = None, None
               
                for i, step in enumerate(steps):
                    text = step.strip()
                    is_decision = "?" in text or "decide" in text.lower()
                    x1, y1 = 300, y_pos
                    x2, y2 = 500, y_pos + 70
                   
                    if is_decision:
                        points = [(x1 + 100, y1), (x2, y1 + 35), (x1 + 100, y2), (x1, y1 + 35)]
                        draw.polygon(points, fill="#fef3c7", outline="#f59e0b", width=2)
                    else:
                        draw.rectangle([x1, y1, x2, y2], fill="#eff6ff", outline="#3b82f6", width=2)
                   
                    text_bbox = draw.textbbox((0, 0), text, font=self.font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_x = x1 + (x2 - x1 - text_width) // 2
                    text_y = y1 + 20
                    draw.text((text_x, text_y), text, fill="#1f2937", font=self.font)
                   
                    if prev_x is not None:
                        draw.line([prev_x + 100, prev_y + 70, x1 + 100, y1], fill="#6b7280", width=2)
                        draw.polygon([x1 + 95, y1, x1 + 105, y1, x1 + 100, y1 + 5], fill="#6b7280")
                   
                    prev_x, prev_y = x1, y1
                    y_pos += 120
            else:
                draw.ellipse([400, 300, 800, 400], fill="#fef3c7", outline="#f59e0b", width=3)
                text_bbox = draw.textbbox((0, 0), prompt, font=self.font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = 600 - text_width // 2
                draw.text((text_x, 335), prompt, fill="#92400e", font=self.font)
 
            footer_text = "Generated by Enhanced Image Service"
            footer_bbox = draw.textbbox((0, 0), footer_text, font=self.font)
            footer_width = footer_bbox[2] - footer_bbox[0]
            footer_x = 1200 - footer_width - 20
            draw.text((footer_x, 760), footer_text, fill="#64748b", font=self.font)
 
            prefix = "fallback_flowchart" if image_type == "flowchart" else "fallback_general"
            return self._save_image(img, prefix)
        except Exception as e:
            print(f"Fallback generation failed: {e}")
            return None
 
# Singleton instance
image_service = EnhancedImageService()
 
# Convenience function for testing
def test_image_service():
    """Test the image service with diagnosis."""
    image_service.diagnose_setup()
 
if __name__ == "__main__":
    test_image_service()
 