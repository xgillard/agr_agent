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


async def initialize_conversation(state: AgentState) -> AgentState:
    return { # type: ignore
        "messages": [ 
            system_prompt,
            HumanMessage(state["input"])
        ]
    }


_Decision = Literal["respond", "what_info"]
class YesNoChoice(SingleChoice[YesNo]):
    pass
async def cond_decide(state: AgentState) -> _Decision:
    if state.get("n", 0) > 5: # circuit breaker
        return "respond"
    
    scratch = state.get("scratch", "")
    enough = cast(YesNoChoice, await (
        LLM.with_structured_output(YesNoChoice)
            .ainvoke(state["messages"] + [ decide.format(scratch=scratch) ])
    ))

    match enough.choice:
        case YesNo.YES:
            return "what_info"
        case YesNo.NO:
            return "respond"


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

_Source = Literal["analyses_of_records", "digitized_registers", "help_resources"]
class DSChoice(SingleChoice[DataSource]):
    pass
async def cond_what_source(state: AgentState) -> _Source:
    thought = state.get("thought", "== I dont need anything ==")
    rsp = cast(DSChoice, await (
        LLM.with_structured_output(DSChoice)
            .ainvoke(state["messages"] + [ what_source.format(thought=thought) ])
    ))
    match rsp.choice:
        case DataSource.ANALYSES_OF_RECORDS: 
            return "analyses_of_records"
        case DataSource.DIGITIZED_REGISTERS:
            return "digitized_registers"
        case DataSource.HELP_RESOURCES:
            return "help_resources"

async def step_help(state: AgentState) -> AgentState:
    # FIXME: TODO
    return {"messages": AIMessage("The help section was unavailable")} # type: ignore

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
    return {"call_data": substate.get("call_data", None)} # type: ignore

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
    return {"call_data": substate.get("call_data", None)} # type: ignore

async def step_observation(state: AgentState) -> AgentState:
    """Deliver the raw data as an AI message."""

    scratch = state.get("scratch", "")
    thought = state.get("thought", "I am done")

    raw_data = to_json(
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
                raw_data = raw_data,
            ) 
        ] )
    )

    scratch = f"{scratch}\n{summary}"
    return { "scratch": scratch, "thought": None, "call_data": None } # type: ignore

ASK_AGATHA = (
    StateGraph(AgentState)
        .add_edge(START, "init")
        #
        .add_node("init", initialize_conversation)
        .add_conditional_edges("init", cond_decide)
        # observation
        .add_node("observation", step_observation)
        .add_conditional_edges("observation", cond_decide)
        # no
        .add_node("respond", step_respond)
        .add_edge("respond", END)
        # yes
        .add_node("what_info", step_what_info)
        .add_conditional_edges("what_info", cond_what_source)
        # analyses
        .add_node("analyses_of_records", step_analyses_of_records)
        .add_edge("analyses_of_records", "observation")
        # digitized
        .add_node("digitized_registers", step_genealogy)
        .add_edge("digitized_registers", "observation")
        # help
        .add_node("help_resources", step_help)
        .add_edge("help_resources", "observation")
        #
        .compile()
)