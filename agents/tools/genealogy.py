"""Data structure and tools implementation to search in genealogical sources on AGATHA.

Date: 2025-09-01
Author: X. Gillard
"""

from enum import StrEnum
from functools import cached_property
from typing import Annotated, Optional

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, ConfigDict, Field

from .agatha_common import Municipality, Parish, PeriodSelector

## Constants
BASE_URL  = "https://agatha.arch.be/search"
AJAX_URL  = f"{BASE_URL}/genealogie/ajax.php"
GENEA_URL = f"{BASE_URL}/genealogie/results/"

## 
class GenealogySource(StrEnum):
    """The possible sources of genealogical acts.

    Attributes:
        CHURCH_REGISTERS (str): Church register prior to 1796
        CIVIL_STATE (str): Civil State for ther records posterior to 1796
    """
    
    CHURCH_REGISTERS = "church-registers"
    CIVIL_STATE      = "civil-state"
    
    @property
    def code(self) -> str:
        """The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        """

        match self:
            case GenealogySource.CHURCH_REGISTERS:
                return "PR"
            case GenealogySource.CIVIL_STATE:
                return "CS"
    
        
    @classmethod    
    def all_values(cls) -> list[str]:
      """Return all the authorized values for this enum.
      
      Returns:
        list[str]: all the authorized values for this enum.
      """
      return [ v._value_ for v in cls.__members__.values() ]
    
    @classmethod
    def all_codes(cls) -> list[str]:
      """Return all the authorized codes for this enum.
      
      Returns:
        list[str]: all the authorized codes for this enum.
      """
      return [ v.code for v in cls.__members__.values() ]


## Types relating to a genealogical search within church registers
class ParishActType(StrEnum):
    """The kind of act documents that can be found in church registers prior to 1796.

    Attributes:
        BAPTISM (str): birth or baptism certificate
        WEDDING (str): wedding certificate
        DEATH (str): funeral / death certificate
        OTHER (str): other kind of documents
    """
    
    BAPTISM = "birth-or-baptism-certificate"
    WEDDING = "wedding-certificate"
    DEATH   = "death-certificate"
    OTHER   = "other"

    @property
    def code(self) -> str:
        """The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        """

        match self:
            case ParishActType.BAPTISM:
                return "1"
            case ParishActType.WEDDING:
                return "2"
            case ParishActType.DEATH:
                return "3"
            case ParishActType.OTHER:
                return "OTHER"
    
        
    @classmethod    
    def all_values(cls) -> list[str]:
      """Return all the authorized values for this enum.
      
      Returns:
        list[str]: all the authorized values for this enum.
      """
      return [ v._value_ for v in cls.__members__.values() ]
    
    @classmethod
    def all_codes(cls) -> list[str]:
      """Return all the authorized codes for this enum.
      
      Returns:
        list[str]: all the authorized codes for this enum.
      """
      return [ v.code for v in cls.__members__.values() ]



