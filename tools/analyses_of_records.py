"""Data structure and tools implementation to search in analyses of records on AGATHA.

Date: 2025-09-01
Author: X. Gillard
"""

from typing import Annotated

import requests
from pydantic import BaseModel, ConfigDict, Field

from .agatha_common import Municipality, PeriodSelector
from .generated import AnalysesActType, AnalysesProject

## Constants
BASE_URL  = "https://agatha.arch.be/search"
FORM_URL  = f"{BASE_URL}/analyses/results/"
AJAX_URL  = f"{BASE_URL}/analyses/ajax.php"

# WHICH_TAB = "FREE"

class AnalysesFreeSearchRequest(BaseModel):
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
        act_type (AnalysesActType | None): Written documents that record a change of status (baptism, marriage, burial,
            conscription, etc.) and have legal value (notarial act, judgment, etc.).
        project (AnalysesProject | None): List of projects executed by volunteers or staff of the State Archives.
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    search_terms: Annotated[str | None, Field(alias="SHORT_ALL_TEXTS")] = None
    location:     Annotated[str | None, Field(alias="ALL_PLACES")] = None
    period:       Annotated[PeriodSelector, Field(alias="CHOOSE_DATE_PERIODE")] = PeriodSelector.BETWEEN
    start_date:   Annotated[str | None, Field(alias="exactYear")] = None
    end_date:     Annotated[str | None, Field(alias="SHOW_PERIODE")] = None
    act_type:     Annotated[AnalysesActType | None, Field(alias="ACTTYPE")] = None
    project:      Annotated[AnalysesProject | None, Field(alias="PROJECT_ID")] = None




def free_search_in_records(req: AnalysesFreeSearchRequest, ajax: str):
    """
    TODO
    """
    data = req.model_dump(by_alias=True, exclude_none=True)

    if req.location:
        location = Municipality.by_name(
            req.location, 
            ajax=ajax, 
            return_single_best_match=True
        )

        if location is not None:
            data["ALL_PLACES"] = location.value
    
    data["CHOOSE_DATE_PERIODE"] = req.period.code
    data["WHICH_TAB"] = "FREE"
    ##
    search  = requests.post(FORM_URL, data = data)
    cookies = dict(search.cookies)
    ## fetch results
    results = requests.post(AJAX_URL, 
                      data = {
                          "method": "getResults", 
                          "pageSize": 20, 
                          "pageNumber": 1,
                      },
                      cookies = cookies)

    results = results.json()
    return results

def search_a_person():
    ...



if __name__ == "__main__":
    req = AnalysesFreeSearchRequest(
        search_terms="Gillard",
        #location="Wezembeek",
    )
    print(str(req))

    #rsp = free_search_in_records(req, ajax=AJAX_URL)
    #print(
    #    json.dumps(rsp, indent=4)
    #)
