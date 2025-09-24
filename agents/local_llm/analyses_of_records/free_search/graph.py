"""Implement the logic to call a search_person_in_analyses_of_records as if the agent went through a wizzard."""

from typing import cast

from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, START, StateGraph

from ....tools.analyses_of_records import (
    AnalysesFreeSearchRequest,
    free_search_in_analyses_of_records,
)
from ...common.llm import LLM
from ..common.schemas import Period
from ..common.steps import (
    step_fill_location,
    step_fill_period,
    step_fill_project,
    step_fill_record_type,
)
from .prompts import (
    search_terms,
)
from .schemas import FreeSearchWizzardState


async def step_search_terms(state: FreeSearchWizzardState) -> FreeSearchWizzardState:
    """Request llm to fill in the search terms input parameter."""

    terms = await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + [search_terms]
    )

    return {"search_terms": terms} # type: ignore

async def step_call_tool(state: FreeSearchWizzardState) -> FreeSearchWizzardState:
    """Performs a call to the Agatha tool"""
    
    period = cast(Period, state.get("period", Period()))
    request = AnalysesFreeSearchRequest(
        search_terms=state.get("search_terms"),
        location=state.get("location"),
        period=period.selector,
        start_year=period.start_year,
        end_year=period.end_year,
        act_type=state.get("act_type"),
        project=state.get("project"),
    )
    
    call = free_search_in_analyses_of_records(request)
    return {
        "call_tool": "Analyses of records / Free Search",
        "call_request": request,
        "call_data": call,
    } # type: ignore

FREE_SEARCH_IN_ANALYSES_OF_RECORDS = (
    StateGraph(FreeSearchWizzardState)
        .add_node("fill_keywords", step_search_terms)
        .add_node("fill_location", step_fill_location)
        .add_node("fill_period", step_fill_period)
        .add_node("fill_act_type", step_fill_record_type)
        .add_node("fill_project", step_fill_project)
        .add_node("call_tool", step_call_tool)
        #
        .add_edge(START, "fill_keywords")
        .add_edge(START, "fill_location")
        .add_edge(START, "fill_period")
        .add_edge(START, "fill_act_type")
        .add_edge(START, "fill_project")
        .add_edge(
            [
                "fill_keywords",
                "fill_location",
                "fill_period",
                "fill_act_type",
                "fill_project"
            ], "call_tool")
        .add_edge("call_tool", END)
        #
        .compile()
)