class OtherParishActType(StrEnum):
    """Precision regarding what 'other' documents should be searched in the church registers.

    Attributes:
        MARRIAGE_EXEMPTION (str): Certificates of dispensations of marriage (Certificate by which an authority 
               releases a person from an obligation or prohibition, in this case the celebration of marriage.)
        MARRIAGE_IMPEDIMENT (str): Certificates of impediment of marriage (Certificate of objection to the 
                marriage on the grounds of non-compliance with a condition for the celebration of the marriage.)
        LIST_OF_COMMUNIANTS (str): List of communicants (Persons who have received the sacrament of eucharist.)
        LIST_OF_CONFIRMANDS (str): List of confirmands (Persons who have received the sacrament of confirmation.)
        LIST_OF_NAMES (str): List of names (List of person drawn up for an event (e.g. for Sunday prayers) or for 
                an association (e.g. membership list of a fraternity).
        MEMORY_MASSES (str): Memory masses (List of deceased persons for whom a church service should be organised 
                annually in memory and for the salvation of souls.)
        STATUS_ANIMARUM (str): Status animarum (List per street or district of the families in a parish 
                (state of souls), with information about the age of the residents, confirmation, ...)
    """
    
    MARRIAGE_EXEMPTION  = "marriage-exemption"
    MARRIAGE_IMPEDIMENT = "marriage-impediment"
    LIST_OF_COMMUNIANTS = "list-of-communiants"
    LIST_OF_CONFIRMANDS = "list-of-confirmands"
    LIST_OF_NAMES       = "list-of-names"
    MEMORY_MASSES       = "memory-masses"
    STATUS_ANIMARUM     = "status-animarum"

    @property
    def code(self) -> str:
        """The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        """

        match self:
            case OtherParishActType.MARRIAGE_EXEMPTION: 
                return "12"
            case OtherParishActType.MARRIAGE_IMPEDIMENT: 
                return "20"
            case OtherParishActType.LIST_OF_COMMUNIANTS: 
                return "11"
            case OtherParishActType.LIST_OF_CONFIRMANDS: 
                return "31"
            case OtherParishActType.LIST_OF_NAMES: 
                return "23"
            case OtherParishActType.MEMORY_MASSES: 
                return "56"
            case OtherParishActType.STATUS_ANIMARUM: 
                return "28"
        
    @classmethod    
    def all_values(cls) -> list[str]:
      """Return all the authorized values for this enum.
      
      Returns:
        list[str]: all the authorized values for this enum.
      """
      return [ v._value_ for v in cls.__members__.values() ]
    
    @classmethod
    def all_codes(cls) -> list[str]:
      """Return all the authorized codes for this enum.
      
      Returns:
        list[str]: all the authorized codes for this enum.
      """
      return [ v.code for v in cls.__members__.values() ]
        

class ParishIndex(StrEnum):
    """Possible indexes where to look up documents in the church registers (prior to 1796).

    Attributes:
        BAPTISM (str): Birth or baptism certificates
        WEDDING (str): Wedding certificates
        DEATH (str): Death / funeral certificates
    """
    
    BAPTISM = "baptism-certificates"
    WEDDING = "wedding-certificates" 
    DEATH   = "death-certificates"

    @property
    def code(self) -> str:
        """The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        """

        match self:
            case ParishIndex.BAPTISM: 
                return "1"
            case ParishIndex.WEDDING:
                return "2"
            case ParishIndex.DEATH: 
                return "3"
    
        
    @classmethod    
    def all_values(cls) -> list[str]:
      """Return all the authorized values for this enum.
      
      Returns:
        list[str]: all the authorized values for this enum.
      """
      return [ v._value_ for v in cls.__members__.values() ]
    
    @classmethod
    def all_codes(cls) -> list[str]:
      """Return all the authorized codes for this enum.
      
      Returns:
        list[str]: all the authorized codes for this enum.
      """
      return [ v.code for v in cls.__members__.values() ]


## Types relating to a genealogical search within civil registers
class CivilActType(StrEnum):
    """The kind of documents that can be found in Civil State registers after 1796.

    Attributes:
        BIRTH (str): Birth certificates
        WEDDING (str): Wedding certificates
        DEATH (str): Death certificates
        OTHER (str): Other kind of documents
    """
    
    BIRTH   = "birth-certificate"
    WEDDING = "wedding-certificate"
    DEATH   = "death-certificate"
    OTHER   = "other"

    @property
    def code(self) -> str:
        """The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        """

        match self:
            case CivilActType.BIRTH: 
                return "1"
            case CivilActType.WEDDING: 
                return "2"
            case CivilActType.DEATH: 
                return "3"
            case CivilActType.OTHER: 
                return "OTHER"
    
    @classmethod    
    def all_values(cls) -> list[str]:
      """Return all the authorized values for this enum.
      
      Returns:
        list[str]: all the authorized values for this enum.
      """
      return [ v._value_ for v in cls.__members__.values() ]
    
    @classmethod
    def all_codes(cls) -> list[str]:
      """Return all the authorized codes for this enum.
      
      Returns:
        list[str]: all the authorized codes for this enum.
      """
      return [ v.code for v in cls.__members__.values() ]


