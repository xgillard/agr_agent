"""Datatypes for a research in the genealogical sources."""

from ....tools.agatha_common import Municipality
from ...common.schemas import AgathaToolState


class GeneaSearchState(AgathaToolState, total=False):
    """Base state for a workflow to search in genealogical sources.

    Attributes:
        municipality (str): the municipality whose registers need to be 
            searched
    """
    
    municipality: Municipality