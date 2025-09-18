import json
import os
import time
from .services.image_service import generate_and_store_image
from .services.analysis_service import summarize_transcript

# Placeholder queue; replace with SQS/RabbitMQ client in production
QUEUE_FILE = os.getenv("MM_QUEUE_FILE", "/tmp/mm_jobs.jsonl")

def poll_jobs():
    while True:
        try:
            with open(QUEUE_FILE, "r+") as f:
                lines = f.readlines()
                f.seek(0); f.truncate()
            for line in lines:
                job = json.loads(line)
                handle_job(job)
        except FileNotFoundError:
            pass
        time.sleep(2)

def handle_job(job):
    kind = job.get("kind")
    if kind == "image":
        generate_and_store_image(job["prompt"])
    elif kind == "summarize":
        summarize_transcript(job["text"])

if __name__ == "__main__":
    poll_jobs()
