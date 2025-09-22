import os
import uuid
import base64
import json
import logging
from typing import Optional, Tuple, Literal
import boto3
import requests
import re
import time

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultimediaStudioService:
    def __init__(self):
        # Set up output directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.output_dir = os.path.join(base_dir, "app", "static", "images")
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

    # Main function to route traffic based on output type
    def generate_output(
        self,
        prompt: str,
        # Updated Literal to include 'general'
        output_type: Literal["image", "flowchart", "general"] = "image",
        width: int = 1024,
        height: int = 1024,
    ) -> Optional[Tuple[str, str]]:
        """
        Generates either a standard image or a flowchart image.
        """
        if not self.client:
            logger.error("Bedrock client not initialized")
            return None
        
        # Now, check for both "image" and "general" together
        if output_type in ["image", "general"]:
            logger.info(f"Routing to standard image generation for prompt: '{prompt[:50]}...'")
            return self._generate_standard_image(prompt, width, height)
        elif output_type == "flowchart":
            logger.info(f"Routing to flowchart generation for prompt: '{prompt[:50]}...'")
            return self._generate_flowchart_image_with_fallback(prompt)
        else:
            # This else block should now only be hit for unexpected values
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
        """
        Generates a standard image using Amazon Titan Image Generator.
        """
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

    def _render_and_save_flowchart(self, mermaid_code: str) -> Optional[Tuple[str, str]]:
        """Renders Mermaid code to SVG and saves it with retries."""
        logger.info("Rendering Mermaid code to SVG image...")
        encoded_mermaid = base64.b64encode(mermaid_code.encode("utf-8")).decode("utf-8")
        render_url = f"https://mermaid.ink/img/{encoded_mermaid}?theme=neutral"

        retries = 3
        for i in range(retries):
            try:
                image_response = requests.get(render_url)
                image_response.raise_for_status()
                return self._save_image(image_response.content, "svg")
            except requests.exceptions.HTTPError as err:
                if err.response.status_code >= 500 and i < retries - 1:
                    logger.warning(f"Attempt {i+1} failed with a 5xx error. Retrying in {2**(i+1)} seconds...")
                    time.sleep(2**(i+1))
                else:
                    raise
        return None

    def _generate_flowchart_image_with_fallback(self, prompt: str) -> Optional[Tuple[str, str]]:
        """
        Generates a flowchart, attempting to use Claude 3.5 Sonnet first
        and falling back to Claude 3 Haiku if rendering fails.
        """
        # Attempt with Claude 3.5 Sonnet first
        mermaid_code = self._generate_mermaid_code(
            prompt, "anthropic.claude-3-5-sonnet-20240620-v1:0"
        )
        if mermaid_code:
            try:
                result = self._render_and_save_flowchart(mermaid_code)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Rendering failed for Sonnet's code: {str(e)}")

        # Fallback to Claude 3 Haiku if Sonnet fails
        logger.info("Sonnet's output failed to render. Falling back to Claude 3 Haiku...")
        mermaid_code = self._generate_mermaid_code(
            prompt, "anthropic.claude-3-haiku-20240307-v1:0"
        )
        if mermaid_code:
            try:
                result = self._render_and_save_flowchart(mermaid_code)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Haiku's output also failed to render: {str(e)}")

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