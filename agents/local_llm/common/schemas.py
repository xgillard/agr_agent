"""Common datatypes that are used accross all tool calls in AGATHA."""

from typing import Any

from langgraph.graph import MessagesState
from pydantic import BaseModel


class AgathaToolState(MessagesState, total=False):
    """The base data type to implement the tool steps to search in AGATHA.

    Attributes:
        call_tool (str): the name of the tool to be called.
        call_request (Any): the request sent to the tool.
        call_data (Any): the outcome of a tool call
        output (str): the result of the search in agatha
    """
    
    call_tool: str
    call_request: Any 
    call_data: Any
    output: str


class Choices[Choice](BaseModel):
    """A generic choice

    Attributes:
        choices (list[Choice]): the chosen options
    """

    choices: list[Choice]

    def options(self) -> list[Choice]:
        return self.choices


class SingleChoice[Choice](BaseModel):
    """A generic choice

    Attributes:
        choice (Choice): the chosen option
    """

    choice: Choice

