"""Usual llm config to use. 

This could be refined based on the task, but apparently, 
only a large-ish model will do.
"""

from langchain.chat_models import init_chat_model

LLM = init_chat_model(
    model = "mistral-small-2506",
    model_provider = "mistralai",
    temperature=0.0,
)
