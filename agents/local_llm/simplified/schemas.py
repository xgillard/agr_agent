"""data to sumup the available information."""

from typing import (
    Any,
)

from langgraph.graph import (
    MessagesState,
)
from pydantic import (
    BaseModel,
)

from ...tools.generated import (
    AnalysesActRole,
    AnalysesActType,
)

ACT_TYPE_OPENS_GENEA_CHURCH = [
    # map to baptism
    AnalysesActType.BIRTH_CERTIFICATES,
    AnalysesActType.BAPTISM_CERTIFICATES,
    AnalysesActType.BIRTH_ANNOUNCEMENT,
    # map to marriage
    AnalysesActType.NOTICES_OF_MARRIAGE,
    AnalysesActType.MARRIAGE_ANNOUNCEMENTS,
    AnalysesActType.MARRIAGE_CERTIFICATES,
    AnalysesActType.MARRIAGE_SETTLEMENT,
    # map to death
    AnalysesActType.FUNERAL_CERTIFICATES,
    AnalysesActType.DEATH_CERTIFICATES,
    AnalysesActType.DEATH_NOTICE,
    AnalysesActType.MORTUARY_AND_MOURNING_CARD,
    AnalysesActType.MORTUARY_INVENTORY,
]
ACT_TYPE_OPENS_GENEA_CIVIL = [
    # map to baptism
    AnalysesActType.BIRTH_CERTIFICATES,
    AnalysesActType.BIRTH_ANNOUNCEMENT,
    # map to marriage
    AnalysesActType.NOTICES_OF_MARRIAGE,
    AnalysesActType.MARRIAGE_ANNOUNCEMENTS,
    AnalysesActType.MARRIAGE_CERTIFICATES,
    AnalysesActType.MARRIAGE_SETTLEMENT,
    # map to death
    AnalysesActType.FUNERAL_CERTIFICATES,
    AnalysesActType.DEATH_CERTIFICATES,
    AnalysesActType.DEATH_NOTICE,
    AnalysesActType.MORTUARY_AND_MOURNING_CARD,
    AnalysesActType.MORTUARY_INVENTORY,
    AnalysesActType.JUDICIAL_DEATH_DECLARATION,
]

ONLINE_HELP_ID    = "Online Help Resources"
ONLINE_HELP_DESCR = """
    * 'Online Help Resources' that will let you search in 
        the user manuals and FAQ sections of the AGATHA platform. 
        This is mostly useful to answer *HOW DO I ...* questions.
"""

ANALYSES_FREE_SEARCH_ID = "Analyses of Records / Free Search"
ANALYSES_FREE_SEARCH_DESCR = """
    * 'Analyses of Records / Free Search': this will let you 
        perform a fulltext search to retrieve documents based
        on their content.
        
        Each result entry provides the following information: 

            - act_id (str): globally unique identifier of this administrative act
            - act_number (Optional[str]): act number that was used by the archive producer
            - project (AnalysesProject): the project that led to the analysis of this record
            - actplace (Optional[str]): the place where this act officially happened
            - parish (Optional[str]): the parish where this act officially happened (if relevant)
            - editorial_form (str): the type of document
            - description (str): a brief description of this document
            - act_date (str): the date when this administrative act actually took place.
            - remarks (str): some remarks about this act
            - persons (list[AnalysesPerson]): people mentioned in the document.
"""

ANALYSES_SEARCH_PERSON_ID = "Analyses of Records / Search Person"
ANALYSES_SEARCH_PERSON_DESCR = """
    * 'Analyses of Records / Search Person': this will let you retrieve documents by placing
        criterion on the people who were mentioned in the documents, their names, profession,
        and roles.
        
        Each result entry provides the following information: 

            - act_id (str): globally unique identifier of this administrative act
            - act_number (Optional[str]): act number that was used by the archive producer
            - project (AnalysesProject): the project that led to the analysis of this record
            - actplace (Optional[str]): the place where this act officially happened
            - parish (Optional[str]): the parish where this act officially happened (if relevant)
            - editorial_form (str): the type of document
            - description (str): a brief description of this document
            - act_date (str): the date when this administrative act actually took place.
            - remarks (str): some remarks about this act
            - persons (list[AnalysesPerson]): people mentioned in the document.
"""

GENEA_CHURCH_ID = "Genealogical sources / Church Registers"
GENEA_CHURCH_DESCR = """
    * 'Genealogical sources / Church Registers': this will let you find digitized scans of 
        the original church registers where official acts have been consigned prior to 1796. 
        This is often helpful in order to find the scan of a specific act. 
    
        Each result entry provides the following information: 

            - description (str): Description of the document.
            - start_date (str): Day of the first act recorded in this document
            - end_date (str): Day of the last act recorded in 
            - last_update (str): Date when this archive was last modified
            - notes (str): Remarks and notes about this document
            - available (bool): Is this document available for online consultation
            - url (Optional[str]): URL where this document can be consulted (if available)
"""

