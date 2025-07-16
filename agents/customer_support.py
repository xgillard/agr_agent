"""A customer support agent"""
from logging import Logger
from langchain.tools import tool
from langchain.chat_models import init_chat_model

from .common import agent

log = Logger(__name__)

@tool
def search_help(question: str) -> str:
    """Search for help in the FAQ and user's manual."""
    log.info("question: %s", question)
    return "Ta mere en short !"


customer_support = agent(
    name  = "customer_support",
    role  = "Senior Customer Support",
    goal  = "Help people answer their questions",
    backstory = "You are a helpful assistant who gives factually correct answers based on what is in the FAQ and user manuals.",
    tools = [search_help],
    model = init_chat_model(
        'llama3.2', 
        model_provider="ollama",
        temperature = 0.1,
    ),
    debug = True,
)