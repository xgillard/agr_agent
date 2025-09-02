"""Common types and datastructures to interact with AGATHA.

Date: 2025-09-02
Author: X. Gillard
"""

from enum import StrEnum
from typing import Annotated, Literal, Optional, Self, overload

import requests
from pydantic import BaseModel, ConfigDict, Field
from textdistance import levenshtein


class PeriodSelector(StrEnum):
    """Precision regarding to how a pair of start / end dates should be interpreted.

    Attributes:
        EXACT_DATE (str): When you want to expecify that the start date is an exact date.
            (eg: something happened 'the 1918-12-25').
        BETWEEN (str): When you want the pair of dates to be considered like an interval.
            (eg: somehting happened 'between 1918-12-25 and 1986-04-28').
        BEFORE (str): When you want the start date to be interpreted as an upper bound
            on the date of the document you would like to find
        AFTER (str): When you want the start date to be interpreted as a lower bound
            on the date of the document you would like to find
    """

    EXACT_DATE = "exact"
    BETWEEN    = "between"
    BEFORE     = "before"
    AFTER      = "after"

    @property
    def code(self) -> str:
        """The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        """

        match self:
            case PeriodSelector.EXACT_DATE:
                return "0"
            case PeriodSelector.BETWEEN:
                return "1"
            case PeriodSelector.BEFORE:
                return "2"
            case PeriodSelector.AFTER:
                return "3"


class Parish(BaseModel):
    """A parish identified within a community

    Attributes:
        parish_id (int): The technical identifier used to reference the parish
        place_name (str): The name of the parish
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

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

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    label: str
    value: str
    current_name: Annotated[str, Field(alias="CURRENT_NAME")]
    placepoint_id: Annotated[int, Field(alias="PLACEPOINT_ID")]
    parishes_id: Annotated[int | None, Field(alias="PARISHES_ID")] = None

    # stub for the usual case
    @overload
    @classmethod
    def by_name(cls, name: str, ajax: str, return_single_best_match: Literal[False] = False) -> list[Self]: ...

    # stub for the return single_best_match case
    @overload
    @classmethod
    def by_name(cls, name: str, ajax: str, return_single_best_match: Literal[True]) -> Optional[Self]: ...
    
    @classmethod
    def by_name(cls, name: str, ajax: str, return_single_best_match: bool=False) -> list[Self] | Optional[Self]:
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
            ajax (str): The url of the ajax service to use to perform the lookup on AGATHA.
            return_single_best_match (bool): A flag indicating whether this method should
                yield all matches corresponding to the search term, or if it should return
                one single Municipality whose name is the closest to the search term.

        Returns:
            list[Self] | Optional[Self]: 
                - A list of municipality matching the given name (when `return_single_best_match` is False).
                - A single `Municipality` object or `None` when `return_single_best_match` is True.

        Example:
            >>> ajax = "https://agatha.arch.be/search/genealogie/ajax.php"
            # the name need not be a full match
            >>> Municipality.by_name("sterre", ajax=ajax)
            [Municipality(label='Sterrebeek (Zaventem)', ...)]
            
            # it can return multiple matches
            >>> result = Municipality.by_name("zaventem", ajax=ajax)
            >>> sorted(result, key=lambda x: x.label)
            [Municipality(label='Nossegem (Zaventem)', ...,
             Municipality(label='Sint-Stevens-Woluwe (Zaventem)', ...),
             Municipality(label='Sterrebeek (Zaventem)', ...),
             Municipality(label='Zaventem', ...),]

            # there can be zero matches if the search term corresponds to nothing
            >>> result = Municipality.by_name("nondidju", ajax=ajax)
            []

            # When the return_single_best_match flag is set, it returns only one municipality
            >>> Municipality.by_name("sterre", ajax=ajax, return_single_best_match=True)
            Municipality(label='Sterrebeek (Zaventem)', ...)

            # When the return_single_best_match flag is set, it returns only one municipality
            # even when there are multiple possible matches
            >>> Municipality.by_name("zaventem", ajax=ajax, return_single_best_match=True)
            Municipality(label='Zaventem', ...)

            # When the return_single_best_match flag is set and there is no match
            # corresponding to the search term, then the method will return None
            >>> Municipality.by_name("nondidju", ajax=ajax, return_single_best_match=True)
            None
        """
        
        r = requests.post(ajax, data = {
            "method": "getMunicipalities",
            "term"  : name,   # location qu'on veut trouver
        })
        results = [ Municipality(**x) for x in r.json() ]
        if return_single_best_match:
            return min(results, key = lambda x: levenshtein(x.label, name)) if results else None # type: ignore[return-value]
        else:
            return results # type: ignore[return-value]

    def parishes(self, ajax: str) -> list[Parish]:
        """Return list of known parishes in this municipality.

        Args:
            ajax (str): The url of the ajax service to use to perform the lookup on AGATHA.

        Returns:
            list[Parish]: the list of known parishes in this municipality.

        Examples:
            >>> ajax = "https://agatha.arch.be/search/genealogie/ajax.php"
            # There can be one result
            >>> Municipality.by_name("sterre", ajax=ajax, return_single_best_match=True).parishes(ajax)
            [Parish(...)]

            # or there can be many
            >>> Municipality.by_name("bruxelles", ajax=ajax, return_single_best_match=True).parishes(ajax)
            [Parish(...)]
        """
        
        r = requests.post(ajax, data = {
            "method":        "getParishFromMunicipality",
            "PLACEPOINT_ID": self.placepoint_id,
        })
        return [ Parish(**x) for x in r.json() ]

