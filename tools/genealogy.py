"""A set of tools that implement research in genealogical sources."""

from enum import StrEnum
from typing import Annotated, Literal
import pydantic
import requests as rq
from textdistance import levenshtein

from langchain_core.tools import tool


## Constants
BASE_URL  = "https://agatha.arch.be/search"
AJAX_URL  = f"{BASE_URL}/genealogie/ajax.php"
GENEA_URL = f"{BASE_URL}/genealogie/results/"

## 
class Municipality(pydantic.BaseModel):
    """All the technical data used to retrieve a given municipality"""

    label:         Annotated[str, "How this municipality should be displayed"]
    value:         Annotated[str, "Name that should be used when referencing this municipality"]
    CURRENT_NAME:  Annotated[str, "The current denomincation of this municipality"]
    PLACEPOINT_ID: Annotated[int, "The effective identifier of this municipality"]
    PARISHES_ID:   Annotated[int | None, "If present, the id of the parish in the municipality"]

def municipality_by_name(
    name:   str, 
) -> list[Municipality]:
    """Find municipality data by name."""
    r = rq.post(AJAX_URL, data = {
        "method": "getMunicipalities",
        "term"  : name,   # location qu'on veut trouver
    })
    return [ Municipality(**x) for x in r.json() ]

## 
class GenealogySource(StrEnum):
    CHURCH = "PR" # Church Register before 1796"
    CIVIL  = "CS" # "Civil State after 1796"


## Types relating to a genealogical search within church registers
class ParishActType(StrEnum):
    BIRTH_OR_BAPTISM = "1"
    WEDDING          = "2"
    DEATH            = "3"
    OTHER_DOCUMENTS  = "OTHER"

class OtherParishActType(StrEnum):
    LIST_OF_COMMUNIANTS = "11"
    DISPENSATION_OF_MARRIAGE_CERTIFICATE = "12"
    IMPEDIMENT_OF_MARRIAGE_CERTIFICATE = "20"
    LIST_OF_NAMES = "23"
    LIST_OF_CONFIRMANDS = "31"
    MEMORY_MASSES = "56"
    STATUS_ANIMARUM = "28"
    
class ParishIndices(StrEnum):
    BIRTH_OR_BAPTISM = "1"
    WEDDING          = "2" 
    DEATH            = "3"

## Types relating to a genealogical search within civil registers
class CivilActType(StrEnum):
    BIRTH            = "1"
    WEDDING          = "2"
    DEATH            = "3"
    OTHER_DOCUMENTS  = "OTHER"

class OtherCivilActType(StrEnum):
    ADDITIONAL_REGISTER = "BS_U"
    ADOPTION_CERTIFICATE= "BS_A"
    DEATH_ANNEXES       = "BS_Ob"
    DIVORCE_CERTIFICATE = "BS_E"
    NATURALISATION_CERTIFICATE = "BS_N"

class CivilIndices(StrEnum):
    ANNUAL_INDEX_OF_DIVORCE = "BS_Ei"
    ANNUAL_INDEX_OF_NATURALISATION = "BS_Ni"
    ANNUAL_INDEX_OF_ADDITIONAL_REGISTER = "BS_Ui"
    DECENNAL_INDEX_OF_ADOPTION = "BS_Ax"
    DECENNAL_INDEX_OF_DIVORCE = "BS_Ex"
    DECENNAL_INDEX_OF_NATURALISATION = "BS_Nx"

class Parish(pydantic.BaseModel):
    """A parish identified within a community"""

    PARISH_ID:    Annotated[int, "The technical identifier used to reference the parish"]
    PLACE_NAME:   Annotated[str, "The name of the parish"]


def parish_by_municipality(
    municipality: Municipality,
) -> list[Parish]:
    """Find the list of parishes within a given municipality."""
    r = rq.post(AJAX_URL, data = {
        "method":        "getParishFromMunicipality",
        "PLACEPOINT_ID": municipality.PLACEPOINT_ID,
    })
    return [ Parish(**x) for x in r.json() ]




