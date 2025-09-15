"""Datatypes for a research in the genealogical sources."""

from pydantic import BaseModel

from ....tools.agatha_common import Municipality, PeriodSelector
from ...common.schemas import AgathaToolState


class Choices[Choice](BaseModel):
    """A generic choice
    
    Attributes:
        choices (list[Choice]): the chosen options
    """

    choices: list[Choice]

    def options(self) -> list[Choice]:
        return self.choices


class YearPeriod(BaseModel):
    """Period when the act might have happened (on a yearly basis).
    
    Attributes:
        selector (PeriodSelector|None): a precision on how to interpret the date range
        start_year (int|None): the start (or exact) year.
        end_year (int|None): the year when this period ends.
    """

    selector: PeriodSelector | None = PeriodSelector.BETWEEN
    start_year: int | None = None
    end_year: int | None = None



class GeneaSearchState(AgathaToolState, total=False):
    """Base state for a workflow to search in genealogical sources.

    Attributes:
        municipality (str): the municipality whose registers need to be searched
        period (YearPeriod): the period when the act might have happened.
    """
    
    municipality: Municipality
    period: YearPeriod