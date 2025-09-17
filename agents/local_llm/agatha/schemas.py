"""Data types to implement the overarching AGATHA interactions workflow."""

from enum import StrEnum


class AgathaSearchEngine(StrEnum):
    """Which search engine do you wish to consult on AGATHA ?
    
    Attributes:
        GENEALOGY (str): when you want to search for scans of documents in the
            genealogic sources of the state archives
        ANALYSES (str): when your goal is to search in the analysed records 
            in order to find a specific act.
    """

    GENEALOGY = "GENEALOGY"
    ANALYSES = "ANALYSES"

    @classmethod
    def all_values(cls) -> list[str]:
        """Return all possible values for this enumerated type.
        
        Returns:
            list[str]: all possible values for this enum.
        """

        return [m._value_ for m in cls.__members__.values()]
