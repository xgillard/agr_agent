"""Common datatypes that are used accross all tool calls in AGATHA."""

from langgraph.graph import MessagesState
from pydantic import BaseModel


class AgathaToolState(MessagesState, total=False):
    """The base data type to implement the tool steps to search in AGATHA.

    Attributes:
        intent (str): what info do you wish to find in AGATHA.
        call_data (BaseModel | None): the outcome of a tool call
    """
    
    intent: str
    call_data: BaseModel | list[BaseModel] | None


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