class GenealogySearchResult(pydantic.BaseModel): 
    """A simplified interface that yields all the useful information (and no more)"""

    description: Annotated[str, "Description"]
    start_date:  Annotated[str, "First day covered by this document"]
    end_date:    Annotated[str, "Last day covered by this document"]
    last_update: Annotated[str, "Date when this archive was last modified"]
    notes:       Annotated[str, "Remarks and notes about this document"]
    available:   Annotated[bool,"Is this document available for online consultation"]
    url:         Annotated[str | None, "URL where this document can be consulted (if available)"]
    

class GenealogyDocument(pydantic.BaseModel):
    """A document that has been found by a research in the genealogic sources."""
    
    BOOKPART_ID: Annotated[str, "Identifier that is used to retrieve the actual document scan"]
    BOOKPARTPLACE_ID: Annotated[str, "I don't know what this means"]
    NEW_MUNICIPALITIES: Annotated[str | None, "New municipality name (after merge)"]
    OLD_MUNICIPALITIES: Annotated[str | None, "Municipality name (before they were merged)"]
    PLACE_NAME: Annotated[str | None, "Parish name (if relevant)"]
    FULL_PARISH_NAME: Annotated[str | None, "Full parish name (if relevant)"]
    START_DAY: Annotated[int | None, "First day covered by this document (day)"]
    START_MONTH: Annotated[int | None, "First day covered by this document (month)"]
    START_YEAR: Annotated[int | None, "First day covered by this document (year)"]
    END_DAY: Annotated[int | None, "Last day covered by this document (day)"]
    END_MONTH: Annotated[int | None, "Last day covered by this document (month)"]
    END_YEAR: Annotated[int | None, "Last day covered by this document (year)"]
    BOOK_LAST_MODIF_DATE: Annotated[str | None, "Date when this archive was last modified"]
    DESCRIPTION: Annotated[str | None, "Description"]
    FULL_REMARKS: Annotated[str | None, "Remarks wrt the document (e.g. missing)"]
    PUBLISH_DATE_REF: Annotated[str | None, "Date when this archive was published"]
    EDITORIALFORMBASE_ID: Annotated[str | None, "Identifier of the document type"]
    ISINDEX: Annotated[str | None, "Does it come from an index"]
    NOTES: Annotated[str | None, "Additional notes regarding this document"]
    AVAILABLE: Annotated[bool | None, "Is the document available for online consultation"]

    def simplified(self) -> GenealogySearchResult:
        """Returns a simplified version of this object"""
        return GenealogySearchResult(
            description = self.DESCRIPTION,
            start_date  = f"{self.START_DAY:02d}/{self.START_MONTH:02d}/{self.START_YEAR:02d}",
            end_date    = f"{self.END_DAY:02d}/{self.END_MONTH:02d}/{self.END_YEAR:02d}",
            last_update = self.BOOK_LAST_MODIF_DATE,
            notes       = (self.NOTES + "\n" if self.NOTES is not None else "") + (self.FULL_REMARKS + "\n" if self.FULL_REMARKS is not None else ""),
            available   = self.AVAILABLE,
            url         = self.find_url()
        )

    def find_url(self) -> str:
        """Retrieve this document URL"""
        if self.AVAILABLE:
            return rq.get(f"{BASE_URL}/genealogie/{self.BOOKPART_ID}").url
            #return f"{BASE_URL}/genealogie/{self.BOOKPART_ID}"
        else:
            return None


