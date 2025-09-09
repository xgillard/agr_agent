"""A customer support agent"""
from logging import Logger

from langchain.chat_models import init_chat_model
from langchain.tools import tool

from tools import (
    agatha_knowledge,
    genealogy_search_church_registers_prior_to_1796,
    genealogy_search_civil_state_registers,
    tool_free_search_in_analyses_of_records,
    tool_search_person_in_analyses_of_records,
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
    tool_search_person_in_analyses_of_records,
    tool_free_search_in_analyses_of_records, 
    manually_activate_user_account,
]

customer_support = agent(
    name   = "customer_support",
    role   = "Senior Customer Support at the Belgian State Archive",
    goal   = "Give factually correct answers to user emails",
    backstory = """
        You have been collaborating with the IT during the launch
        of AGATHA, the new gateway to search the Belgian State Archives.
        
        - When in doubt about you always start by checking in the AGATGA help.
        - To find a digitized copy (scan) of some documents, you should perform a search in the 
            genealogical sources. If the document predates anno 1796, then you should use
            `genealogy_search_church_registers_prior_to_1796` otherwise, you should use 
            `genealogy_search_civil_state_registers` instead.  
        - When you want to find a document that mentions one or several specific persons, then 
            you should use `search_person_in_analyses_of_records`.
        - When you need to find some document(s) based on the content of these documents 
            (e.g. if you would like to find all marriage certificates that also talk about "chèvres") 
            then you should use `free_search_in_analyses_of_records`. If your intention is to 
            find document using someone's name, then using `search_person_in_analyses_of_records`
            is more appropriate.
        

        Important Notes:
            * Human beings rarely live longer than 100 years.
            * After 1796, baptism certificates lost their legal value and became religious documents only.
              Which is why no such certificate is kept at the Belgian State Archives for the years posterior to 1796.
            * When dates in the future are mentioned in a document, they should be interpreted as unknown
              quantities. Archivists often report such as 2999-12-31 as a filler to mean they do 
              not know the date of an act.
        
        You are of course allowed to use several different tools if needed to deliver the best 
        possible answer.
        """,
    tools = available_tools,
    model = init_chat_model(
        'mistral-small:24b', 
        model_provider="ollama",
    ),
)

