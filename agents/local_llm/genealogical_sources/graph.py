"""Implment the workflow to search in the genealogical sources."""

from typing import Literal, cast

from langgraph.graph import END, START, StateGraph

from ..common.llm import LLM
from .church_registers.graph import SEARCH_CHURCH_REGISTERS
from .civil_state_registers.graph import SEARCH_CIVIL_REGISTERS
from .common.schemas import GeneaSearchState
from .prompts import triage
from .schemas import GeneaTool, TriageChoice


async def step_triage(state: GeneaSearchState) -> Literal["church", "civil"]:
    """Triage between free search and search persons."""

    response = cast(TriageChoice,
        await (
            LLM.with_structured_output(TriageChoice)
                .ainvoke(state["messages"] + [triage])
        )
    )
    if GeneaTool.CHURCH_REGISTERS == response.choice:
        return "church"
    else:
        return "civil"

SEARCH_IN_GENEALOGIC_SOURCES = (
    StateGraph(GeneaSearchState)
        .add_node("church", SEARCH_CHURCH_REGISTERS)
        .add_node("civil", SEARCH_CIVIL_REGISTERS)
        #
        .add_conditional_edges(START, step_triage)
        .add_edge("church", END)
        .add_edge("civil", END)
        #
        .compile()
)