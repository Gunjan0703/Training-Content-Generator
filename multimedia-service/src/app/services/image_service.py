import os
import uuid
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import requests

# Optional AWS imports - will work even if AWS isn't configured
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
        self.font = None
        try:
            self.font = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            self.font = ImageFont.load_default()
            
        # Initialize AWS Bedrock client
        self.bedrock_runtime = None
        self.bedrock_client = None
        if AWS_AVAILABLE:
            self._initialize_bedrock_client()

    def _initialize_bedrock_client(self):
        """Initialize the Amazon Bedrock runtime client with comprehensive error handling."""
        try:
            # Check AWS credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if not credentials:
                print("❌ AWS credentials not found. Please run 'aws configure' or set environment variables:")
                print("   export AWS_ACCESS_KEY_ID=your_key")
                print("   export AWS_SECRET_ACCESS_KEY=your_secret") 
                print("   export AWS_REGION=us-east-1")
                return
                
            # Get region
            region = os.environ.get('AWS_REGION', 'us-east-1')
            
            # Initialize both clients - runtime for generation, regular for model listing
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name=region
            )
            
            self.bedrock_client = boto3.client(
                service_name='bedrock',
                region_name=region
            )
            
            print(f"✅ AWS Bedrock clients initialized in region: {region}")
            
            # Test the connection immediately
            self._test_bedrock_access()
            
        except Exception as e:
            print(f"❌ Error initializing Bedrock client: {e}")
            self.bedrock_runtime = None
            self.bedrock_client = None

    def _test_bedrock_access(self):
        """Test Bedrock model access with detailed feedback."""
        if not self.bedrock_client:
            return False
            
        try:
            # Check available models using the regular bedrock client
            response = self.bedrock_client.list_foundation_models()
            models = [model['modelId'] for model in response.get('modelSummaries', [])]
            
            # Check for Titan image models
            titan_image_models = [m for m in models if 'titan-image' in m]
            
            if titan_image_models:
                print(f"✅ Available Titan Image models: {titan_image_models}")
                return True
            else:
                print("❌ No Titan Image models found!")
                print("🔧 Fix: Go to AWS Bedrock Console → Model Access → Request access to Titan Image Generator")
                print("   URL: https://console.aws.amazon.com/bedrock/home#/modelaccess")
                return False
                
        except Exception as e:
            print(f"❌ Bedrock access test failed: {e}")
            if "AccessDeniedException" in str(e):
                print("🔧 Fix: Request model access in AWS Bedrock console")
            elif "UnauthorizedOperation" in str(e):
                print("🔧 Fix: Check your AWS permissions for Bedrock")
            return False

    def _save_image(self, img: Image.Image, prefix: str) -> Tuple[str, str]:
        """Save image to static/images and return (filename, path)."""
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.png"
        image_path = os.path.join(self.output_dir, filename)
        img.save(image_path)
        return filename, f"/static/images/{filename}"

    def generate_professional_diagram(self, prompt: str, image_type: str = "general") -> Optional[Tuple[str, str]]:
        """Generate a professional-looking diagram using PIL."""
        try:
            # Create a larger canvas
            img = Image.new("RGB", (1200, 800), color="#f8f9fa")
            draw = ImageDraw.Draw(img)
            
            # Colors
            primary_color = "#2563eb"
            secondary_color = "#64748b"
            accent_color = "#10b981"
            
            # Draw header
            header_font = self.font
            title = f"{image_type.upper()}: {prompt[:50]}{'...' if len(prompt) > 50 else ''}"
            
            # Header background
            draw.rectangle([0, 0, 1200, 80], fill=primary_color)
            
            # Title text
            title_bbox = draw.textbbox((0, 0), title, font=header_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (1200 - title_width) // 2
            draw.text((title_x, 25), title, fill="white", font=header_font)
            
            # Draw content area based on type
            if image_type == "flowchart":
                self._draw_flowchart_elements(draw, prompt)
            elif image_type == "architecture":
                self._draw_architecture_elements(draw, prompt)
            else:
                self._draw_general_diagram(draw, prompt)
                
            # Add footer
            footer_text = "Generated by Enhanced Image Service"
            footer_bbox = draw.textbbox((0, 0), footer_text, font=self.font)
            footer_width = footer_bbox[2] - footer_bbox[0]
            footer_x = 1200 - footer_width - 20
            draw.text((footer_x, 760), footer_text, fill=secondary_color, font=self.font)
            
            return self._save_image(img, "professional_diagram")
            
        except Exception as e:
            print(f"❌ Error generating professional diagram: {e}")
            return None

    def _draw_flowchart_elements(self, draw, prompt):
        """Draw flowchart-style elements."""
        # Box positions
        boxes = [
            (200, 150, 400, 220, "START"),
            (200, 280, 400, 350, "Process 1"),
            (200, 410, 400, 480, "Decision"),
            (200, 540, 400, 610, "END"),
            (600, 280, 800, 350, "Process 2"),
        ]
        
        # Draw boxes and text
        for x1, y1, x2, y2, text in boxes:
            # Box
            draw.rectangle([x1, y1, x2, y2], fill="#e2e8f0", outline="#475569", width=2)
            # Text
            text_bbox = draw.textbbox((0, 0), text, font=self.font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = x1 + (x2 - x1 - text_width) // 2
            text_y = y1 + (y2 - y1 - text_height) // 2
            draw.text((text_x, text_y), text, fill="#1e293b", font=self.font)
        
        # Draw arrows
        arrows = [
            (300, 220, 300, 280),  # START to Process 1
            (300, 350, 300, 410),  # Process 1 to Decision  
            (300, 480, 300, 540),  # Decision to END
            (400, 315, 600, 315),  # Decision to Process 2
        ]
        
        for x1, y1, x2, y2 in arrows:
            draw.line([x1, y1, x2, y2], fill="#475569", width=3)
            # Simple arrowhead
            if x1 == x2:  # vertical arrow
                draw.polygon([x2-5, y2-10, x2+5, y2-10, x2, y2], fill="#475569")
            else:  # horizontal arrow
                draw.polygon([x2-10, y2-5, x2-10, y2+5, x2, y2], fill="#475569")

    def _draw_architecture_elements(self, draw, prompt):
        """Draw architecture diagram elements."""
        # Component boxes
        components = [
            (100, 150, 300, 250, "Frontend\n(React)"),
            (400, 150, 600, 250, "API Gateway"),
            (700, 150, 900, 250, "Backend\n(Node.js)"),
            (1000, 150, 1100, 250, "Database"),
            (400, 350, 600, 450, "Auth Service"),
            (700, 350, 900, 450, "File Storage"),
        ]
        
        for x1, y1, x2, y2, text in components:
            # Component box
            draw.rectangle([x1, y1, x2, y2], fill="#dbeafe", outline="#3b82f6", width=2)
            # Text
            lines = text.split('\n')
            line_height = 25
            total_height = len(lines) * line_height
            start_y = y1 + (y2 - y1 - total_height) // 2
            
            for i, line in enumerate(lines):
                text_bbox = draw.textbbox((0, 0), line, font=self.font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x1 + (x2 - x1 - text_width) // 2
                text_y = start_y + i * line_height
                draw.text((text_x, text_y), line, fill="#1e40af", font=self.font)
        
        # Connection lines
        connections = [
            (300, 200, 400, 200),  # Frontend to API
            (600, 200, 700, 200),  # API to Backend
            (900, 200, 1000, 200), # Backend to DB
            (500, 250, 500, 350),  # API to Auth
            (800, 250, 800, 350),  # Backend to Storage
        ]
        
        for x1, y1, x2, y2 in connections:
            draw.line([x1, y1, x2, y2], fill="#6b7280", width=2)

    def _draw_general_diagram(self, draw, prompt):
        """Draw a general diagram with boxes and connections."""
        # Central concept
        draw.ellipse([500, 300, 700, 400], fill="#fef3c7", outline="#f59e0b", width=3)
        
        # Central text
        central_text = "Main Concept"
        text_bbox = draw.textbbox((0, 0), central_text, font=self.font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = 600 - text_width // 2
        text_y = 350 - text_height // 2
        draw.text((text_x, text_y), central_text, fill="#92400e", font=self.font)
        
        # Surrounding elements
        satellites = [
            (200, 200, 350, 250, "Element 1"),
            (850, 200, 1000, 250, "Element 2"),
            (200, 500, 350, 550, "Element 3"),
            (850, 500, 1000, 550, "Element 4"),
        ]
        
        for x1, y1, x2, y2, text in satellites:
            draw.rectangle([x1, y1, x2, y2], fill="#dcfce7", outline="#16a34a", width=2)
            text_bbox = draw.textbbox((0, 0), text, font=self.font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = x1 + (x2 - x1 - text_width) // 2
            text_y = y1 + (y2 - y1 - text_height) // 2
            draw.text((text_x, text_y), text, fill="#15803d", font=self.font)
            
            # Connection to center
            center_x, center_y = 600, 350
            element_center_x = x1 + (x2 - x1) // 2
            element_center_y = y1 + (y2 - y1) // 2
            draw.line([center_x, center_y, element_center_x, element_center_y], 
                     fill="#6b7280", width=2)

    def generate_image_from_api(self, prompt: str) -> Optional[Tuple[str, str]]:
        """Generates an image using AWS Bedrock Titan Image Generator."""
        if not self.bedrock_runtime:
            print("⚠️  Bedrock not available, using professional diagram instead")
            return None
            
        try:
            # Enhanced prompt
            enhanced_prompt = f"A professional, clean, high-quality image depicting: {prompt}. Well-composed, detailed, modern style."
            
            # Payload for Titan Image Generator
            payload = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": enhanced_prompt,
                    "negativeText": "blurry, low quality, distorted, poorly drawn, text artifacts"
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,
                    "quality": "premium",
                    "height": 1024,
                    "width": 1024,
                    "cfgScale": 7.5,
                    "seed": 42
                }
            }

            print(f"🚀 Generating image with Bedrock: {enhanced_prompt}")

            # Try different model IDs
            model_ids = [
                'amazon.titan-image-generator-v2:0',
                'amazon.titan-image-generator-v1:0'
            ]
            
            for model_id in model_ids:
                try:
                    response = self.bedrock_runtime.invoke_model(
                        body=json.dumps(payload),
                        modelId=model_id,
                        contentType='application/json',
                        accept='application/json'
                    )

                    response_body = json.loads(response['body'].read())
                    
                    if 'images' not in response_body or not response_body['images']:
                        continue
                        
                    base64_data = response_body['images'][0]
                    image_bytes = base64.b64decode(base64_data)
                    image_stream = io.BytesIO(image_bytes)
                    img = Image.open(image_stream)
                    
                    print(f"✅ Image generated successfully with model: {model_id}")
                    return self._save_image(img, "bedrock_generated")
                    
                except Exception as model_error:
                    print(f"❌ Model {model_id} failed: {model_error}")
                    continue
                    
            print("❌ All Bedrock models failed")
            return None

        except Exception as e:
            print(f"❌ Bedrock API error: {e}")
            return None

    def generate_image_with_clear_text(self, prompt: str) -> Optional[Tuple[str, str]]:
        """Generate a simple fallback image - only used as last resort."""
        try:
            img = Image.new("RGB", (600, 400), color="#fee2e2")
            draw = ImageDraw.Draw(img)

            # Warning message
            warning_text = "⚠️  API UNAVAILABLE"
            fallback_text = f"Fallback: {prompt}"
            
            # Draw warning
            warning_bbox = draw.textbbox((0, 0), warning_text, font=self.font)
            warning_width = warning_bbox[2] - warning_bbox[0]
            warning_x = (img.width - warning_width) // 2
            draw.text((warning_x, 150), warning_text, fill="#dc2626", font=self.font)
            
            # Draw fallback text
            fallback_bbox = draw.textbbox((0, 0), fallback_text, font=self.font)
            fallback_width = fallback_bbox[2] - fallback_bbox[0]
            fallback_x = (img.width - fallback_width) // 2
            draw.text((fallback_x, 200), fallback_text, fill="#991b1b", font=self.font)
            
            return self._save_image(img, "fallback")
        except Exception as e:
            print(f"❌ Even fallback failed: {e}")
            return None

    def generate_image(self, prompt: str, image_type: str = "general") -> Optional[Tuple[str, str]]:
        """Main image generation method with multiple fallback options."""
        print(f"🎨 Generating image: '{prompt}' (type: {image_type})")
        
        # Enhanced prompt based on type
        if image_type == "flowchart":
            enhanced_prompt = f"A professional flowchart diagram showing: {prompt}. Include clear boxes, arrows, decision diamonds, and labels."
        elif image_type == "architecture":
            enhanced_prompt = f"A clean system architecture diagram illustrating: {prompt}. Use standard symbols, clear connections, and proper labeling."
        else:
            enhanced_prompt = prompt
        
        # Try AWS Bedrock first
        if self.bedrock_runtime:
            print("🔄 Attempting Bedrock API generation...")
            result = self.generate_image_from_api(enhanced_prompt)
            if result:
                print("✅ Bedrock generation successful!")
                return result
            else:
                print("❌ Bedrock generation failed, trying professional diagram...")
        
        # Try professional diagram generation
        print("🔄 Generating professional diagram...")
        result = self.generate_professional_diagram(prompt, image_type)
        if result:
            print("✅ Professional diagram generated!")
            return result
        
        # Last resort fallback
        print("🔄 Using basic fallback...")
        result = self.generate_image_with_clear_text(f"{image_type.capitalize()}: {prompt}")
        if result:
            print("⚠️  Basic fallback used")
            return result
        
        print("❌ All generation methods failed!")
        return None

    def diagnose_setup(self):
        """Comprehensive diagnosis of the setup."""
        print("\n🔍 ENHANCED IMAGE SERVICE DIAGNOSIS")
        print("=" * 50)
        
        # Check directory
        print(f"📁 Output directory: {self.output_dir}")
        print(f"   Exists: {os.path.exists(self.output_dir)}")
        print(f"   Writable: {os.access(self.output_dir, os.W_OK)}")
        
        # Check PIL
        print(f"🖼️  PIL/Pillow: Available")
        print(f"   Font loaded: {self.font is not None}")
        
        # Check AWS
        if AWS_AVAILABLE:
            print(f"☁️  AWS SDK: Available")
            if self.bedrock_runtime:
                print(f"   Bedrock client: Initialized")
                # Test access
                try:
                    response = self.bedrock_client.list_foundation_models()
                    models = [m['modelId'] for m in response.get('modelSummaries', [])]
                    titan_models = [m for m in models if 'titan-image' in m]
                    print(f"   Available models: {len(models)} total")
                    print(f"   Titan image models: {titan_models}")
                    
                    if not titan_models:
                        print("   ❌ ACTION REQUIRED:")
                        print("      1. Go to: https://console.aws.amazon.com/bedrock/home#/modelaccess")
                        print("      2. Request access to 'Amazon Titan Image Generator G1'")
                        print("      3. Wait for approval (usually instant)")
                        
                except Exception as e:
                    print(f"   ❌ Bedrock access error: {e}")
            else:
                print(f"   Bedrock client: Failed to initialize")
        else:
            print(f"☁️  AWS SDK: Not available (install with: pip install boto3)")
        
        print("\n🧪 Running test generation...")
        result = self.generate_image("test diagram", "flowchart")
        if result:
            filename, path = result
            print(f"✅ Test successful: {filename}")
            print(f"   Saved to: {path}")
        else:
            print("❌ Test failed")

# Singleton instance
image_service = EnhancedImageService()

# Convenience function for testing
def test_image_service():
    """Test the image service with diagnosis."""
    image_service.diagnose_setup()

if __name__ == "__main__":
    test_image_service()