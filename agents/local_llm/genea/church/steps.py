"""steps to call the genea church tool"""

from typing import (
    TypeAlias,
    cast,
)

from langchain_core.output_parsers import (
    StrOutputParser,
)

from ....tools.agatha_common import (
    Municipality,
)
from ....tools.genealogy import (
    AJAX_URL,
    genealogy_search_church_registers_prior_to_1796,
)
from ...agatha.schemas import (
    BaseCriteria,
    PeriodOfInterest,
)
from ...agatha.steps import (
    _build_context,
)
from ...common.llm import (
    LLM,
)
from .prompts import (
    analyse_doctype,
    select_doctype,
)
from .schemas import (
    DocTypeChoice,
    GeneaChurchState,
    get_act_types,
)

State: TypeAlias = GeneaChurchState

async def step_analyse(state: State) -> State:
    evaluation = await (
        (LLM | StrOutputParser())
        .ainvoke(state["messages"] + [
            analyse_doctype.format(
                context=_build_context(state),
            )
        ])
    )
    return {"doctype_evaluation": evaluation} # type: ignore

async def step_select(state: State) -> State:
    choice = cast(DocTypeChoice, await(
        LLM.with_structured_output(DocTypeChoice)
            .ainvoke(
                state["messages"] + [
                    select_doctype.format(
                        context = _build_context(state),
                        evaluation = state.get("doctype_evaluation", "I've been lazy and did not do anything"),
                    )
                ]
            )
    ))
    return {"doctype_choice": choice.choices} # type: ignore

async def step_invoke(state: State) -> State:
    basic  = cast(BaseCriteria, state.get("criteria", BaseCriteria()))
    period = basic.period_of_interest if basic.period_of_interest else PeriodOfInterest()

    assert(basic.municipality_name_in_french_or_dutch is not None)

    municipality = Municipality.by_name(
        name=basic.municipality_name_in_french_or_dutch, 
        ajax=AJAX_URL, 
        return_single_best_match=True
    )
    parishes = municipality.parishes(AJAX_URL) if municipality is not None else []

    if basic.parish_name is not None:
        parishes = [ p for p in parishes if basic.parish_name in p.place_name.lower() ]
    
    start_year = period.min_date_formatted_as_yyyy_mm_dd[:4] if period.min_date_formatted_as_yyyy_mm_dd else None
    end_year = period.max_date_formatted_as_yyyy_mm_dd[:4] if period.max_date_formatted_as_yyyy_mm_dd else None

    act_types, other_types = get_act_types(state)

    call_request = dict(
        municipality=municipality,
        parishes=parishes,
        start_year=start_year,
        end_year=end_year,
        act_types=act_types,
        other_types=other_types,
        #index_types=,
        #period_selector=
    )

    if municipality is None:
        return { # type: ignore
            "call_tool": "Genealogical sources / Church Registers",
            "call_request": call_request,
            "call_data": "Unknown municipality. Did you use french or dutch spelling ?",
        }
    else:
        call_data = genealogy_search_church_registers_prior_to_1796(**call_request) # type: ignore
        return { # type: ignore
            "call_tool": "Genealogical sources / Church Registers",
            "call_request": call_request,
            "call_data": call_data,
        }



