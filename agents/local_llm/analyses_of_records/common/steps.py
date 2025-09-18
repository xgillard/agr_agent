"""Common steps to perform a search in the analyses of records."""

from typing import TypeVar, cast

from ...common.llm import LLM
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

T = TypeVar("T", bound=SearchAnalysesState)

async def step_fill_location(state: T) -> T:
    """Fill the location field"""

    loc = cast(Location,
        await LLM
        .with_structured_output(Location)
        .ainvoke( state["messages"] + [ location ])
    )
    return { "location": loc.location } # type: ignore


async def step_fill_period(state: T) -> T:
    """Fill the search period."""

    when = cast(Period,
        await LLM
        .with_structured_output(Period)
        .ainvoke( state["messages"] + [ period ])
    )
    return { "period": when } # type: ignore


async def step_fill_record_type(state: T) -> T:
    """Fill the record type."""

    rsp = cast(ActTypeChoice,
        await LLM
        .with_structured_output(ActTypeChoice)
        .ainvoke( state["messages"] + [ act_type ])
    )
    return {"act_type": rsp.act_type } # type: ignore

async def step_fill_project(state: T) -> T:
    """Fill the project name."""

    rsp = cast(ProjectChoice,
        await LLM
        .with_structured_output(ProjectChoice)
        .ainvoke( state["messages"] + [ project_type ])
    )
    return {"project": rsp.project } # type: ignore
