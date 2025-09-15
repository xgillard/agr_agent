"""Common datatypes that are used accross all tool calls in AGATHA."""

from langgraph.graph import MessagesState
from pydantic import BaseModel


class AgathaToolState(MessagesState, total=False):
    """The base data type to implement the tool steps to search in AGATHA.

    Attributes:
        call_data (BaseModel | None): the outcome of a tool call
    """

    call_data: BaseModel | list[BaseModel] | None

