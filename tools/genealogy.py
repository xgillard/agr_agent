"""A set of tools that implement research in genealogical sources."""

from enum import StrEnum
from functools import cached_property
from typing import Annotated, Literal, Optional, Self, overload

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from textdistance import levenshtein

## Constants
BASE_URL  = "https://agatha.arch.be/search"
AJAX_URL  = f"{BASE_URL}/genealogie/ajax.php"
GENEA_URL = f"{BASE_URL}/genealogie/results/"

## 
class Parish(BaseModel):
    """A parish identified within a community

    Attributes:
        parish_id (int): The technical identifier used to reference the parish
        place_name (str): The name of the parish
    """

    parish_id: Annotated[int, Field(alias="PARISH_ID")]
    place_name:   Annotated[str, Field(alias="PLACE_NAME")]


class Municipality(BaseModel):
    """All the technical data used to retrieve a given municipality.
    
    Attributes:
        label (str): How this municipality should be displayed
        value (str): Name that should be used when referencing this municipality
        current_name (str): The current denomination of this municipality
        placepoint_id (int): The effective identifier of this municipality
        parishes_id (int | None): If present, the id of the parish in the municipality
    """

    label: str
    value: str
    current_name: Annotated[str, Field(alias="CURRENT_NAME")]
    placepoint_id: Annotated[int, Field(alias="PLACEPOINT_ID")]
    parishes_id: Annotated[int | None, Field(alias="PARISHES_ID")] = None

    # stub for the usual case
    @overload
    @classmethod
    def by_name(cls, name: str, return_single_best_match: Literal[False] = False) -> list[Self]: ...

    # stub for the return single_best_match case
    @overload
    @classmethod
    def by_name(cls, name: str, return_single_best_match: Literal[True]) -> Optional[Self]: ...
    
    @classmethod
    def by_name(cls, name: str, return_single_best_match: bool=False) -> list[Self] | Optional[Self]:
        """Find municipality data by name.

        Retrieves the municipalities matching the given search name and returns them
        as a list of Municipalities. If the `return_single_best_match` flag is set `True`,
        then this method is guaranteed to return at most one single Municipality whose
        `label` field is the closest to the search name (as per levensthein distance).

        When there is no satisfying match for the given search term, this method will
        return an empty list. If however, the `return_single_best_match` flag is set, 
        then the method will return None instead of an empty list.
        
        Arguments:
            name (str): The name of the municipality we'd like to retrieve.
            return_single_best_match (bool): A flag indicating whether this method should
                yield all matches corresponding to the search term, or if it should return
                one single Municipality whose name is the closest to the search term.

        Returns:
            list[Self] | Optional[Self]: 
                - A list of municipality matching the given name (when `return_single_best_match` is False).
                - A single `Municipality` object or `None` when `return_single_best_match` is True.

        Example:
            # the name need not be a full match
            >>> Municipality.by_name("sterre")
            [Municipality(label='Sterrebeek (Zaventem)', ...)]
            
            # it can return multiple matches
            >>> result = Municipality.by_name("zaventem")
            >>> sorted(result, key=lambda x: x.label)
            [Municipality(label='Nossegem (Zaventem)', ...,
             Municipality(label='Sint-Stevens-Woluwe (Zaventem)', ...),
             Municipality(label='Sterrebeek (Zaventem)', ...),
             Municipality(label='Zaventem', ...),]

            # there can be zero matches if the search term corresponds to nothing
            >>> result = Municipality.by_name("nondidju")
            []

            # When the return_single_best_match flag is set, it returns only one municipality
            >>> Municipality.by_name("sterre", return_single_best_match=True)
            Municipality(label='Sterrebeek (Zaventem)', ...)

            # When the return_single_best_match flag is set, it returns only one municipality
            # even when there are multiple possible matches
            >>> Municipality.by_name("zaventem", return_single_best_match=True)
            Municipality(label='Zaventem', ...)

            # When the return_single_best_match flag is set and there is no match
            # corresponding to the search term, then the method will return None
            >>> Municipality.by_name("nondidju", return_single_best_match=True)
            None
        """
        
        r = requests.post(AJAX_URL, data = {
            "method": "getMunicipalities",
            "term"  : name,   # location qu'on veut trouver
        })
        results = [ Municipality(**x) for x in r.json() ]
        if return_single_best_match:
            return min(results, key = lambda x: levenshtein(x.label, name)) if results else None # type: ignore[return-value]
        else:
            return results # type: ignore[return-value]

    @cached_property
    def parishes(self) -> list[Parish]:
        """Return list of known parishes in this municipality.

        Returns:
            list[Parish]: the list of known parishes in this municipality.

        Examples:
            # There can be one result
            >>> Municipality.by_name("sterre", return_single_best_match=True).parishes
            [Parish(...)]

            # or there can be many
            >>> Municipality.by_name("bruxelles", return_single_best_match=True).parishes
            [Parish(...)]
        """
        
        r = requests.post(AJAX_URL, data = {
            "method":        "getParishFromMunicipality",
            "PLACEPOINT_ID": self.placepoint_id,
        })
        return [ Parish(**x) for x in r.json() ]

