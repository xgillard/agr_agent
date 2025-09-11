"""Common datatypes that are used accross all tool calls in AGATHA."""

from langgraph.graph import MessagesState
from pydantic import BaseModel

from ...tools.agatha_common import PeriodSelector


class AgathaToolState(MessagesState, total=False):
    """The base data type to implement the tool steps to search in AGATHA.

    Attributes:
        period_selector (PeriodSelector|None): a precision on how to interpret the dates
        start_date (str|None): the start date or exact date
        end_date (str|None): the end date.
    """

    period_selector: PeriodSelector|None
    start_date: str | None
    end_date: str | None


class Period(BaseModel):
    """Period when the act might have happened.
    
    Attributes:
        selector (PeriodSelector|None): a precision on how to interpret the dates
        start_date (str|None): the start date or exact date
        end_date (str|None): the end date.
    """

    selector: PeriodSelector | None = PeriodSelector.BETWEEN
    start_date: str | None = None
    end_date: str | None = None

