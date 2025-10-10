from typing import (
    TypeAlias,
    cast,
)

from langchain_core.output_parsers import (
    StrOutputParser,
)

from ....local_llm.agatha.schemas import (
    BaseCriteria,
    SignaleticPerson,
    PeriodOfInterest,
)
from ....local_llm.common.llm import (
    LLM,
)
from ....tools.analyses_of_records import (
    AnalysesFreeSearchRequest,
    AnalysesSearchPersonRequest,
    PersonCriterion,
    free_search_in_analyses_of_records,
    search_person_in_analyses_of_records,
)
from ....tools.generated import (
    AnalysesActRole,
    AnalysesActType,
)
from ...agatha.steps import (
    _build_context,
)
from .prompts import (
    analyse_doc_type,
    analyse_person_role,
    search_terms,
    select_doc_type,
    select_person_role,
)
from .schemas import (
    AnalysesState,
    DocTypeChoice,
    PersonRoleChoice,
)

State: TypeAlias = AnalysesState

async def step_analyse_doctype(state: State) -> State:
    context = _build_context(state)
    evaluation = await (
        (LLM | StrOutputParser())
        .ainvoke(
            state["messages"] + [
                analyse_doc_type.format(
                    context = context,
                )
            ]
        )
    )
    return {"doctype_analyse": evaluation} # type: ignore

async def step_select_doctype(state: State) -> State:
    context = _build_context(state)
    evaluation = state.get("doctype_analyse")
    selection = cast(DocTypeChoice, await (
            LLM.with_structured_output(DocTypeChoice)
            .ainvoke(
                state["messages"] + [
                    select_doc_type.format(
                        context=context,
                        evaluation=evaluation,
                    )
                ]
            )
        )
    )
    doctype = AnalysesActType.from_code(selection.type_of_record_code) if selection.type_of_record_code else None
    return {"doctype_selection": doctype} # type: ignore

def person_str(p: SignaleticPerson) -> SignaleticPerson:
    name = p.family_name if p.family_name else ""
    first= p.first_name if p.first_name else ""
    return f"{first} {name.upper()}"


async def single_person_role(
        state: State, 
        context: str, 
        p: SignaleticPerson,
    ) -> PersonCriterion:

    who = person_str(p)
    evaluation = await (LLM | StrOutputParser()).ainvoke(
                state["messages"] + [
                    analyse_person_role.format(
                        context = context,
                        who = who,
                    )
                ]
            )
    #
    selection = cast(PersonRoleChoice, await (
                    LLM.with_structured_output(PersonRoleChoice)
                    .ainvoke(
                        state["messages"] + [
                            select_person_role.format(
                                context=context,
                                who = who,
                                evaluation=evaluation,
                            )
                        ]
                    )
        )
    )
    role = AnalysesActRole.from_code(selection.person_role_code) if selection.person_role_code else None
    return PersonCriterion(
        first_name=p.first_name,
        family_name=p.family_name,
        profession=p.profession,
        role_code=role,
    )

async def step_people_role(state: State) -> State:
    roles = list()
    base  = state.get("criteria", BaseCriteria())
    people= base.people_of_interest

    context = _build_context(state)
    if people:
        pdata = [ single_person_role(state, context, p) for p in people]
        roles = [ await d for d in pdata ]
    
    return {"people": roles} # type: ignore

async def step_search_term(state: State) -> State:
    context = _build_context(state)

    terms =  await (
        (LLM | StrOutputParser())
            .ainvoke(state["messages"] + [search_terms.format(context=context)])
    )

    return {"search_term": terms}



async def tool_analyses_free_search(state: State) -> State:
    crit  = state.get("criteria", BaseCriteria())
    terms = state.get("search_term", "i am not ready")
    location = crit.municipality_name_in_french_or_dutch
    period = crit.period_of_interest if crit.period_of_interest else PeriodOfInterest()
    start_year = period.min_date_formatted_as_yyyy_mm_dd[:4] if period.min_date_formatted_as_yyyy_mm_dd else None
    end_year = period.max_date_formatted_as_yyyy_mm_dd[:4] if period.max_date_formatted_as_yyyy_mm_dd else None
    act_type = cast(AnalysesActType, state.get("doctype_selection"))
    call_request = AnalysesFreeSearchRequest(
        search_terms=terms,
        location=location,
        start_year=start_year,
        end_year=end_year,
        act_type=act_type,
        # project
    )

    call_data = free_search_in_analyses_of_records(call_request)
    
    return { # type: ignore
        "call_tool": "Analyses of Records / Free Search",
        "call_request": call_request,
        "call_data": call_data,
    }

async def tool_analyses_search_person(state: State) -> State:
    crit  = state.get("criteria", BaseCriteria())
    location = crit.municipality_name_in_french_or_dutch
    period = crit.period_of_interest if crit.period_of_interest else PeriodOfInterest()
    start_year = period.min_date_formatted_as_yyyy_mm_dd[:4] if period.min_date_formatted_as_yyyy_mm_dd else None
    end_year = period.max_date_formatted_as_yyyy_mm_dd[:4] if period.max_date_formatted_as_yyyy_mm_dd else None
    act_type = cast(AnalysesActType, state.get("doctype_selection"))
    persons = state.get("people", [])

    call_request = AnalysesSearchPersonRequest(
        persons=persons,
        location=location,
        start_year=start_year,
        end_year=end_year,
        act_type=act_type,
        #project=,
    )

    call_data = search_person_in_analyses_of_records(call_request)
    
    return { # type: ignore
        "call_tool": "Analyses of Records / Search Person",
        "call_request": call_request,
        "call_data": call_data,
    }
