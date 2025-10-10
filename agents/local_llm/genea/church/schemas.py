from typing import (
    Literal,
    TypeAlias,
)

from pydantic import (
    BaseModel,
)

from ....tools.genealogy import (
    OtherParishActType,
    ParishActType,
)
from ...agatha.schemas import (
    AgentState,
)

DocTypeCode: TypeAlias = Literal[1, 2, 3, 12, 20, 11, 31, 23, 56, 28]
ActType: TypeAlias = ParishActType
OtherType: TypeAlias = OtherParishActType

class DocTypeChoice(BaseModel):
    choices: list[DocTypeCode]

class GeneaChurchState(AgentState):
    doctype_evaluation: str
    doctype_choice: list[DocTypeCode]

def __act_type(code: DocTypeCode) -> tuple[ParishActType, OtherParishActType | None]:
    match code:
        case 1:
            return (ParishActType.BAPTISM, None)
        case 2: 
            return (ParishActType.WEDDING, None)
        case 3:
            return (ParishActType.DEATH, None)
        case 12:
            return (ParishActType.OTHER, OtherParishActType.MARRIAGE_EXEMPTION)
        case 20:
            return (ParishActType.OTHER, OtherParishActType.MARRIAGE_IMPEDIMENT)
        case 11:
            return (ParishActType.OTHER, OtherParishActType.LIST_OF_COMMUNIANTS)
        case 31:
            return (ParishActType.OTHER, OtherParishActType.LIST_OF_CONFIRMANDS)
        case 23:
            return (ParishActType.OTHER, OtherParishActType.LIST_OF_NAMES)
        case 56:
            return (ParishActType.OTHER, OtherParishActType.MEMORY_MASSES)
        case 28:
            return (ParishActType.OTHER, OtherParishActType.STATUS_ANIMARUM)
        case _:
            raise ValueError("not a known code")
    
def get_act_types(state: GeneaChurchState) -> tuple[list[ParishActType], list[OtherParishActType] | None]:
    act_types   = set()
    other_types = set()

    for code in state.get("doctype_choice", []):
        t, o = __act_type(code)
        act_types.add(t)
        if o:
            other_types.add(o)
    
    return (list(act_types), list(other_types) if other_types else None)

