"""Datatypes for a research in the genealogical sources."""

from pydantic import BaseModel

from ....tools.agatha_common import Municipality
from ...common.schemas import AgathaToolState


class Choices[Choice](BaseModel):
    """A generic choice
    
    Attributes:
        choices (list[Choice]): the chosen options
    """

    choices: list[Choice]

    def options(self) -> list[Choice]:
        return self.choices


class GeneaSearchState(AgathaToolState, total=False):
    """Base state for a workflow to search in genealogical sources.

    Attributes:
        municipality (str): the municipality whose registers need to be 
            searched
    """
    
    municipality: Municipality