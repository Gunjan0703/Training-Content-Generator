import os
from langchain.chains import RetrievalQA
from langchain_aws import ChatBedrockConverse
from .vector_store import get_store

def _llm(temperature=0.5, max_tokens=2048):
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
        model_kwargs={"temperature": temperature, "max_tokens": max_tokens}
    )

def summarize_user_weaknesses(user_id: str) -> str:
    """
    Retrieves and summarizes a user's weak areas from the vector store.
    """
    store = get_store()
    retriever = store.as_retriever(search_kwargs={"k": 4, "filter": {"user_id": user_id}})
    qa = RetrievalQA.from_chain_type(llm=_llm(temperature=0.3, max_tokens=1024), chain_type="stuff", retriever=retriever)
    return qa.run("Summarize this user's weak areas in one concise paragraph.")

def generate_adaptive_content(topic: str, user_id: str, user_role: str) -> dict:
    """
    Generates personalized training content that focuses on the user's weak areas.
    """
    try:
        weaknesses = summarize_user_weaknesses(user_id)
    except Exception:
        # If vector store not configured or retrieval fails, proceed without special context
        weaknesses = ""

    prompt = (
        f"You are a corporate training content creator.\n\n"
        f"Create a training module on the topic: '{topic}'.\n"
        f"Audience role: '{user_role}'.\n"
        f"{'Focus on remediating these weak areas: ' + weaknesses if weaknesses else 'No prior weaknesses available; cover core and advanced concepts succinctly.'}\n\n"
        f"Structure: introduction, 3-5 learning objectives, 2-4 sections with examples/exercises, and a summary.\n"
        f"Tone: clear, practical, and role-relevant."
    )

    content = _llm(temperature=0.6, max_tokens=2048).invoke(prompt).content
    return {
        "personalized_content": content,
        "weakness_context_used": bool(weaknesses)
    }