class OtherCivilActType(StrEnum):
    """Precision regarding what 'other' documents should be searched in the civil state registers.

    Attributes:
        ADDITIONAL_REGISTER (str): Additional register (Supplement to a register containing 
            exhibited documents (extracts) or notes.)
        ADOPTION (str): Adoption certificates (Certificate by which a court or authority establishes 
            a legal direct relationship between persons who are not blood relatives.)
        DEATH_ANNEXES (str): Death annexes (Extracts of deaths abroad or death declarations of missing persons 
            (after the World Wars) attached to death certificates.)
        DIVORCE (str): Divorce certificates (Certificate of the termination of marriage.).
        NATURALISATION (str): Naturalisation certificates (Certificate by which a court or authority grants 
            ationality to a person). 
    """
    
    ADDITIONAL_REGISTER = "additional-register"
    ADOPTION            = "adoption"
    DEATH_ANNEXES       = "death-annexes"
    DIVORCE             = "divorce"
    NATURALISATION      = "naturalization"

    @property
    def code(self) -> str:
        """The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        """

        match self: 
            case OtherCivilActType.ADDITIONAL_REGISTER:
                return "BS_U"
            case OtherCivilActType.ADOPTION:
                return "BS_A"
            case OtherCivilActType.DEATH_ANNEXES:
                return "BS_Ob"
            case OtherCivilActType.DIVORCE:
                return "BS_E"
            case OtherCivilActType.NATURALISATION:
                return "BS_N"
        
    @classmethod    
    def all_values(cls) -> list[str]:
      """Return all the authorized values for this enum.
      
      Returns:
        list[str]: all the authorized values for this enum.
      """
      return [ v._value_ for v in cls.__members__.values() ]
    
    @classmethod
    def all_codes(cls) -> list[str]:
      """Return all the authorized codes for this enum.
      
      Returns:
        list[str]: all the authorized codes for this enum.
      """
      return [ v.code for v in cls.__members__.values() ]


class CivilIndex(StrEnum):
    """Possible indexes where to look up documents in the church registers (prior to 1796).

    Attributes:
        BIRTH (str): Birth certificates
        WEDDING (str): Wedding certificates
        DEATH (str): Death / funeral certificates
    """
    
    BIRTH   = "birth-certificates"
    WEDDING = "wedding-certificates" 
    DEATH   = "death-certificates"
    OTHER   = "other"

    @property
    def code(self) -> str:
        """The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        """

        match self:
            case CivilIndex.BIRTH: 
                return "1"
            case CivilIndex.WEDDING:
                return "2"
            case CivilIndex.DEATH: 
                return "3"
            case CivilIndex.OTHER:
                return "OTHER"
    
        
    @classmethod    
    def all_values(cls) -> list[str]:
      """Return all the authorized values for this enum.
      
      Returns:
        list[str]: all the authorized values for this enum.
      """
      return [ v._value_ for v in cls.__members__.values() ]
    
    @classmethod
    def all_codes(cls) -> list[str]:
      """Return all the authorized codes for this enum.
      
      Returns:
        list[str]: all the authorized codes for this enum.
      """
      return [ v.code for v in cls.__members__.values() ]


