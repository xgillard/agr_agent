"""Data structure and tools implementation to search in analyses of records on AGATHA.

Date: 2025-09-01
Author: X. Gillard
"""

from typing import Annotated, Optional

import requests
from pydantic import BaseModel, ConfigDict, Field

from .agatha_common import Municipality, PeriodSelector
from .generated import AnalysesActRole, AnalysesActType, AnalysesProject

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

class AnalysesAct(BaseModel):
    """Description of an administrative act that took place in the past.

    Attrtibutes:
        act_id (str): globally unique identifier of this administrative act
        act_number (Optional[str]): act number that was used by the archive producer
        project (AnalysesProject): the project that led to the analysis of this record
        actplace (Optional[str]): the place where this act officially happened
        parish (Optional[str]): the parish where this act officially happened (if relevant)
        editorial_form (str): the type of document
        description (str): a brief description of this document
        act_date (str): the date when this administrative act actually took place.
        remarks (str): some remarks about this act
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    act_id: str
    act_number: Optional[str]
    project: AnalysesProject
    actplace: Optional[str]
    parish: Optional[str]
    editorial_form: str
    description: Optional[str]
    act_date: Optional[str]
    remarks: Optional[str]


## TODO: create the AnalysesPerson class and create those instances by processing the person_ fields.

def _clean(x: str|None) -> str|None:
        """Clean the value of x to remove the unnecessary 'NN' values and replace them with None.
        
        Args:
            x (str|None): the value we wish to clean
        
        Return: 
            str|None:
                - the same value as x when x is different from 'NN'
                - None whenever x is None or x == 'NN'
            
        Examples:
            >>> _clean('NN')

            >>> _clean("coucou")
            'coucou'

            >>> _clean(None)

        """

        return x if x != 'NN' else None


class AnalysesSearchResponseDocument(BaseModel):
    """Description of a document in a raw response from Agatha.
    
    Note:
        The document response mixes concerns about the act itself and
        the people that are mentioned in the act. Plus, it uses a columnar
        format for the persons data which I think could be made more obvious
        if the data that belong together were grouped together. Which is
        why, I have only adopted a restricted subset of the information
        I intend to use in a downstream simplified version of the document.

        Additionally, it is important to note that in many case the value 'NN'
        is being used to mention that no data is available. Which is why i propose
        to filter those values out in the simplified version of the data model.
        
    Attrtibutes:
        # attributes that directly relate to the act itself
        act_id (str): globally unique identifier of this administrative act
        act_number (Optional[str]): act number that was used by the archive producer
        project (AnalysesProject): the project that led to the analysis of this record
        actplace (Optional[str]): the place where this act officially happened
        parish (Optional[str]): the parish where this act officially happened (if relevant)
        editorial_form (str): the type of document
        description (str): a brief description of this document
        act_date (str): the date when this administrative act actually took place.
        remarks (str): some remarks about this act
        # attributes relating to the persons that are mentioned in the act
        person_name (list[str]): list of names of the persons mentioned in the document
        person_title (list[str]): title of the persons mentioned in the document (eg. Dr)
        person_birth_date (list[str]): birthdates of the people mentioned in the document
        person_birth_place (list[str]): places of births of the people mentioned in the document
        person_death_date (list[str]): death date of these people
        person_death_place (list[str]): dath place of these people
        person_residence_location (list[str]): location where these people used to reside
        person_civil_status (list[str]): civil statuses of thes people
        person_remarks (list[str]): remarks about each of those people
        person_occupation (list[str]): the job of those people
        person_role_code (list[str]): the role each person played in the act
        person_age (list[str]): the age of all people when the act happened.
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    # attributes that belong to the act description itself.
    act_id: Annotated[str, Field(alias="ACT_ID")]
    act_number: Annotated[Optional[str], Field(alias="ACT_NUMBER")]
    project: Annotated[AnalysesProject, Field(alias="PROJECT_ID")]
    actplace: Annotated[Optional[str], Field(alias="ACTPLACE_STRING")]
    parish: Annotated[Optional[str], Field(alias="PARISH")]
    editorial_form: Annotated[str, Field(alias="EDITORIALFORM_ENG")]
    description: Annotated[str, Field(alias="ACT_DESCRIPTION")]
    act_date: Annotated[Optional[str], Field(alias="ACTDATE")]
    remarks: Annotated[Optional[str], Field(alias="REMARKS_ACT")]
    # attributes relating to the persons that are mentioned in the act
    person_name: Annotated[list[str], Field(alias="FULL_NAME")]
    person_title: Annotated[list[str], Field(alias="TITLE_PERSON")]
    person_birth_date: Annotated[list[str], Field(alias="BIRTHDATE")]
    person_birth_place: Annotated[list[str], Field(alias="BIRTHPLACE")]
    person_death_date: Annotated[list[str], Field(alias="DEATHDATE")]
    person_death_place: Annotated[list[str], Field(alias="DEATHPLACE")]
    person_residence_location: Annotated[list[str], Field(alias="RESIDENCE")]
    person_civil_status: Annotated[list[str], Field(alias="CIVILSTATUS")]
    person_remarks: Annotated[list[str], Field(alias="REMARKS_PERSON")]
    person_occupation: Annotated[list[str], Field(alias="OCCUPATION")]
    person_role_code: Annotated[list[str], Field(alias="ACTROLE_CODE")]
    person_age: Annotated[list[str], Field(alias="AGE")]

    @property
    def act(self) -> AnalysesAct:
        """Return a simplified representation of this act (no people)."""

        return AnalysesAct(
            act_id=self.act_id,
            act_number = _clean(self.act_number),
            project = self.project,
            actplace = _clean(self.actplace),
            parish = _clean(self.parish),
            editorial_form = self.editorial_form,
            description = _clean(self.description),
            act_date = _clean(self.act_date),
            remarks = _clean(self.remarks),
        )

    
class AnalysesSearchResponse(BaseModel):
    """A raw search response from the call to agatha.
    
    Attributes:
        numFound (int): the number of results corresponding to the search request
        start (int): offset of the 1st document in the complete list of possible results
        docs (list[AnalysesSearchResponseDocument]): the list of actual documents that
            matched with the user's search request.
    """

    numFound: int
    start: int
    docs: list[AnalysesSearchResponseDocument]


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
                          "pageSize": 2, 
                          "pageNumber": 1,
                      },
                      cookies = cookies)

    return AnalysesSearchResponse(**(results.json()["response"]))

def search_a_person():
    ...



if __name__ == "__main__":
    req = AnalysesFreeSearchRequest(
        search_terms="Gillard",
        #location="Wezembeek",
    )

    rsp = free_search_in_records(req, ajax=AJAX_URL)
    print(rsp.docs[0].act)

    print(AnalysesActRole.from_code("7"))
