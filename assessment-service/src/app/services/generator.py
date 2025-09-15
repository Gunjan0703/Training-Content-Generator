from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_aws import ChatBedrock
import os

def get_llm():
    """Initializes and returns the ChatBedrock LLM client."""
    return ChatBedrock(
        region_name=os.environ.get("AWS_REGION"),
        model_id="anthropic.claude-3-sonnet-20240229-v1:0", # A balanced model for this task
        model_kwargs={
            "temperature": 0.5,
            "max_tokens": 2048
        }
    )

def create_advanced_assessment(content: str, assessment_type: str) -> str:
    """
    Generates an assessment of a specified type based on the provided content.

    Args:
        content: The text content to base the assessment on.
        assessment_type: The type of assessment to generate ('multiple_choice', 'scenario', etc.).

    Returns:
        The generated assessment text.
    """
    llm = get_llm()

    # A dictionary mapping assessment types to specific, high-quality prompts
    templates = {
        "multiple_choice": """You are an expert quiz designer. Based on the content below, create a 5-question multiple-choice quiz.
- Each question must have 4 options (A, B, C, D).
- Only one option should be correct.
- After all the questions, provide a separate answer key.

Content:
---
{content}
---
""",
        "scenario": """You are an expert in instructional design. Based on the content below, create a realistic workplace scenario that tests a user's decision-making and practical application of the knowledge.
- The scenario should be detailed and plausible.
- After the scenario, ask a single, clear question about what the user should do next.
- Finally, provide an 'Ideal Answer' section that explains the best course of action with justifications based on the content.

Content:
---
{content}
---
""",
        "fill_in_the_blanks": """You are a meticulous editor. Based on the key concepts in the content below, create a 5-item fill-in-the-blanks quiz.
- Each item should be a complete sentence with a single blank space represented by '____'.
- The sentences should test important definitions or process steps.
- Provide a separate, clearly labeled answer key with the words that fill the blanks.

Content:
---
{content}
---
"""
    }

    # Select the appropriate template, defaulting to multiple_choice if the type is invalid
    template = templates.get(assessment_type, templates["multiple_choice"])

    prompt = PromptTemplate(input_variables=["content"], template=template)
    
    # Create and run the LangChain chain
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.invoke({"content": content})
    
    return response['text']