class OtherCivilIndex(StrEnum):
    """Possible indexes where to look up documents in the civil state registers (after 1796).

    Attributes:
        ANNUAL_INDEX_OF_DIVORCE (str): Annual index of divorce certificates
        ANNUAL_INDEX_OF_NATURALISATION (str): Annual index of naturalisation certificates
        ANNUAL_INDEX_OF_ADDITIONAL_REGISTER (str): Index of additional register
        DECENNAL_INDEX_OF_ADOPTION (str): Ten-year index of adoption certificates
        DECENNAL_INDEX_OF_DIVORCE (str): Ten-year index of divorce certificates
        DECENNAL_INDEX_OF_NATURALISATION (str): Ten-year index of naturalisation certificates
    """
    
    ANNUAL_INDEX_OF_DIVORCE             = "annual-index-of-divorce"
    ANNUAL_INDEX_OF_NATURALISATION      = "annual-index-of-naturalisation"
    ANNUAL_INDEX_OF_ADDITIONAL_REGISTER = "annual-index-of-additional-register"
    DECENNAL_INDEX_OF_ADOPTION          = "decennal-index-of-adoption"
    DECENNAL_INDEX_OF_DIVORCE           = "decennal-index-of-divorce"
    DECENNAL_INDEX_OF_NATURALISATION    = "decennal-index-of-naturalisation"

    @property
    def code(self) -> str:
        """The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        """

        match self:
            case OtherCivilIndex.ANNUAL_INDEX_OF_DIVORCE:
                return "BS_Ei"
            case OtherCivilIndex.ANNUAL_INDEX_OF_NATURALISATION:
                return "BS_Ni"
            case OtherCivilIndex.ANNUAL_INDEX_OF_ADDITIONAL_REGISTER:
                return "BS_Ui"
            case OtherCivilIndex.DECENNAL_INDEX_OF_ADOPTION:
                return "BS_Ax"
            case OtherCivilIndex.DECENNAL_INDEX_OF_DIVORCE:
                return "BS_Ex"
            case OtherCivilIndex.DECENNAL_INDEX_OF_NATURALISATION:
                return "BS_Nx"
        
    @classmethod    
    def all_values(cls) -> list[str]:
      """Return all the authorized values for this enum.
      
      Returns:
        list[str]: all the authorized values for this enum.
      """
      return [ v._value_ for v in cls.__members__.values() ]
    
    @classmethod
    def all_codes(cls) -> list[str]:
      """Return all the authorized codes for this enum.
      
      Returns:
        list[str]: all the authorized codes for this enum.
      """
      return [ v.code for v in cls.__members__.values() ]


