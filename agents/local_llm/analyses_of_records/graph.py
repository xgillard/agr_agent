"""Implment the workflow to search in the analyses of records."""

from typing import Literal, cast

from langgraph.graph import END, START, StateGraph

from ..common.llm import LLM
from ..common.schemas import AgathaToolState
from .free_search import FREE_SEARCH_IN_ANALYSES_OF_RECORDS
from .prompts import triage
from .schemas import AnalysesOfRecordsTool, TriageChoice
from .search_person import SEARCH_PERSON_IN_ANALYSES_OF_RECORDS


async def step_triage(state: AgathaToolState) -> Literal["free_search", "search_person"]:
    """Triage between free search and search persons."""

    response = cast(TriageChoice,
        await (
            LLM.with_structured_output(TriageChoice)
                .ainvoke(state["messages"] + [triage])
        )
    )
    if AnalysesOfRecordsTool.SEARCH_PERSON == response.choice:
        return "search_person"
    else:
        return "free_search"

SEARCH_IN_ANALYSES_OF_RECORDS = (
    StateGraph(AgathaToolState)
        .add_node("free_search", FREE_SEARCH_IN_ANALYSES_OF_RECORDS)
        .add_node("search_person", SEARCH_PERSON_IN_ANALYSES_OF_RECORDS)
        #
        .add_conditional_edges(START, step_triage)
        .add_edge("free_search", END)
        .add_edge("search_person", END)
        #
        .compile()
)