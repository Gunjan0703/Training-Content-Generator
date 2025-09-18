import os
from typing import List, Dict, Any, Optional
from langchain.chains import RetrievalQA
from langchain_aws import ChatBedrockConverse
from .vector_store_pg import get_store, save_user_weakness, find_similar_weaknesses  # pgvector-backed store

# -------------------------
# LLM initializer
# -------------------------
def _llm(temperature=0.5, max_tokens=2048):
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
        temperature=temperature,
        max_tokens=max_tokens
    )

# -------------------------
# Weakness Analysis
# -------------------------
def analyze_topic_weaknesses(topic: str, user_weaknesses: List[Dict[str, Any]]) -> str:
    """Analyze weaknesses relevant to the current topic."""
    print(f"[DEBUG] Analyzing weaknesses for topic: {topic}")
    print(f"[DEBUG] Number of weaknesses to analyze: {len(user_weaknesses)}")
    
    if not user_weaknesses:
        print("[DEBUG] No weaknesses provided for analysis")
        return ""
    
    try:
        # Create topic-focused analysis prompt
        weakness_texts = [w["weakness_text"] for w in user_weaknesses]
        print(f"[DEBUG] Weakness texts to analyze: {json.dumps(weakness_texts)}")
        
        prompt = (
            f"Topic: {topic}\n\n"
            f"User's learning gaps:\n{json.dumps(weakness_texts)}\n\n"
            "Analyze these gaps in the context of the topic. "
            "Identify which weaknesses are most relevant and how they might impact learning this topic. "
            "Format as a concise paragraph focusing on actionable insights. "
            "If any weakness is not relevant to the topic, exclude it from the analysis."
        )
        
        analysis = _llm(temperature=0.3).invoke(prompt).content
        print(f"[DEBUG] Generated weakness analysis: {analysis}")
        return analysis
        
    except Exception as e:
        print(f"[ERROR] Error in analyze_topic_weaknesses: {str(e)}")
        return ""

def find_relevant_weaknesses(topic: str, user_id: str) -> List[Dict[str, Any]]:
    """Find weaknesses relevant to the current topic using vector similarity."""
    try:
        # Get user's specific weaknesses first
        store = get_store()
        retriever = store.as_retriever(
            search_kwargs={
                "k": 3,
                "filter": {"metadata": {"user_id": user_id}},
                "fetch_k": 10  # Fetch more candidates for better matching
            }
        )
        
        # Search with the topic as query
        user_results = retriever.get_relevant_documents(topic)
        print(f"[DEBUG] Found {len(user_results)} user-specific weaknesses for user {user_id}")
        
        # Find similar weaknesses across all users
        topic_related = find_similar_weaknesses(topic, limit=3)
        print(f"[DEBUG] Found {len(topic_related)} topic-related weaknesses")
        
        # Combine and deduplicate results
        all_weaknesses = {}
        
        # Add topic-related weaknesses
        for w in topic_related:
            all_weaknesses[w["id"]] = w
        
        # Add user-specific weaknesses
        for doc in user_results:
            doc_id = doc.metadata.get("id")
            if doc_id and doc_id not in all_weaknesses:
                all_weaknesses[doc_id] = {
                    "id": doc_id,
                    "weakness_text": doc.page_content,
                    "user_id": doc.metadata.get("user_id", user_id),
                    "similarity": doc.metadata.get("similarity", 0.0)
                }
        
        results = list(all_weaknesses.values())
        print(f"[DEBUG] Combined {len(results)} unique relevant weaknesses")
        return results
        
    except Exception as e:
        print(f"[ERROR] Error in find_relevant_weaknesses: {str(e)}")
        return []

# -------------------------
# Generate personalized content
# -------------------------
def generate_adaptive_content(topic: str, user_id: str, user_role: str) -> dict:
    """
    Generate personalized training content using RAG for weakness analysis.
    """
    try:
        # Find relevant weaknesses using vector similarity
        relevant_weaknesses = find_relevant_weaknesses(topic, user_id)
        
        # Analyze weaknesses in context of the topic
        weakness_analysis = analyze_topic_weaknesses(topic, relevant_weaknesses)
        
        # Generate personalized content
        prompt = (
            f"You are a corporate training content creator specializing in personalized learning.\n\n"
            f"Create a training module on: '{topic}'\n"
            f"Audience role: '{user_role}'\n\n"
            f"Learner Context:\n{weakness_analysis if weakness_analysis else 'No prior learning gaps identified.'}\n\n"
            "Required Structure:\n"
            "1. Introduction (relevance to role)\n"
            "2. Learning Objectives (3-5 measurable goals)\n"
            "3. Prerequisite Review (if gaps identified)\n"
            "4. Main Content (2-3 sections with examples)\n"
            "5. Targeted Exercises (practice activities)\n"
            "6. Summary (key takeaways)\n\n"
            "Requirements:\n"
            "- Address identified knowledge gaps progressively\n"
            "- Include role-specific examples\n"
            "- Provide scaffolded learning activities\n"
            "- Clear, practical explanations\n"
        )

        content = _llm(temperature=0.6, max_tokens=2048).invoke(prompt).content

        return {
            "personalized_content": str(content),
            "weakness_context_used": bool(weakness_analysis),
            "weakness_analysis": weakness_analysis if weakness_analysis else None
        }
    except Exception as e:
        print(f"[Error] RAG retrieval failed: {e}")
        # Fallback to basic content generation
        prompt = (
            f"Create a training module on '{topic}' for role '{user_role}'.\n"
            "Include: introduction, learning objectives, main content with examples, "
            "exercises, and summary. Focus on core concepts and practical applications."
        )
        content = _llm(temperature=0.6, max_tokens=2048).invoke(prompt).content
        
        return {
            "personalized_content": str(content),
            "weakness_context_used": False
        }
