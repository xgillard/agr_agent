"""A customer support agent"""
import os

from logging import Logger
from typing import NamedTuple, Annotated

from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import BaseTool, render_text_description

from .common import agent
from tools import (
    agatha_knowledge,
    genealogy_search_church_registers_prior_to_1796,
    genealogy_search_civil_state_registers,
)

from functools import partial

log = Logger(__name__)

_knowledge = agatha_knowledge()

@tool
def manually_activate_user_account(user_email: str) -> bool:
    """Manually activate a user's account.
    
    Returns True upon success, False otherwise.
    """
    print(f"Activation du compte de {user_email}")
    return True


available_tools = [ 
    _knowledge, 
    genealogy_search_church_registers_prior_to_1796,
    genealogy_search_civil_state_registers, 
    manually_activate_user_account,
]

customer_support = agent(
    name   = "customer_support",
    role   = "Senior Customer Support at the Belgian State Archive",
    goal   = "Give factually correct answers to user emails",
    backstory = """
        You have been collaborating with the IT during the launch
        of AGATHA, the new gateway to search the Belgian State Archives.""",
    tools = available_tools,
    # === QWEN3 ==============
    #model = init_chat_model(
    #    'qwen3:8b', 
    #    model_provider="ollama",
    #    temperature = 0.01,
    #),
    #model = init_chat_model(
    #    'qwen3:14b', 
    #    model_provider="ollama",
    #    temperature = 0.01,
    #),
    #model = init_chat_model(
    #    'qwen3:30b', 
    #    model_provider="ollama",
    #    temperature = 0.01,
    #),
    # === LLAMA3 ==============
    #model = init_chat_model(
    #    'llama3.1:8b', 
    #    model_provider="ollama",
    #    temperature = 0.01,
    #),
    #model = init_chat_model(
    #    'llama3.2:latest', 
    #    model_provider="ollama",
    #    temperature = 0.01,
    #    
    #),
    # === MISTRAL =============
    #model = init_chat_model(
    #    'mistral-nemo', 
    #    model_provider="ollama",
    #    temperature = 0.01,
    #),
    # === GEMINI ==============
    model = init_chat_model(
        'gemini-2.5-flash', 
        model_provider="google_genai",
        temperature = 0.2,
    ),
    #model = init_chat_model(
    #    'gemini-2.5-pro', 
    #    model_provider="google_genai",
    #    temperature = 0.2,
    #),
    debug = True,
)

