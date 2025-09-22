import os
import uuid
import base64
import json
import logging
from typing import Optional, Tuple, Literal
import boto3
import re
import asyncio
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultimediaStudioService:
    def __init__(self):
        # Set up output directory
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "static", "images")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize AWS Bedrock client
        try:
            self.client = boto3.client("bedrock-runtime", region_name="us-east-1")
            logger.info("AWS Bedrock client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS Bedrock client: {str(e)}")
            self.client = None

        # Valid image sizes for Titan Image Generator
        self.valid_sizes = {(1024, 1024), (1024, 576), (576, 1024), (1280, 720), (1920, 1080)}

    def generate_output(
        self,
        prompt: str,
        output_type: Literal["image", "flowchart", "general"] = "image",
        width: int = 1024,
        height: int = 1024,
    ) -> Optional[Tuple[str, str]]:
        if not self.client:
            logger.error("Bedrock client not initialized")
            return None
        
        if output_type in ["image", "general"]:
            logger.info(f"Routing to standard image generation for prompt: '{prompt[:50]}...'")
            return self._generate_standard_image(prompt, width, height)
        elif output_type == "flowchart":
            logger.info(f"Routing to flowchart generation for prompt: '{prompt[:50]}...'")
            return asyncio.run(self._generate_flowchart_async(prompt))
        else:
            logger.error(f"Invalid output_type: {output_type}")
            return None

    def _get_valid_size(self, width: int, height: int) -> Tuple[int, int]:
        if (width, height) in self.valid_sizes:
            return width, height
        logger.warning(f"Invalid size ({width}, {height}). Defaulting to (1024, 1024).")
        return 1024, 1024

    def _generate_standard_image(
        self,
        prompt: str,
        width: int,
        height: int,
        cfg_scale: float = 8.0,
        seed: Optional[int] = None,
    ) -> Optional[Tuple[str, str]]:
        width, height = self._get_valid_size(width, height)
        image_config = {
            "numberOfImages": 1,
            "width": width,
            "height": height,
            "cfgScale": cfg_scale
        }
        if seed is not None and seed >= 0:
            image_config["seed"] = seed
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": prompt},
            "imageGenerationConfig": image_config
        }
        try:
            logger.info(f"Sending request to Titan Image Generator...")
            response = self.client.invoke_model(
                modelId="amazon.titan-image-generator-v1",
                body=json.dumps(request_body),
            )
            response_body = json.loads(response.get("body").read())
            base64_image_data = response_body.get("images")[0]
            image_data = base64.b64decode(base64_image_data)
            return self._save_image(image_data, "png")
        except Exception as e:
            logger.error(f"Titan image generation error: {str(e)}")
            return None

    def _generate_mermaid_code(self, prompt: str, model_id: str) -> Optional[str]:
        """Generates Mermaid code using a specified model."""
        try:
            logger.info(f"Invoking {model_id} to generate Mermaid code...")
            system_prompt = "You are a helpful assistant that only generates Mermaid code for flowcharts. Do not include any explanations or surrounding text. Your output must ONLY be the code itself inside a ```mermaid ... ``` block."
            claude_request = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Generate a flowchart for the following topic: {prompt}"
                    }
                ]
            }
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(claude_request)
            )
            response_body = json.loads(response.get('body').read())
            mermaid_content = response_body['content'][0]['text']
            
            mermaid_code_match = re.search(r'```mermaid\n(.*?)```', mermaid_content, re.DOTALL)
            if not mermaid_code_match:
                logger.error(f"Could not parse Mermaid code from {model_id}'s response.")
                return None
            
            mermaid_code = mermaid_code_match.group(1).strip()
            logger.info(f"Successfully generated Mermaid code with {model_id}:\n{mermaid_code}")
            return mermaid_code

        except Exception as e:
            logger.error(f"Mermaid code generation error with {model_id}: {str(e)}")
            return None

    async def _render_mermaid_to_svg(self, mermaid_code: str) -> Optional[bytes]:
        """Renders Mermaid code to SVG bytes using a headless browser."""
        browser = None
        try:
            browser = await launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            page = await browser.newPage()
            
            # HTML template for Mermaid rendering
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
              <style>
                body {{ background-color: white; }}
              </style>
            </head>
            <body>
              <div class="mermaid">
                {mermaid_code}
              </div>
              <script>
                // Initialize Mermaid
                mermaid.init();
              </script>
            </body>
            </html>
            """
            
            await page.setContent(html_content, {'waitUntil': 'networkidle0'})
            await page.waitForSelector('.mermaid svg', {'timeout': 10000})

            svg_element = await page.querySelector('.mermaid svg')
            if not svg_element:
                raise Exception("Could not find the SVG element after rendering.")

            svg_content = await page.evaluate('(element) => element.outerHTML', svg_element)
            
            return svg_content.encode('utf-8')
        except TimeoutError:
            logger.error("Timeout waiting for Mermaid SVG element.")
            return None
        except Exception as e:
            logger.error(f"Failed to render Mermaid code to SVG: {e}")
            return None
        finally:
            if browser:
                await browser.close()

    async def _generate_flowchart_async(self, prompt: str) -> Optional[Tuple[str, str]]:
        """
        Generates a flowchart, attempting to use Claude 3.5 Sonnet first
        and falling back to Claude 3 Haiku if rendering fails.
        """
        # Attempt with Claude 3.5 Sonnet first
        mermaid_code = self._generate_mermaid_code(
            prompt, "anthropic.claude-3-5-sonnet-20240620-v1:0"
        )
        if mermaid_code:
            image_data = await self._render_mermaid_to_svg(mermaid_code)
            if image_data:
                return self._save_image(image_data, "svg")
            else:
                logger.warning("Rendering failed for Sonnet's code.")

        # Fallback to Claude 3 Haiku if Sonnet fails
        logger.info("Sonnet's output failed to render. Falling back to Claude 3 Haiku...")
        mermaid_code = self._generate_mermaid_code(
            prompt, "anthropic.claude-3-haiku-20240307-v1:0"
        )
        if mermaid_code:
            image_data = await self._render_mermaid_to_svg(mermaid_code)
            if image_data:
                return self._save_image(image_data, "svg")
            else:
                logger.error("Haiku's output also failed to render.")

        return None

    def _save_image(self, image_data: bytes, ext: str) -> Tuple[str, str]:
        """Saves image data to a file and returns the filename and URL."""
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_data)
        logger.info(f"Image saved at {filepath}")
        image_url = f"/static/images/{filename}"
        return filename, image_url


# Initialize global instance
multimedia_service = MultimediaStudioService()