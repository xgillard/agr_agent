"""Actual implementation of the react model."""

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
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from pydantic_core import (
    to_json,
)

from ...tools.agatha_help import (
    agatha_help,
)
from ..analyses_of_records.graph import (
    SEARCH_IN_ANALYSES_OF_RECORDS,
)
from ..common.llm import (
    LLM,
)
from ..common.schemas import (
    SingleChoice,
)
from ..genealogical_sources.graph import (
    SEARCH_IN_GENEALOGIC_SOURCES,
)
from .prompts import (
    decide,
    respond,
    summarize,
    system_prompt,
    what_information,
    what_source,
)
from .schemas import (
    AgentState,
    DataSource,
    YesNo,
)

AGATHA_HELP = agatha_help()

async def initialize_conversation(state: AgentState) -> AgentState:
    messages = [ 
        system_prompt,
        HumanMessage(state["input"])
    ]

    plan = await (LLM | StrOutputParser()).ainvoke(
        messages + [
            AIMessage(
            """
            Considering the tools available to you, make a step-by-step 
            plan of how you would address the user's request in order to
            deliver a high quality, conclusive answer.
            """
            )
        ]
    )

    return { # type: ignore
        "messages": messages,
        "scratch" : f"\n< Plan >\n{plan}\n</ Plan >\n",
    }

async def step_respond(state: AgentState) -> AgentState:
    scratch = state.get("scratch", "I just know the answer")
    rsp = await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + [ respond.format(scratch=scratch) ]
    )
    return {"messages": AIMessage(rsp), "output": rsp} # type: ignore


async def step_what_info(state: AgentState) -> AgentState:
    n = state.get("n", 0) 
    scratch = state.get("scratch", "")
    rsp = await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + [ what_information.format(scratch=scratch) ]
    )
    return {"n": n+1, "thought": rsp} # type: ignore

_Source = Literal["Analyses of records", "Genealogical sources", "Help Resources", "respond"]
class DSChoice(SingleChoice[DataSource]):
    pass
async def cond_what_source(state: AgentState) -> _Source:
    thought = state.get("thought", "== I dont need anything ==")

    if thought.startswith("I want to find the help section"):
        return "Help Resources"
    elif thought.startswith("I want to find the FAQ section"):
        return "Help Resources"
    elif thought.startswith("I want to find the details of "):
        return "Analyses of records"
    elif thought.startswith("I want to find a digitized scan of"):
        return "Genealogical sources"
    elif thought.startswith("I want to stop and send my definitive response to the user"):
        return "respond"
    
    rsp = cast(DSChoice, await (
        LLM.with_structured_output(DSChoice)
            .ainvoke(state["messages"] + [ what_source.format(thought=thought) ])
    ))
    match rsp.choice:
        case DataSource.ANALYSES_OF_RECORDS: 
            return "Analyses of records"
        case DataSource.DIGITIZED_REGISTERS:
            return "Genealogical sources"
        case DataSource.HELP_RESOURCES:
            return "Help Resources"

async def step_help(state: AgentState) -> AgentState:
    thought = state.get("thought", "__ i do not have any question __")
    response = await AGATHA_HELP.ainvoke(input=thought)

    return {
        "call_tool": "Help Resources",
        "call_request": thought,
        "call_data": response,
    } # type: ignore

async def step_analyses_of_records(state: AgentState) -> AgentState:
    thought = state.get("thought", "")
    context = state.get("scratch", "")

    prompt = HumanMessage(f"""
    < Context >
    Here is my reasoning so far:
    {context}
    </ Context>
    < Goal >{thought}</ Goal >""")

    substate = await SEARCH_IN_ANALYSES_OF_RECORDS.ainvoke({"messages": state["messages"] + [prompt]}) # type: ignore
    return {
        "call_tool": substate.get("call_tool"),
        "call_request": substate.get("call_request"),
        "call_data": substate.get("call_data"),
    } # type: ignore

async def step_genealogy(state: AgentState) -> AgentState:
    thought = state.get("thought", "")
    context = state.get("scratch", "")

    prompt = HumanMessage(f"""
    < Context >
    Here is my reasoning so far:
    {context}
    </ Context>
    < Goal >{thought}</ Goal >""")

    substate = await SEARCH_IN_GENEALOGIC_SOURCES.ainvoke({"messages": state["messages"] + [prompt]}) # type: ignore
    return {
        "call_tool": substate.get("call_tool"),
        "call_request": substate.get("call_request"),
        "call_data": substate.get("call_data"),
    } # type: ignore

async def step_observation(state: AgentState) -> AgentState:
    """Deliver the raw data as an AI message."""

    scratch = state.get("scratch", "")
    thought = state.get("thought", "I am done")

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

    summary  = await (
        (LLM | StrOutputParser())
        .ainvoke( state["messages"] + [ 
            summarize.format(
                scratch = scratch,
                thought = thought,
                call_tool = call_tool,
                call_request = call_request,
                call_data = call_data,
            ) 
        ] )
    )

    scratch = f"""{scratch}

Thought: {thought}
Action: I have used {call_tool} as follows
{call_request}
Observation: {summary}
    
    """

    return { "scratch": scratch, "thought": None, "call_data": None } # type: ignore

ASK_AGATHA = (
    StateGraph(AgentState)
        .add_edge(START, "init")
        #
        .add_node("init", initialize_conversation)
        .add_edge("init", "what_info")
        # observation
        .add_node("observation", step_observation)
        .add_edge("observation", "what_info")
        # no
        .add_node("respond", step_respond)
        .add_edge("respond", END)
        # yes
        .add_node("what_info", step_what_info)
        .add_conditional_edges("what_info", cond_what_source)
        # analyses
        .add_node("Analyses of records", step_analyses_of_records)
        .add_edge("Analyses of records", "observation")
        # digitized
        .add_node("Genealogical sources", step_genealogy)
        .add_edge("Genealogical sources", "observation")
        # help
        .add_node("Help Resources", step_help)
        .add_edge("Help Resources", "observation")
        #
        .compile()
)