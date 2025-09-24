"""Workflow to search in civil registers posterior to 1796."""

from typing import (
    Literal,
    cast,
)

from langgraph.graph import END, START, StateGraph

from ....tools.genealogy import (
    CivilActType,
    CivilIndex,
    Municipality,
    OtherCivilActType,
    OtherCivilIndex,
    genealogy_search_civil_state_registers,
)
from ...common.llm import LLM
from ...common.schemas import Choices
from ..common.schemas import TypeOfDocument, YearPeriod
from ..common.steps import (
    step_fill_year_period,
    step_municipality,
    step_type_of_doc,
)
from .prompts import (
    act_type,
    index_type,
    other_index_type,
    other_type,
)
from .schemas import (
    SearchCivilRegisterState,
)


class ChoicesCivilActType(Choices[CivilActType]):
    pass

async def step_act_type(state: SearchCivilRegisterState) -> SearchCivilRegisterState:
    """fill the act type."""

    options = cast(ChoicesCivilActType,
        await (
            LLM
            .with_structured_output(ChoicesCivilActType)
            .ainvoke(state["messages"] + [ act_type ] )
        )
    )
    return { "act_types": options.options() } # type: ignore

class ChoicesOtherCivilActType(Choices[OtherCivilActType]):
    pass

async def step_other_act_type(state: SearchCivilRegisterState) -> SearchCivilRegisterState:
    """fill the other act type."""

    act_types = cast(list[CivilActType], state.get("act_types", []))
    if CivilActType.OTHER in act_types:
        options = cast(ChoicesOtherCivilActType,
            await (
                LLM
                .with_structured_output(ChoicesOtherCivilActType)
                .ainvoke(state["messages"] + [ other_type ] )
            )
        )
        return { "other_act_types": options.options() } # type: ignore
    else:
        return {} # type: ignore

class ChoicesCivilIndex(Choices[CivilIndex]):
    pass

async def step_index(state: SearchCivilRegisterState) -> SearchCivilRegisterState:
    """fill the index type."""

    options = cast(ChoicesCivilIndex,
        await (
            LLM
            .with_structured_output(ChoicesCivilIndex)
            .ainvoke(state["messages"] + [ index_type ] )
        )
    )
    return { "indexes": options.options() } # type: ignore

class ChoicesOtherCivilIndex(Choices[OtherCivilIndex]):
    pass

async def step_other_index(state: SearchCivilRegisterState) -> SearchCivilRegisterState:
    """fill the index type."""

    indexes = cast(list[CivilIndex], state.get("indexes", []))
    if CivilIndex.OTHER in indexes:
        options = cast(ChoicesOtherCivilIndex,
            await (
                LLM
                .with_structured_output(ChoicesCivilIndex)
                .ainvoke(state["messages"] + [ other_index_type ] )
            )
        )
        return { "other_indexes": options.options() } # type: ignore
    else:
        return {} # type: ignore

## TODO: other index step.

async def step_call_tool(state: SearchCivilRegisterState) -> SearchCivilRegisterState:
    """Actually calls the tool using state information."""
    # deal with required
    municipality = state.get("municipality")
    
    if municipality is None:
        return {"call_data": None} # type: ignore

    period = cast(YearPeriod, state.get("period", YearPeriod()))
    request = dict(
        municipality=cast(Municipality, municipality),
        act_types=cast(list[CivilActType]|None, state.get("act_types")),
        other_types=cast(list[OtherCivilActType]|None, state.get("other_act_types")),
        index_types=cast(list[CivilIndex]|None, state.get("indexes")),
        other_indexes=cast(list[OtherCivilIndex]|None, state.get("other_indexes")),
        period_selector=period.selector,
        start_year=period.start_year,
        end_year=period.end_year,
    )
    call_data = genealogy_search_civil_state_registers(**request) # type: ignore
    return {
        "call_tool": "Genealogical sources / Civil State Registers",
        "call_request": request,
        "call_data": call_data,
    } # type: ignore

    return {"call_data": call_data} # type: ignore


DocTypePath = Literal["act_type", "index", "act_type_and_index"]
def route_on_type_of_doc(state: SearchCivilRegisterState) -> DocTypePath:
    """Route the flow based on type of doc."""

    tod = cast(TypeOfDocument, state.get("type_of_doc", TypeOfDocument.ACTS))
    match tod:
        case TypeOfDocument.ACTS:
            return "act_type"
        case TypeOfDocument.INDEXES:
            return "index"
        case TypeOfDocument.BOTH:
            return "act_type_and_index"

def _do_nothing(state: SearchCivilRegisterState) -> SearchCivilRegisterState:
    """Do nothing"""

    return {} # type: ignore

SEARCH_CIVIL_REGISTERS = (
    StateGraph(SearchCivilRegisterState)
        .add_node("municipality", step_municipality)
        .add_node("type_of_doc", step_type_of_doc)
        #
        .add_node("act_type", step_act_type)
        .add_node("other_act_type", step_other_act_type)
        .add_node("index", step_index)
        .add_node("other_index", step_other_index)
        .add_node("act_type_and_index", _do_nothing)
        .add_node("act_index_join", _do_nothing)
        #
        .add_node("period", step_fill_year_period)
        .add_node("call_tool", step_call_tool)
        .add_edge(START, "municipality")
        .add_edge(START, "type_of_doc")
        .add_edge(START, "period")
        #
        .add_conditional_edges("type_of_doc", route_on_type_of_doc)
        .add_edge("act_type_and_index", "act_type")
        .add_edge("act_type_and_index", "index")
        .add_edge("act_type", "other_act_type")
        .add_edge("index", "other_index")
        .add_edge("other_act_type", "act_index_join")
        .add_edge("other_index", "act_index_join")
        #
        .add_edge([
            "municipality", 
            "period",
            "act_index_join",
        ], "call_tool")
        #
        .add_edge("call_tool", END)
        .compile()
)