## 
class GenealogySource(StrEnum):
    """The possible sources of genealogical acts.

    Attributes:
        CHURCH_REGISTERS (str): Church register prior to 1796
        CIVIL_STATE (str): Civil State for ther records posterior to 1796
    """
    
    CHURCH_REGISTERS = "church"
    CIVIL_STATE      = "civil"
    
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



## Types relating to a genealogical search within church registers
class ParishActType(StrEnum):
    """The kind of act documents that can be found in church registers prior to 1796.

    Attributes:
        BAPTISM (str): birth or baptism certificate
        WEDDING (str): wedding certificate
        DEATH (str): funeral / death certificate
        OTHER (str): other kind of documents
    """
    
    BAPTISM = "baptism"
    WEDDING = "wedding"
    DEATH   = "death"
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
    
    MARRIAGE_EXEMPTION  = "marriage::exemption"
    MARRIAGE_IMPEDIMENT = "marriage::impediment"
    LIST_OF_COMMUNIANTS = "communiants"
    LIST_OF_CONFIRMANDS = "confirmands"
    LIST_OF_NAMES       = "names"
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
        

class ParishIndex(StrEnum):
    """Possible indexes where to look up documents in the church registers (prior to 1796).

    Attributes:
        BAPTISM (str): Birth or baptism certificates
        WEDDING (str): Wedding certificates
        DEATH   (str): Death / funeral certificates
    """
    
    BAPTISM = "baptism"
    WEDDING = "wedding" 
    DEATH   = "death"

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


## Types relating to a genealogical search within civil registers
class CivilActType(StrEnum):
    """The kind of documents that can be found in Civil State registers after 1796.

    Attributes:
        BIRTH   (str): Birth certificates
        WEDDING (str): Wedding certificates
        DEATH   (str): Death certificates
        OTHER   (str): Other kind of documents
    """
    
    BIRTH   = "birth"
    WEDDING = "wedding"
    DEATH   = "death"
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


class OtherCivilActType(StrEnum):
    """Precision regarding what 'other' documents should be searched in the civil state registers.

    Attributes:
        ADDITIONAL_REGISTER (str): Additional register (Supplement to a register containing 
                                   exhibited documents (extracts) or notes.)
        ADOPTION            (str): Adoption certificates (Certificate by which a court or authority establishes 
                                   a legal direct relationship between persons who are not blood relatives.)
        DEATH_ANNEXES       (str): Death annexes (Extracts of deaths abroad or death declarations of missing persons 
                                   (after the World Wars) attached to death certificates.)
        DIVORCE             (str): Divorce certificates (Certificate of the termination of marriage.).
        NATURALISATION      (str): Naturalisation certificates (Certificate by which a court or authority grants 
                                   nationality to a person). 
    """
    
    ADDITIONAL_REGISTER = "additional"
    ADOPTION            = "adoption"
    DEATH_ANNEXES       = "death-annexes"
    DIVORCE             = "divorce"
    NATURALISATION      = "naturalisation"

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

