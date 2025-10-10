from typing import (
    Literal,
    TypeAlias,
)

from pydantic import (
    BaseModel,
)

from ....tools.genealogy import (
    CivilActType,
    OtherCivilActType,
)
from ...agatha.schemas import (
    AgentState,
)

DocTypeCode: TypeAlias = Literal["1", "2", "3", "BS_U", "BS_A", "BS_Ob", "BS_E", "BS_N"]

class DocTypeChoice(BaseModel):
    choices: list[DocTypeCode]

class GeneaCivilState(AgentState):
    doctype_evaluation: str
    doctype_choice: list[DocTypeCode]

def __act_type(code: DocTypeCode) -> tuple[CivilActType, OtherCivilActType | None]:
    match code:
        case "1":
            return (CivilActType.BIRTH, None)
        case "2": 
            return (CivilActType.WEDDING, None)
        case "3":
            return (CivilActType.DEATH, None)
        case "BS_U":
            return (CivilActType.OTHER, OtherCivilActType.ADDITIONAL_REGISTER)
        case "BS_A":
            return (CivilActType.OTHER, OtherCivilActType.ADOPTION)
        case "BS_Ob":
            return (CivilActType.OTHER, OtherCivilActType.DEATH_ANNEXES)
        case "BS_E":
            return (CivilActType.OTHER, OtherCivilActType.DIVORCE)
        case "BS_N":
            return (CivilActType.OTHER, OtherCivilActType.NATURALISATION)
        case _:
            raise ValueError("not a known code")
        
def get_act_types(state: GeneaCivilState) -> tuple[list[CivilActType], list[OtherCivilActType] | None]:
    act_types   = set()
    other_types = set()

    for code in state.get("doctype_choice", []):
        t, o = __act_type(code)
        act_types.add(t)
        if o:
            other_types.add(o)
    
    return (list(act_types), list(other_types) if other_types else None) 

