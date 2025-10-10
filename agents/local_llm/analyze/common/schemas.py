from typing import (
    Literal,
    TypeAlias,
)

from pydantic import (
    BaseModel,
)

from ....tools.analyses_of_records import (
    AnalysesActRole,
    AnalysesActType,
    PersonCriterion,
)
from ...agatha.schemas import (
    AgentState,
)

ActRoleCode: TypeAlias = Literal[*AnalysesActRole.all_codes()] # type: ignore
ActTypeCode: TypeAlias = Literal[*AnalysesActType.all_codes()] # type: ignore

class DocTypeChoice(BaseModel):
    type_of_record_code: ActTypeCode | None = None # type: ignore

class PersonRoleChoice(BaseModel):
    person_role_code: ActRoleCode | None = None # type: ignore


class AnalysesState(AgentState):
    doctype_analyse: str
    doctype_selection: AnalysesActType
    people: list[PersonCriterion]
    search_term: str
