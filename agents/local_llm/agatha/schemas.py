"""Datatypes to implement the base react behavior."""

from enum import StrEnum
from typing import (
    Any,
)

from langgraph.graph import MessagesState


class DataSource(StrEnum):
    """Data source that can be consulted to find more information.

    Attributes:
        ANALYSES_OF_RECORDS (str): search in analyses of records
        GENEALOGICAL_SOURCES (str): search digitized registers (genealogic sources)
        HELP_RESOURCES (str): manual and FAQ
    """

    ANALYSES_OF_RECORDS = "Analyses of records"
    DIGITIZED_REGISTERS = "Genealogical sources"
    HELP_RESOURCES = "Help Resources"

    @classmethod
    def all_values(cls) -> list[str]:
        """Return the list of possible values for this enum"""

        return [m._value_ for m in cls.__members__.values()]



class YesNo(StrEnum):
    """A boolean for llm.
    
    Attributes:
        YES (str): yes
        NO (str): no
    """

    YES = "yes"
    NO = "no"

    @classmethod
    def all_values(cls) -> list[str]:
        """Return the list of possible values for this enum"""

        return [m._value_ for m in cls.__members__.values()]


class AgentState(MessagesState):
    """State of the agent.
    
    Attributes:
        input (str): the user's request.
        scratch (str): the agent' scratchpad where all it knows its explicited.

        thought (str): the current thought (will be appended to scratchpad eventually)
        
        call_tool (str): the name of the tool to be called.
        call_request (Any): the request sent to the tool.
        call_data (Any): the outcome of a tool call
        
        n (int): the number of erroneous tool calls.
    """

    input: str
    scratch: str

    thought: str

    call_tool: str
    call_request: Any
    call_data: Any

    n: int