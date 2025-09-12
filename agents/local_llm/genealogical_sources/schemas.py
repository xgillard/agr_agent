"""Datatypes to implement the search in genealogical sources"""

from enum import StrEnum

from pydantic import BaseModel


class GeneaTool(StrEnum):
    """An enum to triage the requests to the appropriate tool.
    
    Attributes:
        CHURCH_REGISTERS (str): search in church registers for documents prior to 1796
        CIVIL_STATE_REGISTERS (str): search in persons registers for documents after 1796.
    """

    CHURCH_REGISTERS = "church"
    CIVIL_STATE_REGISTERS = "civil"

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
        choice (GeneaTool): the choice
    """

    choice: GeneaTool