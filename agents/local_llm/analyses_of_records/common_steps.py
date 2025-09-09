"""Common steps to perform a search in the analyses of records."""

from typing import cast

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from .common_prompts import (
    act_type,
    location,
    period,
    project_type,
)
from .common_schemas import (
    ActTypeChoice,
    Location,
    Period,
    ProjectChoice,
    SearchAnalysesState,
)

LLM = init_chat_model(
    model = "mistral-small:24b",
    model_provider = "ollama",
)

def find_location(state: SearchAnalysesState) -> SearchAnalysesState:
    """Find the location"""

    loc = cast(Location,
        LLM
        .with_structured_output(Location)
        .invoke( state["outer_context"] + [ HumanMessage( location ) ])
    )
    return { "location": loc.location }

def find_period(state: SearchAnalysesState) -> SearchAnalysesState:
    """Find the search period."""

    when = cast(Period,
        LLM
        .with_structured_output(Period)
        .invoke( state["outer_context"] + [ HumanMessage( period ) ])
    )
    return { 
        "period_selector": when.selector, 
        "start_date": when.start_date,
        "end_date": when.end_date,
    }

def find_record_type(state: SearchAnalysesState) -> SearchAnalysesState:
    """Find the record type."""

    rsp = cast(ActTypeChoice,
        LLM
        .with_structured_output(ActTypeChoice)
        .invoke( state["outer_context"] + [ HumanMessage( act_type ) ])
    )
    return {"act_type": rsp.act_type }

def find_project(state: SearchAnalysesState) -> SearchAnalysesState:
    """Find the project name."""

    rsp = cast(ProjectChoice,
        LLM
        .with_structured_output(ProjectChoice)
        .invoke( state["outer_context"] + [ HumanMessage( project_type ) ])
    )
    return {"project": rsp.project }
