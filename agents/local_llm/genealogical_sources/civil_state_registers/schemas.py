"""Data types to implement the genealogical search workflow."""

from ....tools.genealogy import (
    CivilActType,
    CivilIndex,
    OtherCivilActType,
    OtherCivilIndex,
)
from ..common.schemas import GeneaSearchState


class SearchCivilRegisterState(GeneaSearchState, total=False):
    """Genea search in civil registers posterior to 1796."""

    act_types: list[CivilActType]
    other_act_types: list[OtherCivilActType]
    indexes: list[CivilIndex]
    other_indexes: list[OtherCivilIndex]
