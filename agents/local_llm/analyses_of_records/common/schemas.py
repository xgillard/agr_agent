"""Common data types to implement the search in analyses of records tool."""


from pydantic import BaseModel

from ....local_llm.common.schemas import AgathaToolState
from ....tools.analyses_of_records import (
    AnalysesActType,
    AnalysesProject,
)


class SearchAnalysesState(AgathaToolState, total=False):
    """The base data type to implement the steps to search in analyses of records.

    Attributes:
        location (str|None): the location where the act has taken place
        period_selector (PeriodSelector|None): a precision on how to interpret the dates
        start_date (str|None): the start date or exact date
        end_date (str|None): the end date.
        act_type (AnalysesActType | None): the kind of act which is beign sought after.
        project (AnalysesProject | None): the project which led to this record being analyzed.
    """

    location: str | None
    act_type: AnalysesActType | None
    project: AnalysesProject | None


class Location(BaseModel):
    """Profession.
    
    Attributes:
        location (str|None): the location where it happened
    """

    location: str | None = None


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

