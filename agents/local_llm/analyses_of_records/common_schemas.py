"""Common data types to implement the search in analyses of records tool."""

from typing import TypedDict

from pydantic import BaseModel

from tools.agatha_common import PeriodSelector
from tools.analyses_of_records import (
    AnalysesActType,
    AnalysesProject,
)


class SearchAnalysesState(TypedDict, total=False):
    """The base data type to implement the steps to search in analyses of records.

    Attributes:
        outer_context (list): the outer context (= conversation that has happened outside of this wizzard)
        location (str|None): the location where the act has taken place
        period_selector (PeriodSelector|None): a precision on how to interpret the dates
        start_date (str|None): the start date or exact date
        end_date (str|None): the end date.
        act_type (AnalysesActType | None): the kind of act which is beign sought after.
        project (AnalysesProject | None): the project which led to this record being analyzed.
    """

    outer_context: list

    location: str | None
    period_selector: PeriodSelector|None
    start_date: str | None
    end_date: str | None
    act_type: AnalysesActType | None
    project: AnalysesProject | None


class Location(BaseModel):
    """Profession.
    
    Attributes:
        location (str|None): the location where it happened
    """

    location: str | None = None

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


class ActTypeChoice(BaseModel):
    """Act type choice.
    
    Attributes:
        act_type (AnalysesActType | None): the selected act type.
    """
    
    act_type: AnalysesActType | None = None


class ProjectChoice(BaseModel):
    """Project choice.
    
    Attributes:
        project (AnalysesProject | None): the selected project.
    """
    
    project: AnalysesProject | None = None

