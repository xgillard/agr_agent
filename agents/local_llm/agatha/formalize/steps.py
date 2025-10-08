"""steps to implements the formalization workflow."""

from textwrap import (
    dedent,
    indent,
)
from typing import (
    cast,
)

from langchain_core.output_parsers import (
    StrOutputParser,
)

from ....local_llm.common.llm import (
    LLM,
)
from ....tools.generated import (
    AnalysesActRole,
    AnalysesActType,
)
from ..schemas import (
    AvailableData,
    PersonData,
)
from ..steps import (
    _build_context,
)
from .prompts import (
    analyse_doc_type,
    analyse_person_role,
    base_info,
    period_of_interest,
    select_doc_type,
    select_person_role,
)
from .schemas import (
    BaseInfo,
    DocTypeChoice,
    FormalizationState,
    PersonRoleChoice,
    PeriodOfInterest,
    SignaleticPerson,
)


def step_base_info(state: FormalizationState) -> FormalizationState:
    info = cast(BaseInfo, 
                LLM.with_structured_output(BaseInfo)
                .invoke(
                    state["messages"] + [
                        base_info.format(
                            context = _build_context(state)
                        )
                    ]
                )
    )
    return {"base_info": info} # type: ignore

def step_period_of_interest(state: FormalizationState) -> FormalizationState:
    context = _build_context(state)
    period = cast(PeriodOfInterest,
                  LLM.with_structured_output(PeriodOfInterest)
                    .invoke(
                        state["messages"] + [
                            period_of_interest.format(
                                context=context,
                            )
                        ]
                    )
    )
    return {"period": period} # type: ignore

def step_doctype(state: FormalizationState) -> FormalizationState:
    context = _build_context(state)
    codes = indent(AnalysesActType.code_descriptions(), "  ")
    evaluation = (LLM | StrOutputParser()).invoke(
                state["messages"] + [
                    analyse_doc_type.format(
                        context = context,
                        type_of_record_code_desc = codes,
                    )
                ]
            )
    #
    selection = cast(DocTypeChoice, 
                     LLM.with_structured_output(DocTypeChoice)
                     .invoke(
                         state["messages"] + [
                             select_doc_type.format(
                                 context=context,
                                 type_of_record_code_desc = codes,
                                 evaluation=evaluation,
                             )
                         ]
                     )
    )
    return {"document_type": selection} # type: ignore

def person_str(p: SignaleticPerson) -> SignaleticPerson:
    name = p.family_name if p.family_name else ""
    first= p.first_name if p.first_name else ""
    return f"{first} {name.upper()}"

def step_people_role(state: FormalizationState) -> FormalizationState:
    roles = list()
    base  = state.get("base_info", BaseInfo())
    people= base.people

    context = _build_context(state)
    codes = indent(AnalysesActRole.code_descriptions(), "  ")
    if people:
        for p in people:
            evaluation = evaluation = (LLM | StrOutputParser()).invoke(
                        state["messages"] + [
                            analyse_person_role.format(
                                context = context,
                                type_of_roles_code_desc = codes,
                                who = person_str(p),
                            )
                        ]
                    )
            #
            selection = cast(PersonRoleChoice, 
                            LLM.with_structured_output(PersonRoleChoice)
                            .invoke(
                                state["messages"] + [
                                    select_person_role.format(
                                        context=context,
                                        type_of_roles_code_desc = codes,
                                        who = person_str(p),
                                        evaluation=evaluation,
                                    )
                                ]
                            )
            )
            person_data = PersonData(
                first_name=p.first_name,
                family_name=p.family_name,
                profession=p.profession,
                role_code=selection.person_role_code,
            )
            roles.append(person_data)

    return {"people_roles": roles} # type: ignore

def step_synthesize(state: FormalizationState) -> FormalizationState:
    basic  = state.get("base_info", BaseInfo())
    period = state.get("period", PeriodOfInterest())
    people = state.get("people_roles", [])
    doctype= state.get("document_type")

    synthesis = AvailableData(
        municipality_name=basic.municipality_name_in_french_or_dutch,
        parish_name=basic.parish_name,
        type_of_record_code=doctype.type_of_record_code,
        people=people,
        min_document_date_formatted_as_yyyy_mm_dd=period.min_date_formatted_as_yyyy_mm_dd,
        max_document_date_formatted_as_yyyy_mm_dd=period.max_date_formatted_as_yyyy_mm_dd,
    )
    return {"available_data": synthesis} # type: ignore
