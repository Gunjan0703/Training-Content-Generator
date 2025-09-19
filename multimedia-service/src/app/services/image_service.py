import base64
import os
import graphviz
from datetime import datetime
from typing import Optional, Tuple, Union
from .storage_service import save_media

class ImageService:
    def __init__(self):
        # Create static directory relative to the app directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.output_dir = os.path.join(base_dir, "app", "static", "images")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Image output directory: {self.output_dir}")

    def generate_image_bytes_with_bedrock(self, prompt: str) -> bytes:
        """
        Replace this stub with the actual Bedrock Titan Image Generator call.
        For now, return a 1x1 PNG pixel so the pipeline works end-to-end.
        """
        # 1x1 transparent PNG
        return base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=")

    def generate_flowchart(self, prompt: str) -> Optional[Tuple[str, bytes]]:
        """Generate a flowchart based on the provided prompt."""
        try:
            # Create a new directed graph
            dot = graphviz.Digraph(comment=prompt)
            dot.attr(rankdir='TB')
            dot.attr('node', shape='rectangle', style='rounded')
            
            # Parse the prompt to identify nodes and connections
            if "llm architecture" in prompt.lower():
                # LLM Architecture specific flowchart
                dot.node('UI', 'User Interface\n(React Frontend)')
                dot.node('API', 'API Gateway\n(FastAPI)')
                dot.node('Content', 'Content Service\n(LLM Generation)')
                dot.node('Multimedia', 'Multimedia Service\n(Image/Video)')
                dot.node('Personal', 'Personalization\n(User Adaptation)')
                dot.node('Summary', 'Summarization\n(Content Digest)')
                dot.node('Assess', 'Assessment\n(Evaluation)')
                dot.node('DB', 'Vector Database\n(PostgreSQL + pgvector)')
                
                dot.edge('UI', 'API')
                dot.edge('API', 'Content')
                dot.edge('API', 'Multimedia')
                dot.edge('API', 'Personal')
                dot.edge('API', 'Summary')
                dot.edge('API', 'Assess')
                dot.edge('Content', 'DB')
                dot.edge('Multimedia', 'DB')
                dot.edge('Personal', 'DB')
            else:
                # Generic flowchart with simple processing steps
                steps = [x.strip() for x in prompt.split(',')]
                prev_node = None
                
                for i, step in enumerate(steps):
                    node_id = f'node_{i}'
                    dot.node(node_id, step)
                    
                    if prev_node:
                        dot.edge(prev_node, node_id)
                    prev_node = node_id

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flowchart_{timestamp}"
            file_path = dot.render(
                filename=os.path.join(self.output_dir, filename),
                format='png',
                cleanup=True
            )
            
            # Read the generated file
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
            
            return os.path.basename(file_path), image_bytes

        except Exception as e:
            print(f"Error generating flow chart: {str(e)}")
            return None

    def generate_and_store_image(self, prompt: str, image_type: str = "general") -> Tuple[str, str]:
        """Generate and store an image based on the prompt and type."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if image_type == "flowchart":
                result = self.generate_flowchart(prompt)
                if result:
                    filename, image_bytes = result
                    # The file is already saved by graphviz
                    return filename + ".png", f"/static/images/{filename}.png"
            else:
                img_bytes = self.generate_image_bytes_with_bedrock(prompt)
                filename = f"image_{timestamp}.png"
                file_path = os.path.join(self.output_dir, filename)
                
                # Save the image bytes to file
                with open(file_path, 'wb') as f:
                    f.write(img_bytes)
                
                return filename, f"/static/images/{filename}"
                
                # Save the generated image bytes
                with open(file_path, 'wb') as f:
                    f.write(img_bytes)
                
                return filename, f"/static/images/{filename}"
                
                # Save to file system
                with open(file_path, 'wb') as f:
                    f.write(img_bytes)
                return filename, f"/static/images/{filename}"
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            raise

# Initialize the global image service
image_service = ImageService()
