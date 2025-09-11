"""Data types to implement the genealogical search workflow."""

from pydantic import BaseModel

from ....tools.agatha_common import Parish
from ....tools.genealogy import OtherParishActType, ParishActType, ParishIndex
from ..common.schemas import GeneaSearchState


class StrList(BaseModel):
    """list of strings.
    
    Attributes:
        lst (list[str]): list of strings
    """

    lst: list[str]


class SearchChurchRegisterState(GeneaSearchState, total=False):
    """Genea search in church registers prior to 1796.
    
    Attributes:
        parish (str): the parish where the act has happened
    """

    parish: list[Parish]
    act_types: list[ParishActType]
    other_act_types: list[OtherParishActType]
    indexes: list[ParishIndex]
