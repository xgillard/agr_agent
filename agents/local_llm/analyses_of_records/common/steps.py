"""Common steps to perform a search in the analyses of records."""

from typing import cast

from langchain_core.messages import HumanMessage

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
        .ainvoke( state["outer_context"] + [ HumanMessage( location ) ])
    )
    return { "location": loc.location }

async def step_fill_period(state: SearchAnalysesState) -> SearchAnalysesState:
    """Fill the search period."""

    when = cast(Period,
        await LLM
        .with_structured_output(Period)
        .ainvoke( state["outer_context"] + [ HumanMessage( period ) ])
    )
    return { 
        "period_selector": when.selector, 
        "start_date": when.start_date,
        "end_date": when.end_date,
    }

async def step_fill_record_type(state: SearchAnalysesState) -> SearchAnalysesState:
    """Fill the record type."""

    rsp = cast(ActTypeChoice,
        await LLM
        .with_structured_output(ActTypeChoice)
        .ainvoke( state["outer_context"] + [ HumanMessage( act_type ) ])
    )
    return {"act_type": rsp.act_type }

async def step_fill_project(state: SearchAnalysesState) -> SearchAnalysesState:
    """Fill the project name."""

    rsp = cast(ProjectChoice,
        await LLM
        .with_structured_output(ProjectChoice)
        .ainvoke( state["outer_context"] + [ HumanMessage( project_type ) ])
    )
    return {"project": rsp.project }