@tool
def genealogy_search_church_registers_prior_to_1796(
    municipality_name: Annotated[str, "Name of the municipality"],
    parish_name: Annotated[str | None, "Name of the parish"] = None,
    act_types: Annotated[list[ParishActType], "The kind of document we are searching for"] = None,
    other_types: Annotated[list[OtherParishActType] | None, "Mandatory when act_types is OTHER"] = None,
    index_types: Annotated[list[ParishIndices] | None, "The kind of index where to search data"] = None,
    start_year: Annotated[int | None, "Start year of the considered period"] = None,
    end_year: Annotated[int | None, "End year of the considered period"] = None,
) -> list[GenealogySearchResult]:
    """Search in the Church Registers (prior to 1796).

    Note: providing at least one 'act_types' or 'index_types' in mandatory.
    """
    municipality = min(municipality_by_name(municipality_name), key = lambda x: levenshtein(x.value, municipality_name))
    parishes     = parish_by_municipality(municipality)

    if parish_name is not None:
        parishes = [ p for p in parishes if parish_name in p.PLACE_NAME.lower() ]
        
    #
    request_data = {
        "WHICH_TAB": "PR",
        "PLACEPOINT_ID_PR" : municipality.PLACEPOINT_ID,
        "PLACE_PR": municipality.value,
        "CURRENT_NAME_PR": municipality.CURRENT_NAME,
        "PARISH_ID[]": ",".join( str(p.PARISH_ID) for p in parishes ),
    }
    
    if act_types is not None:
        request_data["TYPEACTES_PR[]"] = ",".join(act_types)
    
    if other_types is not None:
        request_data["TYPEACTES_OTHER_PR[]"] = other_types

    if index_types is not None:
        request_data["TYPEINDEX_PR[]"] = index_type

    if start_year is not None:
        request_data["exactYear"] = start_year

    if end_year is not None:
        request_data["SHOW_PERIODE"] = end_year
    
    ## search genea
    search  = rq.post(GENEA_URL, data = request_data)
    cookies = dict(search.cookies)
    ## fetch results
    results = rq.post(AJAX_URL, 
                      data = {
                          "method": "getResults", 
                          "pageSize": 10, 
                          "pageNumber": 1,
                      },
                      cookies = cookies)

    results = results.json()
    results = results["response"]["docs"]
    return [GenealogyDocument(**x).simplified() for x in results]


@tool
def genealogy_search_civil_state_registers(
    municipality_name: Annotated[str, "Name of the municipality"],
    act_types: Annotated[list[CivilActType], "The kind of document we are searching for"] = None,
    other_types: Annotated[list[OtherCivilActType] | None, "Mandatory when act_types is OTHER"] = None,
    index_types: Annotated[list[CivilIndices] | None, "The kind of index where to search data"] = None,
    start_year: Annotated[int | None, "Start year of the considered period"] = None,
    end_year: Annotated[int | None, "End year of the considered period"] = None,
) -> list[GenealogySearchResult]:
    """Search in the Church Registers (prior to 1796).

    Note: providing at least one 'act_types' or 'index_types' in mandatory.
    """
    municipality = min(municipality_by_name(municipality_name), key = lambda x: levenshtein(x.value, municipality_name))

    request_data = {
        "WHICH_TAB": "CS",
        "PLACEPOINT_ID_CS" : municipality.PLACEPOINT_ID,
        "PLACE_CS": municipality.value,
        "CURRENT_NAME_CS": municipality.CURRENT_NAME,
        "CHOOSE_DATE_PERIODE": "1",
    }
    
    if act_types is not None:
        request_data["TYPEACTES_CS[]"] = ",".join(act_types)
    
    if other_types is not None:
        request_data["TYPEACTES_OTHER_CS[]"] = other_types

    if index_types is not None:
        request_data["TYPEINDEX_CS[]"] = index_type

    if start_year is not None:
        request_data["exactYear"] = start_year

    if end_year is not None:
        request_data["SHOW_PERIODE"] = end_year
    
    ## search genea
    search  = rq.post(GENEA_URL, data = request_data)
    cookies = dict(search.cookies)
    ## fetch results
    results = rq.post(AJAX_URL, 
                      data = {
                          "method": "getResults", 
                          "pageSize": 10, 
                          "pageNumber": 1,
                      },
                      cookies = cookies)

    results = results.json()
    results = results["response"]["docs"]
    return [GenealogyDocument(**x).simplified() for x in results]
    