"""Schemas for structured output."""

from typing import (
    Literal,
)

from pydantic import (
    BaseModel,
)

from ....tools.generated import (
    AnalysesActRole,
    AnalysesActType,
)
from ..schemas import (
    AgentState,
    PersonData,
)

ActRoleCode = Literal[*AnalysesActRole.all_codes()] # type: ignore
ActTypeCode = Literal[*AnalysesActType.all_codes()] # type: ignore


class SignaleticPerson(BaseModel):
    first_name: str | None = None
    family_name: str | None = None
    profession: str | None = None


class BaseInfo(BaseModel):
    """The information that is easily gathered."""

    municipality_name_in_french_or_dutch: str | None = None
    parish_name: str | None = None

    people: list[SignaleticPerson] | None = None

class PeriodOfInterest(BaseModel):
    min_date_formatted_as_yyyy_mm_dd: str | None = None
    max_date_formatted_as_yyyy_mm_dd: str | None = None


class DocTypeChoice(BaseModel):
    type_of_record_code: ActTypeCode | None = None # type: ignore

class PersonRoleChoice(BaseModel):
    person_role_code: ActRoleCode | None = None # type: ignore


class FormalizationState(AgentState):
    base_info: BaseInfo
    period: PeriodOfInterest
    document_type: DocTypeChoice
    people_roles: list[PersonData]