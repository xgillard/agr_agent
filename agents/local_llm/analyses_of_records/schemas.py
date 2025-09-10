"""Datatypes to implement the search in analyses of records"""

from enum import StrEnum

from pydantic import BaseModel


class AnalysesOfRecordsTool(StrEnum):
    """An enum to triage the requests to the appropriate tool.
    
    Attributes:
        SEARCH_PERSON (str): search person tab, aka precise, targeted search
        FREE_SEARCH (str): free search tab to perform a broad general search
    """

    SEARCH_PERSON = "search-person"
    FREE_SEARCH = "free-search"

    @classmethod
    def all_values(cls) -> list[str]:
        """Return all possible values of this enum.
        
        Returns: 
            list[str]: all possible values for this enumeration
        """
        
        return [ v._value_ for v in cls.__members__.values() ]
    
class TriageChoice(BaseModel):
    """The choice for a triage
    
    Attribute:
        choice (AnalysesOfRecordsTool): the choice
    """

    choice: AnalysesOfRecordsTool