## Results of a search in the genealogical sources.
class GenealogySearchResult(BaseModel): 
    """A simplified interface for the genealogy search result.
    
    Attributes:
        description (str): Description of the document.
        start_date (str): Day of the first act recorded in this document
        end_date (str): Day of the last act recorded in 
        last_update (str): Date when this archive was last modified
        notes (str): Remarks and notes about this document
        available (bool): Is this document available for online consultation
        url (Optional[str]): URL where this document can be consulted (if available)
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    description: Optional[str]
    start_date:  Optional[str]
    end_date:    Optional[str]
    last_update: Optional[str]
    notes:       Optional[str]
    available:   bool
    url:         Optional[str]
    

class GenealogyDocument(BaseModel):
    """An entry from the results of a search in the genealogic sources.

    Attributes:
        bookpart_id (str): Identifier that is used to retrieve the actual document scan
        bookpartplace_id (str): I don't know what this means
        new_municipalities (Optional[str]): New municipality name (after merge)
        old_municipalities (Optional[str]): Municipality name (before they were merged)
        place_name (Optional[str]): Parish name (if relevant)
        full_parish_name (Optional[str]): Full parish name (if relevant)
        start_day (Optional[int]): Date of the first act recorded in this document (day)
        start_month (Optional[int]): Date of the first act recorded in this document (month)
        start_year (Optional[int]): Date of the first act recorded in this document (year)
        end_day (Optional[int]): Date of the last act recorded in this document (day)
        end_month (Optional[int]): Date of the last act recorded in this document (month)
        end_year (Optional[int]): Date of the last act recorded in this document (year)
        book_last_modif_date (Optional[str]): Date when this archive was last modified
        description (Optional[str]): Description
        full_remarks (Optional[str]): Remarks wrt the document (e.g. missing)
        publish_date_ref (Optional[str]): Date when this archive was published
        editorialformbase_id (Optional[str]): Identifier of the document type
        isindex (Optional[str]): Does it come from an index
        notes (Optional[str]): Additional notes regarding this document
        available (Optional[bool]): Is the document available for online consultation
    """
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    bookpart_id:          Annotated[str,           Field(alias="BOOKPART_ID")]
    bookpartplace_id:     Annotated[str,           Field(alias="BOOKPARTPLACE_ID")]
    new_municipalities:   Annotated[Optional[str], Field(alias="NEW_MUNICIPALITIES")] = None
    old_municipalities:   Annotated[Optional[str], Field(alias="OLD_MUNICIPALITIES")] = None
    place_name:           Annotated[Optional[str], Field(alias="PLACE_NAME")] = None
    full_parish_name:     Annotated[Optional[str], Field(alias="FULL_PARISH_NAME")] = None
    start_day:            Annotated[Optional[int], Field(alias="START_DAY")] = None
    start_month:          Annotated[Optional[int], Field(alias="START_MONTH")] = None
    start_year:           Annotated[Optional[int], Field(alias="START_YEAR")] = None
    end_day:              Annotated[Optional[int], Field(alias="END_DAY")] = None
    end_month:            Annotated[Optional[int], Field(alias="END_MONTH")] = None
    end_year:             Annotated[Optional[int], Field(alias="END_YEAR")] = None
    book_last_modif_date: Annotated[Optional[str], Field(alias="BOOK_LAST_MODIF_DATE")] = None
    description:          Annotated[Optional[str], Field(alias="DESCRIPTION")] = None
    full_remarks:         Annotated[Optional[str], Field(alias="FULL_REMARKS")] = None
    publish_date_ref:     Annotated[Optional[str], Field(alias="PUBLISH_DATE_REF")] = None
    editorialformbase_id: Annotated[Optional[str], Field(alias="EDITORIALFORMBASE_ID")] = None
    isindex:              Annotated[Optional[str], Field(alias="ISINDEX")] = None
    notes:                Annotated[Optional[str], Field(alias="NOTES")] = None
    available:            Annotated[bool, Field(alias="AVAILABLE")] = False

    @property
    def start_date(self) -> str | None:
        """Date of the first act recorded in this document.
        
        Returns:
            str | None: 
                - None when there is not enough data to format the date appropriatedly
                - a properly formatted string with the start date 
        """

        if self.start_day is None or self.start_month is None or self.start_year is None:
            return None
        return f"{self.start_day:02d}/{self.start_month:02d}/{self.start_year:04d}"

    @property
    def end_date(self) -> str | None:
        """Date of the last act recorded in this document.
        
        Returns:
            str | None: 
                - None when there is not enough data to format the date appropriatedly
                - a properly formatted string with the start date 
        """
        
        if self.end_day is None or self.end_month is None or self.end_year is None:
            return None
        return f"{self.end_day:02d}/{self.end_month:02d}/{self.end_year:04d}"


    @property
    def detailed_notes(self) -> str:
        """Properly formatted string with all the notes related to this document.

        Return:
            str: Properly formatted string with all the notes and remarks related to this document.
        """
        
        return "\n".join(filter(None, [self.notes, self.full_remarks]))
        
    @cached_property
    def url(self) -> Optional[str]:
        """URL where this document can be consulted (if available).
        
        Returns:
            Optional[str]: the url where a scan of this document can be consulted online (if available).
        """
        if self.available:
            return requests.get(f"{BASE_URL}/genealogie/{self.bookpart_id}").url
        else:
            return None
    
    def simplified(self) -> GenealogySearchResult:
        """Return a simplified version of this object.
        
        Returns:
            GenealogySearchResult: a simplified version of the document.
        """
        
        return GenealogySearchResult(
            description = self.description,
            start_date  = self.start_date,
            end_date    = self.end_date,
            last_update = self.book_last_modif_date,
            notes       = self.detailed_notes,
            available   = self.available,
            url         = self.url,
        )


## Definition of the actual tools
def genealogy_search_church_registers_prior_to_1796(
    municipality:      Municipality,
    parishes:          list[Parish],
    act_types:         Optional[list[ParishActType]] =  None,
    other_types:       Optional[list[OtherParishActType]] = None,
    index_types:       Optional[list[ParishIndex]] = None,
    period_selector:   Optional[PeriodSelector] = None,
    start_year:        Optional[int] = None,
    end_year:          Optional[int] = None,
) -> list[GenealogySearchResult]:
    """Search genealogic data in the Church Registers (prior to 1796).

    Args:
        municipality (Municipality): the municipality where to perform search
        parishes (list[Parish]): the parishes where to perform search
        act_types (Optional[list[ParishActType]]): The kind of document we are searching for
        other_types (Optional[list[OtherParishActType]]): Mandatory precision when act_types is OTHER
        index_types (Optional[list[ParishIndex]]): The kind of index where to search data
        period_selector (Optional[PeriodSelector]): specify how to interpret period
        start_year (Optional[int]): Start year of the period considered for this search
        end_year (Optional[int]): End year of the period considered for this search

    Note: 
        - Providing at least one 'act_types' or 'index_types' in mandatory.

    Returns: 
        list[GenealogySearchResult]: a possibly empty list of genealogical search results.

    Raises:
        requests.exceptions.RequestException: whenever something goes wrong with the search on agatha.
    """

    request_data = {
        "WHICH_TAB":         GenealogySource.CHURCH_REGISTERS.code,
        "PLACEPOINT_ID_PR" : municipality.placepoint_id,
        "PLACE_PR":          municipality.value,
        "CURRENT_NAME_PR":   municipality.current_name,
        "PARISH_ID[]":       ",".join( str(p.parish_id) for p in parishes ),
    }
    
    if act_types is not None:
        request_data["TYPEACTES_PR[]"] = ",".join( t.code for t in act_types )
    
    if other_types is not None:
        request_data["TYPEACTES_OTHER_PR[]"] = ",".join( t.code for t in other_types )

    if index_types is not None:
        request_data["TYPEINDEX_PR[]"] = ",".join( i.code for i in index_types )

    selector = period_selector if period_selector is not None else PeriodSelector.BETWEEN
    request_data["CHOOSE_DATE_PERIODE"] = selector.code

    if start_year is not None:
        request_data["exactYear"] = start_year

    if end_year is not None:
        request_data["SHOW_PERIODE"] = end_year
    
    ## search genea
    search  = requests.post(GENEA_URL, data = request_data)
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
    results = results["response"]["docs"]
    return [GenealogyDocument(**x).simplified() for x in results]

@tool(
    parse_docstring=True,
    description=
    f"""Search genealogic data in the Church Registers (prior to 1796).

    Args:
        municipality_name (str): Name of the municipality
        parish_name (Optional[str]): Name of the parish
        act_types (Optional[list[ParishActType]]): The kind of document we are searching for
            Accepted Values:
                {str(ParishActType.all_values())}
        other_types (Optional[list[OtherParishActType]]): Mandatory precision when act_types is OTHER
            Accepted Values:
                {str(OtherParishActType.all_values())}
        index_types (Optional[list[ParishIndex]]): The kind of index where to search data
            Accepted Values:
                {str(ParishIndex.all_values())}
        period_selector (Optional[PeriodSelector]): specify how to interpret period
        start_year (Optional[str]): Start year of the period considered for this search
        end_year (Optional[str]): End year of the period considered for this search

    Note: 
        - Providing at least one 'act_types' or 'index_types' in mandatory.

    Returns: 
        list[GenealogySearchResult]: a possibly empty list of genealogical search results.
    """)
def tool_genealogy_search_church_registers_prior_to_1796(
    municipality_name: str,
    parish_name:       Optional[str] = None,
    act_types:         Optional[list[ParishActType]] =  None,
    other_types:       Optional[list[OtherParishActType]] = None,
    index_types:       Optional[list[ParishIndex]] = None,
    period_selector:   Optional[PeriodSelector] = None,
    start_year:        Optional[int] = None,
    end_year:          Optional[int] = None,
) -> list[GenealogySearchResult]:
    """Search genealogic data in the Church Registers (prior to 1796).

    Args:
        municipality_name (str): Name of the municipality
        parish_name (Optional[str]): Name of the parish
        act_types (Optional[list[ParishActType]]): The kind of document we are searching for
        other_types (Optional[list[OtherParishActType]]): Mandatory precision when act_types is OTHER
        index_types (Optional[list[ParishIndex]]): The kind of index where to search data
        period_selector (Optional[PeriodSelector]): specify how to interpret period
        start_year (Optional[int]): Start year of the period considered for this search
        end_year (Optional[int]): End year of the period considered for this search

    Note: 
        - Providing at least one 'act_types' or 'index_types' in mandatory.

    Returns: 
        list[GenealogySearchResult]: a possibly empty list of genealogical search results.

    Raises:
        requests.exceptions.RequestException: whenever something goes wrong with the search on agatha.
    """

    municipality = Municipality.by_name(municipality_name, AJAX_URL, return_single_best_match=True)
    if municipality is None:
        return []
    
    parishes = municipality.parishes(AJAX_URL)

    if parish_name is not None:
        parishes = [ p for p in parishes if parish_name in p.place_name.lower() ]
    
    return genealogy_search_church_registers_prior_to_1796(
        municipality=municipality,
        parishes=parishes,
        act_types=act_types,
        other_types=other_types,
        index_types=index_types,
        period_selector=period_selector,
        start_year=start_year,
        end_year=end_year
    )


def genealogy_search_civil_state_registers(
    municipality:      Municipality | None,
    act_types:         Optional[list[CivilActType]] =  None,
    other_types:       Optional[list[OtherCivilActType]] = None,
    index_types:       Optional[list[CivilIndex]] = None,
    other_indexes:     Optional[list[OtherCivilIndex]] = None,
    period_selector:   Optional[PeriodSelector] = None,
    start_year:        Optional[int] = None,
    end_year:          Optional[int] = None,
) -> list[GenealogySearchResult]:
    """Search genealogic data in the Civil State Registers (after 1796).

    Args:
        municipality (str): The municipality where the act has happened
        act_types (Optional[list[CivilActType]]): The kind of document we are searching for
        other_types (Optional[list[OtherCivilActType]]): Mandatory precision when act_types is OTHER
        index_types (Optional[list[CivilIndex]]): The kind of index where to search data
        other_indexes (Optional[list[OtherCivilIndex]]): Mandatory precision when index_types is OTHER
        period_selector (Optional[PeriodSelector]): specify how to interpret period
        start_year (Optional[int]): Start year of the period considered for this search
        end_year (Optional[int]): End year of the period considered for this search

    Note: 
        - Providing at least one 'act_types' or 'index_types' in mandatory.

    Returns: 
        list[GenealogySearchResult]: a possibly empty list of genealogical search results.

    Raises:
        requests.exceptions.RequestException: whenever something goes wrong with the search on agatha.

    Examples:
      # start by fetching municipality and parish
      >>> sterrebeek = Municipality.by_name("sterrebeek", AJAX_URL, return_single_best_match=True)
      >>> rixensart  = Municipality.by_name("rixensart", AJAX_URL, return_single_best_match=True)
      >>> bruxelles  = Municipality.by_name("bruxelles", AJAX_URL, return_single_best_match=True)
      
      # There can be no result
      >>> res = genealogy_search_civil_state_registers(
      ...     municipality      = sterrebeek,
      ...     act_types         = [CivilActType.DEATH],
      ...     start_year        = 1948,
      ... )
      >>> sorted(res, key=lambda x: x.start_date)
      []

      # There can be one result
      >>> len(genealogy_search_civil_state_registers(
      ...     municipality      = rixensart,
      ...     act_types         = [CivilActType.BIRTH],
      ...     start_year        = 1900,
      ... ))
      1

      # There can be many (max 20)
      >>> rx = genealogy_search_civil_state_registers(
      ...     municipality      = bruxelles,
      ...     act_types         = [CivilActType.DEATH],
      ...     start_year        = 1798,
      ... )
      >>> len(rx)
      20
    """

    if municipality is None:
        return []
    
    request_data = {
        "WHICH_TAB":         GenealogySource.CIVIL_STATE.code,
        "PLACEPOINT_ID_CS" : municipality.placepoint_id,
        "PLACE_CS":          municipality.value,
        "CURRENT_NAME_CS":   municipality.current_name,
    }
    
    if act_types is not None:
        request_data["TYPEACTES_CS[]"] = ",".join( t.code for t in act_types )
    
    if other_types is not None:
        request_data["TYPEACTES_OTHER_CS[]"] = ",".join( t.code for t in other_types )

    if index_types is not None:
        request_data["TYPEINDEX_CS[]"] = ",".join( i.code for i in index_types )
    
    if other_indexes is not None:
        request_data["TYPEINDEX_OTHER_CS[]"] = ",".join(i.code for i in other_indexes)

    selector = PeriodSelector.BETWEEN if period_selector is None else period_selector
    request_data["CHOOSE_DATE_PERIODE"] = selector.code

    if start_year is not None:
        request_data["exactYear"] = start_year

    if end_year is not None:
        request_data["SHOW_PERIODE"] = end_year
    
    ## search genea
    search  = requests.post(GENEA_URL, data = request_data)
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
    results = results["response"]["docs"]
    return [GenealogyDocument(**x).simplified() for x in results]

@tool(
    parse_docstring=True,
    description=
    f"""Search genealogic data in the Civil State Registers (after 1796).

    Args:
        municipality_name (str): Name of the municipality
        act_types (Optional[list[CivilActType]]): The kind of document we are searching for
            Accepted Values:
                {str(CivilActType.all_values())}
        other_types (Optional[list[OtherCivilActType]]): Mandatory precision when act_types is OTHER
            Accepted Values:
                {str(OtherCivilActType.all_values())}
        index_types (Optional[list[CivilIndex]]): The kind of index where to search data
            Accepted Values:
                {str(CivilIndex.all_values())}
        other_indexes (Optional[list[OtherCivilIndex]]): mandatory precision when index is OTHER
            Accepted Values:
                {str(OtherCivilIndex.all_values())}
        period_selector (Optional[PeriodSelector]): specify how to interpret period
        start_year (Optional[int]): Start year of the period considered for this search
        end_year (Optional[int]): End year of the period considered for this search

    Note: 
        - Providing at least one 'act_types' or 'index_types' in mandatory.

    Returns: 
        list[GenealogySearchResult]: a possibly empty list of genealogical search results.
    """
)
def tool_genealogy_search_civil_state_registers(
    municipality_name: str,
    act_types:         Optional[list[CivilActType]] =  None,
    other_types:       Optional[list[OtherCivilActType]] = None,
    index_types:       Optional[list[CivilIndex]] = None,
    other_indexes:     Optional[list[OtherCivilIndex]] = None,
    period_selector:   Optional[PeriodSelector] = None,
    start_year:        Optional[int] = None,
    end_year:          Optional[int] = None,
) -> list[GenealogySearchResult]:
    """Search genealogic data in the Civil State Registers (after 1796).

    Args:
        municipality_name (str): Name of the municipality
        act_types (Optional[list[CivilActType]]): The kind of document we are searching for
        other_types (Optional[list[OtherCivilActType]]): Mandatory precision when act_types is OTHER
        index_types (Optional[list[CivilIndex]]): The kind of index where to search data
        other_indexes (Optional[list[OtherCivilIndex]]): mandatory precision when index is OTHER
        period_selector (Optional[PeriodSelector]): specify how to interpret period
        start_year (Optional[int]): Start year of the period considered for this search
        end_year (Optional[int]): End year of the period considered for this search

    Note: 
        - Providing at least one 'act_types' or 'index_types' in mandatory.

    Returns: 
        list[GenealogySearchResult]: a possibly empty list of genealogical search results.

    Raises:
        requests.exceptions.RequestException: whenever something goes wrong with the search on agatha.

    Examples:
      # There can be no result
      >>> res = genealogy_search_civil_state_registers(
      >>>     municipality_name = "sterrebeek",
      >>>     act_types         = [CivilActType.DEATH],
      >>>     start_year        = 1948,
      >>> )
      >>> sorted(res, key=lambda x: x.start_date)
      []

      # There can be one result
      >>> genealogy_search_civil_state_registers(
      >>>     municipality_name = "rixensart",
      >>>     act_types         = [CivilActType.BIRTH],
      >>>     start_year        = 1900,
      >>> )
      [GenealogySearchResult(
          description='Birth certificates', 
          start_date='01/01/1894', 
          end_date='31/12/1912',
          ...),
      ]

      # There can be many (max 20)
      >>> rx = genealogy_search_civil_state_registers(
      >>>     municipality_name = "bruxelles",
      >>>     act_types         = [CivilActType.DEATH],
      >>>     start_year        = 1798,
      >>> )
      >>> len(rx)
    """
    
    municipality = Municipality.by_name(municipality_name, AJAX_URL, return_single_best_match=True)
    return genealogy_search_civil_state_registers(
        municipality=municipality,
        act_types=act_types,
        other_types=other_types,
        index_types=index_types,
        other_indexes=other_indexes,
        period_selector=period_selector,
        start_year=start_year,
        end_year=end_year,
    )
    