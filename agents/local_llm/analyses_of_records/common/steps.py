"""Common steps to perform a search in the analyses of records."""

from typing import cast

from langchain_core.messages import AIMessage, HumanMessage

from .llm import LLM
from .prompts import (
    act_type,
    location,
    period,
    project_type,
)
from .schemas import (
    ActTypeChoice,
    Location,
    Period,
    ProjectChoice,
    SearchAnalysesState,
)


async def step_fill_location(state: SearchAnalysesState) -> SearchAnalysesState:
    """Fill the location field"""

    loc = cast(Location,
        await LLM
        .with_structured_output(Location)
        .ainvoke( state["messages"] + [ HumanMessage( location ) ])
    )
    return { "location": loc.location } # type: ignore

async def step_fill_period(state: SearchAnalysesState) -> SearchAnalysesState:
    """Fill the search period."""

    when = cast(Period,
        await LLM
        .with_structured_output(Period)
        .ainvoke( state["messages"] + [ HumanMessage( period ) ])
    )
    return { 
        "period_selector": when.selector, 
        "start_date": when.start_date,
        "end_date": when.end_date,
    } # type: ignore

async def step_fill_record_type(state: SearchAnalysesState) -> SearchAnalysesState:
    """Fill the record type."""

    rsp = cast(ActTypeChoice,
        await LLM
        .with_structured_output(ActTypeChoice)
        .ainvoke( state["messages"] + [ HumanMessage( act_type ) ])
    )
    return {"act_type": rsp.act_type } # type: ignore

async def step_fill_project(state: SearchAnalysesState) -> SearchAnalysesState:
    """Fill the project name."""

    rsp = cast(ProjectChoice,
        await LLM
        .with_structured_output(ProjectChoice)
        .ainvoke( state["messages"] + [ HumanMessage( project_type ) ])
    )
    return {"project": rsp.project } # type: ignore

async def step_deliver_raw_data(state: SearchAnalysesState) -> SearchAnalysesState:
    """Deliver the raw data as an AI message."""

    return { # type: ignore
        "messages": AIMessage( # type: ignore
            f"""
            I have searched the analysed records in the archives, and here is the raw data I found:
            {state["call_data"].model_dump_json(by_alias=False, exclude_none=True)}
            """
        ),
    }