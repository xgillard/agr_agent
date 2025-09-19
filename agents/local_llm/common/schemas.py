"""Common datatypes that are used accross all tool calls in AGATHA."""

from langgraph.graph import MessagesState
from pydantic import BaseModel


class AgathaToolState(MessagesState, total=False):
    """The base data type to implement the tool steps to search in AGATHA.

    Attributes:
        call_data (BaseModel | None): the outcome of a tool call
        output (str): the result of the search in agatha
    """
    
    call_data: BaseModel | list[BaseModel] | None
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

