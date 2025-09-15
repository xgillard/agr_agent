"""Datatypes for a research in the genealogical sources."""

from enum import StrEnum

from pydantic import BaseModel

from ....tools.agatha_common import Municipality, PeriodSelector
from ...common.schemas import AgathaToolState


class TypeOfDocument(StrEnum):
    """What type of document do you wish to consider (acts or indexes)
    
    Attributes:
        ACTS (str): when you want to search the scan of an official actual act
        INDEX (str): when you want to search the scan of an index (long list of names
            associated with some documents)
        BOTH (str): when you want to search both in the acts registers as well as in
            the index registers.
    """

    ACTS = "acts"
    INDEXES = "indexes"
    BOTH = "both"

    @classmethod
    def all_values(cls) -> list[str]:
        """All possible values for this enum.
        
        Returns:
            list[str]: the list of all possible values of this enum
        """

        return [ m._value_ for m in cls.__members__.values() ]


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
        type_of_doc (TypeOfDocument): the kind of document we wish to find in the results.
    """
    
    municipality: Municipality
    period: YearPeriod
    type_of_doc: TypeOfDocument
