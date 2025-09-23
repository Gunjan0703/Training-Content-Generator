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
        """Draw flowchart-style elements - detects specific flowchart types."""
        # Check for specific flowchart types
        if any(keyword in prompt.lower() for keyword in ['user login', 'authentication', 'auth']):
            self._draw_login_flowchart(draw)
        elif any(keyword in prompt.lower() for keyword in ['deployment', 'ci/cd', 'pipeline']):
            self._draw_deployment_flowchart(draw)
        else:
            self._draw_generic_flowchart(draw, prompt)
    
    def _draw_login_flowchart(self, draw):
        """Draw a user login process flowchart."""
        # Flowchart elements with specific login process
        elements = [
            (200, 120, 400, 170, "START: User Login", "#f0f9ff", "#0ea5e9"),
            (200, 200, 400, 250, "Enter Credentials", "#eff6ff", "#3b82f6"),
            (200, 280, 400, 350, "Valid\nCredentials?", "#fef3c7", "#f59e0b"),  # Diamond shape
            (500, 280, 700, 330, "Authentication\nSuccess", "#f0fdf4", "#10b981"),
            (200, 400, 400, 450, "Show Error\nMessage", "#fef2f2", "#ef4444"),
            (500, 380, 700, 430, "Redirect to\nDashboard", "#f0fdf4", "#10b981"),
        ]
        
        # Draw elements
        for x1, y1, x2, y2, text, bg_color, border_color in elements:
            if "?" in text:  # Decision diamond
                # Draw diamond shape
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                width, height = x2 - x1, y2 - y1
                diamond_points = [
                    (center_x, y1),  # top
                    (x2, center_y),  # right
                    (center_x, y2),  # bottom
                    (x1, center_y),  # left
                ]
                draw.polygon(diamond_points, fill=bg_color, outline=border_color, width=2)
            else:
                draw.rectangle([x1, y1, x2, y2], fill=bg_color, outline=border_color, width=2)
            
            # Add text
            lines = text.split('\n')
            line_height = 20
            total_height = len(lines) * line_height
            start_y = y1 + (y2 - y1 - total_height) // 2
            
            for i, line in enumerate(lines):
                text_bbox = draw.textbbox((0, 0), line, font=self.font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x1 + (x2 - x1 - text_width) // 2
                text_y = start_y + i * line_height
                draw.text((text_x, text_y), line, fill="#1f2937", font=self.font)
        
        # Draw arrows with labels
        arrows = [
            (300, 170, 300, 200, ""),
            (300, 250, 300, 280, ""),
            (400, 315, 500, 305, "YES"),
            (300, 350, 300, 400, "NO"),
            (600, 330, 600, 380, ""),
        ]
        
        for x1, y1, x2, y2, label in arrows:
            draw.line([x1, y1, x2, y2], fill="#6b7280", width=2)
            # Arrowhead
            if x1 == x2:  # vertical
                draw.polygon([x2-5, y2-8, x2+5, y2-8, x2, y2], fill="#6b7280")
            else:  # horizontal
                draw.polygon([x2-8, y2-5, x2-8, y2+5, x2, y2], fill="#6b7280")
            
            # Label
            if label:
                label_x = (x1 + x2) // 2 + 10
                label_y = (y1 + y2) // 2 - 10
                draw.text((label_x, label_y), label, fill="#059669", font=self.font)
    
    def _draw_deployment_flowchart(self, draw):
        """Draw a CI/CD deployment flowchart."""
        elements = [
            (150, 120, 300, 170, "Code Commit", "#eff6ff", "#3b82f6"),
            (150, 200, 300, 250, "Run Tests", "#fef3c7", "#f59e0b"),
            (150, 280, 300, 330, "Build Image", "#f0fdf4", "#10b981"),
            (400, 200, 550, 250, "Deploy to\nStaging", "#fef2f2", "#ef4444"),
            (400, 300, 550, 350, "Integration\nTests", "#fef3c7", "#f59e0b"),
            (400, 400, 550, 450, "Deploy to\nProduction", "#f0fdf4", "#10b981"),
        ]
        
        for x1, y1, x2, y2, text, bg_color, border_color in elements:
            draw.rectangle([x1, y1, x2, y2], fill=bg_color, outline=border_color, width=2)
            lines = text.split('\n')
            line_height = 20
            total_height = len(lines) * line_height
            start_y = y1 + (y2 - y1 - total_height) // 2
            
            for i, line in enumerate(lines):
                text_bbox = draw.textbbox((0, 0), line, font=self.font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x1 + (x2 - x1 - text_width) // 2
                text_y = start_y + i * line_height
                draw.text((text_x, text_y), line, fill="#1f2937", font=self.font)
        
        # Arrows
        arrows = [
            (225, 170, 225, 200),
            (225, 250, 225, 280),
            (300, 225, 400, 225),
            (475, 250, 475, 300),
            (475, 350, 475, 400),
        ]
        
        for x1, y1, x2, y2 in arrows:
            draw.line([x1, y1, x2, y2], fill="#6b7280", width=2)
            if x1 == x2:  # vertical
                draw.polygon([x2-5, y2-8, x2+5, y2-8, x2, y2], fill="#6b7280")
            else:  # horizontal
                draw.polygon([x2-8, y2-5, x2-8, y2+5, x2, y2], fill="#6b7280")
    
    def _draw_generic_flowchart(self, draw, prompt):
        """Draw a generic flowchart."""
        # Generic flowchart boxes
        boxes = [
            (200, 150, 400, 220, "START", "#f0f9ff", "#0ea5e9"),
            (200, 280, 400, 350, "Process 1", "#eff6ff", "#3b82f6"),
            (200, 410, 400, 480, "Decision?", "#fef3c7", "#f59e0b"),
            (200, 540, 400, 610, "END", "#fef2f2", "#ef4444"),
            (600, 410, 800, 480, "Process 2", "#f0fdf4", "#10b981"),
        ]
        
        for x1, y1, x2, y2, text, bg_color, border_color in boxes:
            if "?" in text:  # Decision diamond
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                diamond_points = [
                    (center_x, y1), (x2, center_y), (center_x, y2), (x1, center_y)
                ]
                draw.polygon(diamond_points, fill=bg_color, outline=border_color, width=2)
            else:
                draw.rectangle([x1, y1, x2, y2], fill=bg_color, outline=border_color, width=2)
            
            text_bbox = draw.textbbox((0, 0), text, font=self.font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = x1 + (x2 - x1 - text_width) // 2
            text_y = y1 + (y2 - y1 - text_height) // 2
            draw.text((text_x, text_y), text, fill="#1f2937", font=self.font)
        
        # Arrows
        arrows = [
            (300, 220, 300, 280),
            (300, 350, 300, 410),
            (300, 480, 300, 540),
            (400, 445, 600, 445),
        ]
        
        for x1, y1, x2, y2 in arrows:
            draw.line([x1, y1, x2, y2], fill="#6b7280", width=2)
            if x1 == x2:  # vertical
                draw.polygon([x2-5, y2-8, x2+5, y2-8, x2, y2], fill="#6b7280")
            else:  # horizontal
                draw.polygon([x2-8, y2-5, x2-8, y2+5, x2, y2], fill="#6b7280")

    def _draw_architecture_elements(self, draw, prompt):
        """Draw architecture diagram elements - detects Kubernetes and creates specialized diagrams."""
        # Check if this is a Kubernetes diagram
        k8s_keywords = ['kubernetes', 'k8s', 'master', 'control plane', 'worker node', 'pod', 'kubelet', 'etcd']
        if any(keyword in prompt.lower() for keyword in k8s_keywords):
            self._draw_kubernetes_architecture(draw)
        else:
            self._draw_generic_architecture(draw, prompt)
    
    def _draw_kubernetes_architecture(self, draw):
        """Draw a detailed Kubernetes architecture diagram."""
        # Colors for different components
        control_plane_color = "#3b82f6"  # Blue
        worker_node_color = "#10b981"    # Green
        service_color = "#f59e0b"        # Orange
        ingress_color = "#8b5cf6"        # Purple
        pod_color = "#ef4444"            # Red
        
        # Draw Control Plane section
        draw.rectangle([50, 120, 580, 320], fill="#eff6ff", outline=control_plane_color, width=3)
        draw.text((60, 130), "CONTROL PLANE / MASTER", fill=control_plane_color, font=self.font)
        
        # Control Plane Components
        control_components = [
            (70, 160, 180, 200, "API Server", control_plane_color),
            (200, 160, 310, 200, "Controller\nManager", control_plane_color),
            (330, 160, 440, 200, "Scheduler", control_plane_color),
            (460, 160, 570, 200, "etcd", control_plane_color),
        ]
        
        for x1, y1, x2, y2, text, color in control_components:
            draw.rectangle([x1, y1, x2, y2], fill="white", outline=color, width=2)
            lines = text.split('\n')
            line_height = 20
            total_height = len(lines) * line_height
            start_y = y1 + (y2 - y1 - total_height) // 2
            
            for i, line in enumerate(lines):
                text_bbox = draw.textbbox((0, 0), line, font=self.font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x1 + (x2 - x1 - text_width) // 2
                text_y = start_y + i * line_height
                draw.text((text_x, text_y), line, fill=color, font=self.font)
        
        # Worker Nodes
        worker_nodes = [
            (650, 120, 1150, 320, "WORKER NODE 1"),
            (650, 350, 1150, 550, "WORKER NODE 2"),
        ]
        
        for wx1, wy1, wx2, wy2, node_title in worker_nodes:
            # Worker node container
            draw.rectangle([wx1, wy1, wx2, wy2], fill="#f0fdf4", outline=worker_node_color, width=3)
            draw.text((wx1+10, wy1+10), node_title, fill=worker_node_color, font=self.font)
            
            # Worker node components
            node_components = [
                (wx1+20, wy1+50, wx1+150, wy1+90, "Kubelet", worker_node_color),
                (wx1+170, wy1+50, wx1+300, wy1+90, "Kube-Proxy", worker_node_color),
                (wx1+20, wy1+110, wx1+120, wy1+180, "Pod\nApp A", pod_color),
                (wx1+140, wy1+110, wx1+240, wy1+180, "Pod\nApp B", pod_color),
                (wx1+260, wy1+110, wx1+360, wy1+180, "Pod\nApp C", pod_color),
            ]
            
            for cx1, cy1, cx2, cy2, text, color in node_components:
                draw.rectangle([cx1, cy1, cx2, cy2], fill="white", outline=color, width=2)
                lines = text.split('\n')
                line_height = 18
                total_height = len(lines) * line_height
                start_y = cy1 + (cy2 - cy1 - total_height) // 2
                
                for i, line in enumerate(lines):
                    text_bbox = draw.textbbox((0, 0), line, font=self.font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_x = cx1 + (cx2 - cx1 - text_width) // 2
                    text_y = start_y + i * line_height
                    draw.text((text_x, text_y), line, fill=color, font=self.font)
        
        # Service Layer
        draw.rectangle([50, 580, 580, 650], fill="#fef3c7", outline=service_color, width=2)
        draw.text((60, 590), "SERVICE LAYER", fill=service_color, font=self.font)
        draw.text((70, 615), "ClusterIP • NodePort • LoadBalancer Services", fill="#92400e", font=self.font)
        
        # Ingress Controller
        draw.rectangle([650, 580, 1150, 650], fill="#f3e8ff", outline=ingress_color, width=2)
        draw.text((660, 590), "INGRESS CONTROLLER", fill=ingress_color, font=self.font)
        draw.text((670, 615), "External Access • SSL Termination • Routing", fill="#7c2d12", font=self.font)
        
        # Connection arrows
        connections = [
            # Control plane to worker nodes
            (580, 220, 650, 220, "API calls"),
            (580, 280, 650, 400, "Pod scheduling"),
            # Services to pods
            (315, 580, 900, 350, "Service routing"),
            (315, 580, 900, 480, "Load balancing"),
            # Ingress to services
            (650, 615, 580, 615, "Traffic routing"),
        ]
        
        for x1, y1, x2, y2, label in connections:
            # Draw arrow line
            draw.line([x1, y1, x2, y2], fill="#6b7280", width=2)
            # Simple arrowhead
            if x2 > x1:  # Right arrow
                draw.polygon([x2-10, y2-5, x2-10, y2+5, x2, y2], fill="#6b7280")
            else:  # Left arrow
                draw.polygon([x2+10, y2-5, x2+10, y2+5, x2, y2], fill="#6b7280")
            
            # Label (optional, comment out if too cluttered)
            # mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2 - 10
            # draw.text((mid_x, mid_y), label, fill="#4b5563", font=self.font)
        
        # External traffic arrow
        draw.line([900, 550, 900, 580], fill=ingress_color, width=4)
        draw.polygon([895, 585, 905, 585, 900, 590], fill=ingress_color)
        draw.text((850, 555), "External Traffic", fill=ingress_color, font=self.font)
        
    def _draw_generic_architecture(self, draw, prompt):
        """Draw generic architecture diagram for non-Kubernetes systems."""
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