"""Data types to implement the search person in analyses of records tool call."""

from ..common.schemas import SearchAnalysesState


class FreeSearchWizzardState(SearchAnalysesState, total=False):
    """The internal state of the wizzard process to create a free search request.

    Attributes:
        search_terms (str): Keyword(s) to define the search: e.g. person, building, object, place, etc.
    """

    search_terms: str

