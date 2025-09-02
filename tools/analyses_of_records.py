"""Data structure and tools implementation to search in analyses of records on AGATHA.

Date: 2025-09-01
Author: X. Gillard
"""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

from .agatha_common import PeriodSelector

## Constants
BASE_URL  = "https://agatha.arch.be/search"
FORM_URL  = f"{BASE_URL}/analyses/results/"
AJAX_URL  = f"{BASE_URL}/analyses/ajax.php"


class RecordType(StrEnum):
    """The type of record. 

    Written documents that record a change of status (baptism, marriage, burial, 
    conscription, etc.) and have legal value (notarial act, judgment, etc.).

    Attributes:
        
    """

# WHICH_TAB = "FREE"

class FreeSearchRequest(BaseModel):
    """
    A request to perform a free search in the analyses of records.

    Attributes:
        search_terms (str | None): Keyword(s) to define the search: e.g. person, building, object, place, etc.
            Tip: use the wildcards * and ? to expand or refine the search.
        location (str | None): In most cases, the municipality where the document was created or a municipality 
            linked to a person (e.g. place of birth or death).
        start_date (str | None): Exact date of the record (format DD/MM/YYYY), start date (or year) of the 
            interval in which one or more records were created.
        end_date (str | None): End date (or year) of the interval in which one or more records were created.
    """

    search_terms: Annotated[str | None, Field(alias="SHORT_ALL_TEXTS")] = None
    location:     Annotated[str | None, Field(alias="ALL_PLACES")] = None
    period:       Annotated[PeriodSelector, Field(alias="CHOOSE_DATE_PERIODE")] = PeriodSelector.BETWEEN
    start_date:   Annotated[str | None, Field(alias="exactYear")] = None
    end_date:     Annotated[str | None, Field(alias="SHOW_PERIODE")] = None




def free_search_in_records():
    ...

def search_a_person():
    ...