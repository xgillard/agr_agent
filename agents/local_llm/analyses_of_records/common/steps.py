"""Common steps to perform a search in the analyses of records."""

from typing import TypeVar, cast

from langchain_core.messages import AIMessage

from ...common.llm import LLM
from .prompts import (
    act_type,
    context,
    location,
    project_type,
)
from .schemas import (
    ActTypeChoice,
    Location,
    ProjectChoice,
    SearchAnalysesState,
)

T = TypeVar("T", bound=SearchAnalysesState)

async def step_fill_location(state: T) -> T:
    """Fill the location field"""

    loc = cast(Location,
        await LLM
        .with_structured_output(Location)
        .ainvoke( state["messages"] + [ location.format(context=context) ])
    )
    return { "location": loc.location } # type: ignore

async def step_fill_record_type(state: T) -> T:
    """Fill the record type."""

    rsp = cast(ActTypeChoice,
        await LLM
        .with_structured_output(ActTypeChoice)
        .ainvoke( state["messages"] + [ act_type.format(context=context) ])
    )
    return {"act_type": rsp.act_type } # type: ignore

async def step_fill_project(state: T) -> T:
    """Fill the project name."""

    rsp = cast(ProjectChoice,
        await LLM
        .with_structured_output(ProjectChoice)
        .ainvoke( state["messages"] + [ project_type.format(context=context) ])
    )
    return {"project": rsp.project } # type: ignore

async def step_deliver_raw_data(state: T) -> T:
    """Deliver the raw data as an AI message."""

    return { # type: ignore
        "messages": AIMessage( # type: ignore
            f"""
            I have searched the analysed records in the archives, and here is the raw data I found:
            {state["call_data"].model_dump_json(by_alias=False, exclude_none=True)}
            """
        ),
    }