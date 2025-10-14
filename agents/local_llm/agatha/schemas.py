"""data to sumup the available information."""

from typing import (
    Any,
)

from langgraph.graph import (
    MessagesState,
)
from pydantic import (
    BaseModel,
)


class SignaleticPerson(BaseModel):
    first_name: str | None = None
    family_name: str | None = None
    profession: str | None = None

class PeriodOfInterest(BaseModel):
    min_date_formatted_as_yyyy_mm_dd: str | None = None
    max_date_formatted_as_yyyy_mm_dd: str | None = None

class BaseCriteria(BaseModel):
    """The information that is easily gathered."""

    municipality_name_in_french_or_dutch: str | None = None
    parish_name: str | None = None

    people_of_interest: list[SignaleticPerson] | None = None
    period_of_interest: PeriodOfInterest | None = None

class AgentState(MessagesState):
    """State of the agent.
    
    Attributes:
        input (str): the user's request.
        scratch (str): the agent' scratchpad where all it knows its explicited.

        thought (str): the current thought (will be appended to scratchpad eventually)
        criteria (BaseCriteria): the basic search criteria
        
        call_tool (str): the name of the tool to be called.
        call_request (Any): the request sent to the tool.
        call_data (Any): the outcome of a tool call
        
        n (int): the number of erroneous tool calls.
    """

    input: str
    scratch: str

    thought: str
    criteria: BaseCriteria

    call_tool: str
    call_request: Any
    call_data: Any

    n: int
