"""Usual llm config to use. 

This could be refined based on the task, but apparently, 
only a large-ish model will do.
"""

#from langchain.chat_models import init_chat_model
#
#LLM = init_chat_model(
#    model = "qwen3:8b",
#    model_provider = "ollama",
#    temperature=0.0,
#    reasoning = True,
#)
from langchain_ollama import ChatOllama

LLM = ChatOllama(
    base_url="http://localhost:11434",
    model="deepseek-r1:8b",
    temperature=0.0,
    reasoning=True,
)