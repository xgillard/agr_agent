"""A customer support agent"""
from logging import Logger

from langchain.chat_models import init_chat_model
from langchain.tools import tool

from tools import (
    agatha_knowledge,
    free_search_in_analyses_of_records,
    genealogy_search_church_registers_prior_to_1796,
    genealogy_search_civil_state_registers,
    search_person_in_analyses_of_records,
)

from .common import agent

log = Logger(__name__)

_knowledge = agatha_knowledge()

@tool
def manually_activate_user_account(user_email: str) -> bool:
    """Manually activate a user's account.
    
    Returns:
        bool: True upon success, False otherwise.
    """
    print(f"Activation du compte de {user_email}")
    return True


available_tools = [ 
    _knowledge, 
    genealogy_search_church_registers_prior_to_1796,
    genealogy_search_civil_state_registers,
    free_search_in_analyses_of_records, 
    search_person_in_analyses_of_records,
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
    model = init_chat_model(
        'deepseek-r1:1.5b', 
        model_provider="ollama",
        temperature = 0.2,
    ),
    debug = True,
)

