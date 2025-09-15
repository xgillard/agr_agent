"""Workflow to search in church registers prior to 1796."""

from typing import (
    Literal,
    TypeVar,
    cast,
)

from langgraph.graph import END, START, StateGraph

from ....tools.agatha_common import Municipality, Parish
from ....tools.genealogy import (
    AJAX_URL,
    OtherParishActType,
    ParishActType,
    ParishIndex,
    genealogy_search_church_registers_prior_to_1796,
)
from ...common.llm import LLM
from ...common.schemas import Choices
from ...common.steps import (
    step_deliver_raw_data,
)
from ..common.schemas import TypeOfDocument, YearPeriod
from ..common.steps import step_fill_year_period, step_municipality, step_type_of_doc
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
    return { "act_types": options.options() } # type: ignore

async def step_other_act_type(state: T) -> T:
    """fill the other act type."""

    act_types = cast(list[ParishActType], state.get("act_types", []))
    if ParishActType.OTHER in act_types:
        options = cast(Choices[OtherParishActType],
            await (
                LLM
                .with_structured_output(Choices[OtherParishActType])
                .ainvoke(state["messages"] + [ other_type ] )
            )
        )
        return { "other_act_types": options.options() } # type: ignore
    else:
        return {} # type: ignore

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
    parishes = state.get("parish")

    period = cast(YearPeriod, state.get("period", YearPeriod()))

    if municipality is None or parishes is None:
        return {"call_data": None} # type: ignore
    
    call_data = genealogy_search_church_registers_prior_to_1796(
        municipality=cast(Municipality, municipality),
        parishes=cast(list[Parish], parishes),
        act_types=cast(list[ParishActType]|None, state.get("act_types")),
        other_types=cast(list[OtherParishActType]|None, state.get("other_act_types")),
        index_types=cast(list[ParishIndex]|None, state.get("indexes")),
        period_selector=period.selector,
        start_year=period.start_year,
        end_year=period.end_year,
    )
    return {"call_data": call_data} # type: ignore


DocTypePath = Literal["act_type", "index", "act_type_and_index"]
def route_on_type_of_doc(state: T) -> DocTypePath:
    """Route the flow based on type of doc."""

    tod = cast(TypeOfDocument, state.get("type_of_doc", TypeOfDocument.ACTS))
    match tod:
        case TypeOfDocument.ACTS:
            return "act_type"
        case TypeOfDocument.INDEXES:
            return "index"
        case TypeOfDocument.BOTH:
            return "act_type_and_index"


def _do_nothing(state: T) -> T:
    """Do nothing"""

    return {} # type: ignore

SEARCH_CHURCH_REGISTERS = (
    StateGraph(SearchChurchRegisterState)
        .add_node("municipality", step_municipality(context))
        .add_node("parish", step_parish)
        .add_node("type_of_doc", step_type_of_doc(context))
        #
        .add_node("act_type", step_act_type)
        .add_node("other_act_type", step_other_act_type)
        .add_node("index", step_index)
        .add_node("act_type_and_index", _do_nothing)
        .add_node("act_index_join", _do_nothing)
        #
        .add_node("period", step_fill_year_period(context))
        .add_node("call_tool", step_call_tool)
        .add_node("deliver_raw_data", step_deliver_raw_data)
        .add_edge(START, "municipality")
        .add_edge(START, "type_of_doc")
        .add_edge(START, "period")
        #
        .add_conditional_edges("type_of_doc", route_on_type_of_doc)
        .add_edge("act_type_and_index", "act_type")
        .add_edge("act_type_and_index", "index")
        #
        .add_edge("municipality", "parish")
        .add_edge("act_type", "other_act_type")
        .add_edge("index", "act_index_join")
        .add_edge("other_act_type", "act_index_join")
        #
        .add_edge([
            "parish", 
            "act_index_join",
            "period",
        ], "call_tool")
        .add_edge("call_tool", "deliver_raw_data")
        .add_edge("deliver_raw_data", END)
        .compile()
)