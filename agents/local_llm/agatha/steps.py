"""steps that implements the simplified agatha workflow."""

from typing import (
    Literal,
    cast,
)

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from langchain_core.output_parsers import (
    StrOutputParser,
)
from pydantic import (
    BaseModel,
)
from pydantic_core import (
    to_json,
)

from ..common.schemas import YesNoChoice

from ...tools.agatha_help import (
    agatha_help,
)
from ..common.llm import (
    LLM,
)
from .prompts import (
    analyze_tool,
    enough_information,
    formalize_basic,
    reasoning_step,
    respond,
    select_tool,
    summarize,
    system_prompt,
    what_objective,
)
from .schemas import (
    AgentState,
    BaseCriteria,
)

AGATHA_HELP = agatha_help()

async def step_initialize(state: AgentState) -> AgentState:
    messages  = state.get("messages", [])
    
    if not messages:
        messages = [system_prompt]

    messages += [ HumanMessage(state["input"]) ]
    return { # type: ignore
        "input": state["input"],
        "messages": messages,
    }


async def cond_enough_info(state: AgentState) -> Literal["Respond", "Set Objective"]:
    # circuit breaker
    n = state.get("n", 0) 
    if n >= 5:
        return "Respond"
    
    context = _build_context(state)
    response= cast(YesNoChoice,
        await LLM.with_structured_output(YesNoChoice)
        .ainvoke(state["messages"] + [
            enough_information.format(
                context=context
            )
        ])
    )
    return "Respond" if response.choice.lower() == "no" else "Set Objective"


def _build_context(state: AgentState) -> str:
    """Build a self-contained context for use in prompts."""

    context   = ""
    scratch   = state.get("scratch")
    objective = state.get("thought")
    if scratch:
        context += f"\n### Previous Research\n{scratch}\n"
    
    if objective:
        context += f"\n\n### Current Partial Objective\n{objective}\n"

    if context:
        context = f"## Context\n{context}\n"
    
    return context

async def step_set_objective(state: AgentState) -> AgentState:
    n = state.get("n", 0) 

    rsp =  await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + [ what_objective.format(
            context     = _build_context(state),
        ) ]
    )
    return {"n": n+1, "thought": rsp} # type: ignore

async def step_formalize(state: AgentState) -> AgentState:
    criteria = cast(BaseCriteria, await (
            LLM.with_structured_output(BaseCriteria)
            .ainvoke(
                state["messages"] + [
                    formalize_basic.format(
                        context = _build_context(state),
                    )
                ]
            )
        )
    )
    return {"criteria": criteria} # type: ignore

_Tool = Literal[
    "Analyses of Records", 
    "Genealogical sources",
    "Online Help Resources",
]

class ToolChoice(BaseModel):
    ranking: list[_Tool]


def can_be_used(formalized: BaseCriteria, tool: _Tool) -> bool:
    match tool:
        case "Online Help Resources":
            return True
        case "Analyses of Records": 
            return True
        case "Genealogical sources":
            poi = formalized.period_of_interest
            return (
                bool(formalized.municipality_name_in_french_or_dutch) and 
                bool(poi) and 
                bool(poi.min_date_formatted_as_yyyy_mm_dd) and 
                bool(poi.max_date_formatted_as_yyyy_mm_dd) 
            )
        case _:
            raise ValueError(f"{tool} is not a known valid tool")

async def cond_what_tool(state: AgentState) -> _Tool:
    context = _build_context(state)

    evaluation = await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + [
            analyze_tool.format(
                context=context,
            )
        ]
    )
    rsp = cast(ToolChoice,  await (
        LLM .with_structured_output(ToolChoice)
            .ainvoke(
            state["messages"] + [ select_tool.format(
                context=context,
                evaluation=evaluation,
            ) ])
    ))
    crit = state.get("criteria", BaseCriteria())
    tools = [t for t in rsp.ranking if can_be_used(crit, t)]
    return cast(_Tool, tools[0])

async def tool_online_help(state: AgentState) -> AgentState:
    thought = state.get("thought", "__ i do not have any question __")
    response = await AGATHA_HELP.ainvoke(input=thought)

    return {
        "call_tool": "Online Help Resources",
        "call_request": thought,
        "call_data": response,
    } # type: ignore

async def step_respond(state: AgentState) -> AgentState:
    context = _build_context(state)
    rsp = await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + [ respond.format(context=context) ]
    )
    return {"messages": AIMessage(rsp), "output": rsp} # type: ignore

async def step_observation(state: AgentState) -> AgentState:
    """Deliver the raw data as an AI message."""

    context   = _build_context(state)
    scratch   = state.get("scratch", "")
    objective = state.get("thought", "")

    call_tool = state.get("call_tool", "__ no tool was used __")
    call_request = to_json(
        state.get("call_request", "__ no data found __"),
        indent=4,
        by_alias=False,
        exclude_none=True,
        bytes_mode="utf8"
    ).decode("utf8")
    call_data = to_json(
        state.get("call_data", "__ no data found __"),
        indent=4,
        by_alias=False,
        exclude_none=True,
        bytes_mode="utf8"
    ).decode("utf8")

    summary  =  await (
        (LLM | StrOutputParser())
        .ainvoke( state["messages"] + [ 
            summarize.format(
                context = context,
                call_tool = call_tool,
                call_request = call_request,
                call_data = call_data,
            ) 
        ] )
    )

    scratch = reasoning_step.format(
        scratch=scratch,
        thought=objective,
        call_tool=call_tool,
        call_request=call_request,
        summary=summary,
    )

    return { "scratch": scratch.strip(), "thought": None, "call_data": None } # type: ignore

