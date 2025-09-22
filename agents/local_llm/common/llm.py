"""Usual llm config to use. 

This could be refined based on the task, but apparently, 
only a large-ish model will do.
"""

from langchain.chat_models import init_chat_model

LLM = init_chat_model(
    model = "gemini-2.5-flash-lite",
    model_provider = "google-genai",
    temperature=0.0,
)