class CivilIndex(StrEnum):
    """Possible indexes where to look up documents in the civil state registers (after 1796).

    Attributes:
        ANNUAL_INDEX_OF_DIVORCE (str): Annual index of divorce certificates
        ANNUAL_INDEX_OF_NATURALISATION (str): Annual index of naturalisation certificates
        ANNUAL_INDEX_OF_ADDITIONAL_REGISTER (str): Index of additional register
        DECENNAL_INDEX_OF_ADOPTION (str): Ten-year index of adoption certificates
        DECENNAL_INDEX_OF_DIVORCE (str): Ten-year index of divorce certificates
        DECENNAL_INDEX_OF_NATURALISATION (str): Ten-year index of naturalisation certificates
    """
    
    ANNUAL_INDEX_OF_DIVORCE             = "divorce::annual"
    ANNUAL_INDEX_OF_NATURALISATION      = "naturalization::annual"
    ANNUAL_INDEX_OF_ADDITIONAL_REGISTER = "additional::annual"
    DECENNAL_INDEX_OF_ADOPTION          = "adoption::10years"
    DECENNAL_INDEX_OF_DIVORCE           = "divorce::10years"
    DECENNAL_INDEX_OF_NATURALISATION    = "naturalization::10years"

    @property
    def code(self) -> str:
        """The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        """

        match self:
            case CivilIndex.ANNUAL_INDEX_OF_DIVORCE:
                return "BS_Ei"
            case CivilIndex.ANNUAL_INDEX_OF_NATURALISATION:
                return "BS_Ni"
            case CivilIndex.ANNUAL_INDEX_OF_ADDITIONAL_REGISTER:
                return "BS_Ui"
            case CivilIndex.DECENNAL_INDEX_OF_ADOPTION:
                return "BS_Ax"
            case CivilIndex.DECENNAL_INDEX_OF_DIVORCE:
                return "BS_Ex"
            case CivilIndex.DECENNAL_INDEX_OF_NATURALISATION:
                return "BS_Nx"


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
        bookpart_id          (str):           Identifier that is used to retrieve the actual document scan
        bookpartplace_id     (str):           I don't know what this means
        new_municipalities   (Optional[str]): New municipality name (after merge)
        old_municipalities   (Optional[str]): Municipality name (before they were merged)
        place_name           (Optional[str]): Parish name (if relevant)
        full_parish_name     (Optional[str]): Full parish name (if relevant)
        start_day            (Optional[int]): Date of the first act recorded in this document (day)
        start_month          (Optional[int]): Date of the first act recorded in this document (month)
        start_year           (Optional[int]): Date of the first act recorded in this document (year)
        end_day              (Optional[int]): Date of the last act recorded in this document (day)
        end_month            (Optional[int]): Date of the last act recorded in this document (month)
        end_year             (Optional[int]): Date of the last act recorded in this document (year)
        book_last_modif_date (Optional[str]): Date when this archive was last modified
        description          (Optional[str]): Description
        full_remarks         (Optional[str]): Remarks wrt the document (e.g. missing)
        publish_date_ref     (Optional[str]): Date when this archive was published
        editorialformbase_id (Optional[str]): Identifier of the document type
        isindex              (Optional[str]): Does it come from an index
        notes                (Optional[str]): Additional notes regarding this document
        available            (Optional[bool]): Is the document available for online consultation
    """
    
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
@tool
def genealogy_search_church_registers_prior_to_1796(
    municipality_name: str,
    parish_name:       Optional[str] = None,
    act_types:         Optional[list[ParishActType]] =  None,
    other_types:       Optional[list[OtherParishActType]] = None,
    index_types:       Optional[list[ParishIndex]] = None,
    start_year:        Optional[int] = None,
    end_year:          Optional[int] = None,
) -> list[GenealogySearchResult]:
    """Search genealogic data in the Church Registers (prior to 1796).

    Args:
        municipality_name (str):                           Name of the municipality
        parish_name (Optional[str]):                       Name of the parish
        act_types   (Optional[list[ParishActType]]):       The kind of document we are searching for
        other_types (Optional[list[OtherParishActType]]):  Mandatory precision when act_types is OTHER
        index_types (Optional[list[ParishIndex]]):         The kind of index where to search data
        start_year  (Optional[int]):                       Start year of the period considered for this search
        end_year    (Optional[int]):                       End year of the period considered for this search

    Note: 
        - Providing at least one 'act_types' or 'index_types' in mandatory.

    Returns: 
        list[GenealogySearchResult]: a possibly empty list of genealogical search results.

    Raises:
        requests.exceptions.RequestException: whenever something goes wrong with the search on agatha.

    Examples:
      # There can be one result
      >>> genealogy_search_church_registers_prior_to_1796(
      >>>     municipality_name = "sterrebeek",
      >>>     act_types         = [ParishActType.DEATH],
      >>>     start_year        = 1795,
      >>> )
      [GenealogySearchResult(
          description='Funeral and death certificates', 
          start_date='01/01/1793', 
          end_date='31/12/1796', 
          ...),
      ]

      # or there can be many
      >>> res = genealogy_search_church_registers_prior_to_1796(
      >>>     municipality_name = "sterrebeek",
      >>>     act_types         = [ParishActType.BAPTISM],
      >>>     start_year        = 1790,
      >>> )
      >>> sorted(res, key=lambda x: x.start_date)
      [
        GenealogySearchResult(start_date='02/01/1791', end_date='17/12/1791', ...), 
        GenealogySearchResult(start_date='02/01/1793', end_date='18/12/1793', ...), 
        GenealogySearchResult(start_date='05/01/1790', end_date='22/12/1790', ...), 
        GenealogySearchResult(start_date='16/01/1796', end_date='12/12/1796', ...), 
        GenealogySearchResult(start_date='18/01/1792', end_date='23/12/1792', ...), 
        GenealogySearchResult(start_date='29/01/1778', end_date='08/10/1796', ...), 
      ]

    """
    municipality = Municipality.by_name(municipality_name, return_single_best_match=True)
    if municipality is None:
        return []
    
    parishes = municipality.parishes

    if parish_name is not None:
        parishes = [ p for p in parishes if parish_name in p.place_name.lower() ]
    
    #
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

    if start_year is not None:
        request_data["exactYear"] = start_year
        request_data["CHOOSE_DATE_PERIODE"] = "1"

    if end_year is not None:
        request_data["SHOW_PERIODE"] = end_year
        request_data["CHOOSE_DATE_PERIODE"] = "1"
    
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


@tool
def genealogy_search_civil_state_registers(
    municipality_name: str,
    act_types:         Optional[list[CivilActType]] =  None,
    other_types:       Optional[list[OtherCivilActType]] = None,
    index_types:       Optional[list[CivilIndex]] = None,
    start_year:        Optional[int] = None,
    end_year:          Optional[int] = None,
) -> list[GenealogySearchResult]:
    """Search genealogic data in the Civil State Registers (after 1796).

    Args:
        municipality_name (str):                          Name of the municipality
        parish_name (Optional[str]):                      Name of the parish
        act_types   (Optional[list[CivilActType]]):       The kind of document we are searching for
        other_types (Optional[list[OtherCivilActType]]):  Mandatory precision when act_types is OTHER
        index_types (Optional[list[CivilIndex]]):         The kind of index where to search data
        start_year  (Optional[int]):                      Start year of the period considered for this search
        end_year    (Optional[int]):                      End year of the period considered for this search

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
    municipality = Municipality.by_name(municipality_name, return_single_best_match=True)
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

    if start_year is not None:
        request_data["exactYear"] = start_year
        request_data["CHOOSE_DATE_PERIODE"] = "1"

    if end_year is not None:
        request_data["SHOW_PERIODE"] = end_year
        request_data["CHOOSE_DATE_PERIODE"] = "1"
    
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

