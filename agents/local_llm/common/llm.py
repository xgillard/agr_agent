"""Usual llm config to use. 

This could be refined based on the task, but apparently, 
only a large-ish model will do.
"""
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

LLM = init_chat_model(
    model          = os.environ["LLM_NAME"],
    model_provider = os.environ["LLM_PROVIDER"],
    temperature    = float(os.environ["LLM_TEMPERATURE"]),
    #reasoning      = os.environ.get("LLM_REASONING") in ["true", "True", "1"]
)
