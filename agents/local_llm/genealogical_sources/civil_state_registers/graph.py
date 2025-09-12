"""Workflow to search in civil registers posterior to 1796."""

from typing import (
    TypeVar,
    cast,
)

from langgraph.graph import END, START, StateGraph

from ....tools.agatha_common import (
    PeriodSelector,
)
from ....tools.genealogy import (
    CivilActType,
    CivilIndex,
    Municipality,
    OtherCivilActType,
    genealogy_search_civil_state_registers,
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
)
from .schemas import (
    SearchCivilRegisterState,
)

T = TypeVar("T", bound=SearchCivilRegisterState)

async def step_act_type(state: T) -> T:
    """fill the act type."""

    options = cast(Choices[CivilActType],
        await (
            LLM
            .with_structured_output(Choices[CivilActType])
            .ainvoke(state["messages"] + [ act_type ] )
        )
    )
    return { "act_type": options.options() } # type: ignore

async def step_other_act_type(state: T) -> T:
    """fill the other act type."""

    options = cast(Choices[OtherCivilActType],
        await (
            LLM
            .with_structured_output(Choices[OtherCivilActType])
            .ainvoke(state["messages"] + [ other_type ] )
        )
    )
    return { "other_act_types": options.options() } # type: ignore

async def step_index(state: T) -> T:
    """fill the index type."""

    options = cast(Choices[CivilIndex],
        await (
            LLM
            .with_structured_output(Choices[CivilIndex])
            .ainvoke(state["messages"] + [ index_type ] )
        )
    )
    return { "indexes": options.options() } # type: ignore


async def step_call_tool(state: T) -> T:
    """Actually calls the tool using state information."""
    # deal with required
    municipality = state.get("municipality")
    

    if municipality is None:
        return {"call_data": None} # type: ignore

    call_data = genealogy_search_civil_state_registers(
        municipality=cast(Municipality, municipality),
        act_types=cast(list[CivilActType]|None, state.get("act_type")),
        other_types=cast(list[OtherCivilActType]|None, state.get("other_act_type")),
        index_types=cast(list[CivilIndex]|None, state.get("index_type")),
        period_selector=cast(PeriodSelector|None, state.get("period_selector")),
        start_year=cast(str|None, state.get("start_date")),
        end_year=cast(str|None, state.get("end_date")),
    )
    return {"call_data": call_data} # type: ignore

SEARCH_CIVIL_REGISTERS = (
    StateGraph(SearchCivilRegisterState)
        .add_node("municipality", step_municipality(context))
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
        .add_edge("act_type", "other_act_type")
        .add_edge([
            "municipality", 
            "other_act_type",
            "index",
            "period",
        ], "call_tool")
        .add_edge("call_tool", "deliver_raw_data")
        .add_edge("deliver_raw_data", END)
        .compile()
)