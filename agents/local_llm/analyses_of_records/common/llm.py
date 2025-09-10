"""Usual llm config to use. 

This could be refined based on the task, but apparently, only a large-ish model will do.
"""

from langchain.chat_models import init_chat_model

LLM = init_chat_model(
    model = "mistral-small:24b",
    model_provider = "ollama",
)