GENEA_CIVIL_ID = "Genealogical sources / Civil State Registers"
GENEA_CIVIL_DESCR = """
    * 'Genealogical sources / Civil State Registers': this will let you find digitized scans of 
        the original civil state registers where official acts have been consigned since 1796. 
        This is often helpful in order to find the scan of a specific act. 
    
        Each result entry provides the following information: 

            - description (str): Description of the document.
            - start_date (str): Day of the first act recorded in this document
            - end_date (str): Day of the last act recorded in 
            - last_update (str): Date when this archive was last modified
            - notes (str): Remarks and notes about this document
            - available (bool): Is this document available for online consultation
            - url (Optional[str]): URL where this document can be consulted (if available)
"""

class PersonData(BaseModel):
    """Data about a person.
    
    Attributes:
        first_name (str | None): first name of the person
        family_name (str | None): family name of the person
        profession (str | None): profession 
        role (AnalysesActRole | None): role played in the events
    """

    first_name: str | None = None
    family_name: str | None = None
    profession: str | None = None
    role: AnalysesActRole | None = None

    def __bool__(self) -> bool:
        """Computes a truth value for people"""

        return bool(self.family_name) or bool(self.first_name)


class AvailableData(BaseModel):
    """This class is meant to formalize the useful available information about a user's request.
    
    Attributes:
        municipality_name (str | None): the name of the municipality where events have happened
        parish_name (str | None): name of the parish where the events happened
        type_of_record (AnalysesActType | None): the type of document we wish to retrieve
        from_year (int | None): start of the date range we want to consider when searching our doc
        until_year (int | None): end of the date range we want to consider when searching our doc
        people (list[PersonData] | None): a list of persons who are involved in the act
    """
    
    municipality_name: str | None = None
    parish_name: str | None = None
    type_of_record: AnalysesActType | None = None
    from_year: int | None = None
    until_year: int | None = None
    people: list[PersonData] | None = None

    def _can_use_genea_church(self) -> bool:
        """Return 'Search Genealogical Sources / Church Registers' can be used."""

        return (
            bool(self.municipality_name) 
            and (self.type_of_record in ACT_TYPE_OPENS_GENEA_CHURCH)
        )
    
    def _can_use_genea_civil(self) -> bool: 
        """Return 'Search Genealogical Sources / Civil State Registers' can be used."""

        return (
            bool(self.municipality_name) 
            and (self.type_of_record in ACT_TYPE_OPENS_GENEA_CIVIL)
        )
    
    def _can_use_analyses_free_search(self) -> bool:
        """Return true, "Analyses of Records / Free Search" can always be used."""
        
        return True
    
    def _can_use_analyses_search_person(self) -> bool:
        """Return true when "Analyses of Records / Search Person" can be used."""

        return (
            bool( [p for p in self.people if bool(p) ]) if self.people else False
        )
    
    def _can_use_help_resources(self) -> bool:
        """Return true as using the manual is always allowed."""

        return True
    
    def available_tools(self) -> tuple[str, list[str]]:
        """Retrurn a description and names of the tools that can be used.

        Returns: 
            tuple[str, list[str]]:
                the 1st item in the tuple is the description of the tools
                the 2nd item in the tuple is the list of tool names.
        """
        tools = []
        descr = "\nYou have acces to the following resources:\n"
        if self._can_use_help_resources():
            descr += ONLINE_HELP_DESCR
            tools.append(ONLINE_HELP_ID)
        
        if self._can_use_analyses_free_search():
            descr += ANALYSES_FREE_SEARCH_DESCR
            tools.append(ANALYSES_FREE_SEARCH_ID)
        
        if self._can_use_analyses_search_person():
            descr += ANALYSES_SEARCH_PERSON_DESCR
            tools.append(ANALYSES_SEARCH_PERSON_ID)

        if self._can_use_genea_church():
            descr += GENEA_CHURCH_DESCR
            tools.append(GENEA_CHURCH_ID)
        
        if self._can_use_genea_civil():
            descr += GENEA_CIVIL_DESCR
            tools.append(GENEA_CIVIL_ID)

        return (descr, tools)
    
    @staticmethod
    def all_tools() -> str:
        """Return the description and use of all the available tools."""

        descr = "\nYou are allowed to use the following tools:\n"

        descr += ONLINE_HELP_DESCR
        descr += ANALYSES_FREE_SEARCH_DESCR
        descr += ANALYSES_SEARCH_PERSON_DESCR
        descr += GENEA_CHURCH_DESCR
        descr += GENEA_CIVIL_DESCR
        #descr += "\n\nNote: Some tools might be unavailable depending on your search criteria.\n"
        
        return descr

class AgentState(MessagesState):
    """State of the agent.
    
    Attributes:
        input (str): the user's request.
        scratch (str): the agent' scratchpad where all it knows its explicited.

        thought (str): the current thought (will be appended to scratchpad eventually)
        
        call_tool (str): the name of the tool to be called.
        call_request (Any): the request sent to the tool.
        call_data (Any): the outcome of a tool call
        
        n (int): the number of erroneous tool calls.
    """

    input: str
    available_data: AvailableData
    scratch: str

    thought: str

    call_tool: str
    call_request: Any
    call_data: Any

    n: int