"""Datatypes to implement the base react behavior."""

from enum import StrEnum
from typing import Any

from langgraph.graph import MessagesState


class DataSource(StrEnum):
    """Data source that can be consulted to find more information.

    Attributes:
        ANALYSES_OF_RECORDS (str): analyses of records, to find the details of an act based on its content.
        DIGITIZED_REGISTERS (str): scans of the original registers where the acts are consigned.
        HELP_RESOURCES (str): manual and FAQ
    """

    ANALYSES_OF_RECORDS = "analyses_of_records"
    DIGITIZED_REGISTERS = "digitized_registers"
    HELP_RESOURCES = "help_resources"


class YesNo(StrEnum):
    """A boolean for llm.
    
    Attributes:
        YES (str): yes
        NO (str): no
    """

    YES = "yes"
    NO = "no"

class AgentState(MessagesState):
    """State of the agent.
    
    Attributes:
        input (str): the user's request.
        call_data (str): response to the current objective.
        n (int): the number of erroneous tool calls.
    """

    input: str
    call_data: Any

    n: int = 0