"""Workflow to search in church registers prior to 1796."""

from typing import (
    TypeVar,
    cast,
)

from langgraph.graph import END, START, StateGraph

from ....tools.agatha_common import Municipality, Parish, PeriodSelector
from ....tools.genealogy import (
    AJAX_URL,
    OtherParishActType,
    ParishActType,
    ParishIndex,
    genealogy_search_church_registers_prior_to_1796,
)
from ...common.llm import LLM
from ...common.steps import (
    step_deliver_raw_data,
    step_fill_period,
)
from ..common.schemas import Choices
from ..common.steps import (
    step_municipality,
)
from .prompts import (
    act_type,
    context,
    index_type,
    other_type,
    parish,
)
from .schemas import (
    SearchChurchRegisterState,
    StrList,
)

T = TypeVar("T", bound=SearchChurchRegisterState)

async def step_parish(state: T) -> T: 
    """Fill the parish."""

    mun = state.get("municipality")
    par = cast(Municipality, mun).parishes(AJAX_URL) if mun is not None else []
    if len(par) <= 1:
        return {"parish": par} # type: ignore
    else:
        par_name = cast(StrList, await (
            LLM.with_structured_output(StrList)
            .ainvoke(
                state["messages"] + 
                [ parish.format(context=context, parish=[p.place_name for p in par]) ]
            ))
        )
        par = [
            p for p in par if p.place_name.lower() in par_name.lst
        ]
        return {"parish": par} # type: ignore


async def step_act_type(state: T) -> T:
    """fill the act type."""

    options = cast(Choices[ParishActType],
        await (
            LLM
            .with_structured_output(Choices[ParishActType])
            .ainvoke(state["messages"] + [ act_type ] )
        )
    )
    return { "act_type": options.options() } # type: ignore

async def step_other_act_type(state: T) -> T:
    """fill the other act type."""

    options = cast(Choices[OtherParishActType],
        await (
            LLM
            .with_structured_output(Choices[OtherParishActType])
            .ainvoke(state["messages"] + [ other_type ] )
        )
    )
    return { "other_act_types": options.options() } # type: ignore

async def step_index(state: T) -> T:
    """fill the index type."""

    options = cast(Choices[ParishIndex],
        await (
            LLM
            .with_structured_output(Choices[ParishIndex])
            .ainvoke(state["messages"] + [ index_type ] )
        )
    )
    return { "indexes": options.options() } # type: ignore


async def step_call_tool(state: T) -> T:
    """Actually calls the tool using state information."""
    # deal with required
    municipality = state.get("municipality")
    parishes = state.get("paris")

    if municipality is None or parishes is None:
        return {"call_data": None} # type: ignore
    
    call_data = genealogy_search_church_registers_prior_to_1796(
        municipality=cast(Municipality, municipality),
        parishes=cast(list[Parish], parishes),
        act_types=cast(list[ParishActType]|None, state.get("act_type")),
        other_types=cast(list[OtherParishActType]|None, state.get("other_act_type")),
        index_types=cast(list[ParishIndex]|None, state.get("index_type")),
        period_selector=cast(PeriodSelector|None, state.get("period_selector")),
        start_year=cast(str|None, state.get("start_date")),
        end_year=cast(str|None, state.get("end_date")),
    )
    return {"call_data": call_data} # type: ignore

SEARCH_CHURCH_REGISTERS = (
    StateGraph(SearchChurchRegisterState)
        .add_node("municipality", step_municipality(context))
        .add_node("parish", step_parish)
        .add_node("act_type", step_act_type)
        .add_node("other_act_type", step_other_act_type)
        .add_node("index", step_index)
        .add_node("period", step_fill_period(context))
        .add_node("call_tool", step_call_tool)
        .add_node("deliver_raw_data", step_deliver_raw_data)
        .add_edge(START, "municipality")
        .add_edge(START, "act_type")
        .add_edge(START, "index")
        .add_edge(START, "period")
        .add_edge("municipality", "parish")
        .add_edge("act_type", "other_act_type")
        .add_edge([
            "parish", 
            "other_act_type",
            "index",
            "period",
        ], "call_tool")
        .add_edge("call_tool", "deliver_raw_data")
        .add_edge("deliver_raw_data", END)
        .compile()
)