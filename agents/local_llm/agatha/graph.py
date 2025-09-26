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

from ..simplified.schemas import (
    AvailableData
)

AGATHA_HELP = agatha_help()

async def initialize_conversation(state: AgentState) -> AgentState:
    messages = [ 
        system_prompt,
        HumanMessage(state["input"])
    ]

    available_data = await (
        LLM.with_structured_output(AvailableData)
        .ainvoke(
            [ 
                system_prompt, 
                HumanMessage(
                f"""
                # USER REQUEST
                {state["input"]}

                # INSTUCTIONS
                Formalize the data that has been given to you. 
                
                Whenever you mention a municipality name, it MUST USE either 
                the French or the Dutch spelling of that name.

                When a data is unknown, just leave it out. The goal is to formalize only what you know.

                
                ## Examples

                >>> I would like to find the birth certificate of Wim Van Piperzeel
                >>> who was born in Sterrebeek in the early 1800.
                ```
                {{
                    "municipality_name": "Sterrebeek",
                    "type_of_record": "Birth certificates",
                    "people": [
                        {{ "first_name": "Wim", "family_name": "Van Piperzeel", "role": "Child"}}
                    ],
                    "from_year": 1800,
                    "until_year": 1810,
                }}
                ```

                >>> I would like to find the marriage notice of my great grand father Olivier Outsiplout.
                ```
                {{
                    "type_of_record": "Notices of marriage",
                    "people": [
                        {{ "first_name": "Olivier", "family_name": "Olivier Outsiplout", "role": "Groom"}}
                    ],
                }}
                ```
                """
                ),
            ]
        )
    )

    return { # type: ignore
        "messages": messages,
        "scratch" : "",
        "available_data": available_data,
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
    available_data = state.get("available_data", AvailableData())
    tool_descr, tool_names = available_data.available_tools()
    rsp = await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + [ what_information.format(
            scratch=scratch,
            tools_descr=tool_descr,
            tool_names=tool_names,
        ) ]
    )
    return {"n": n+1, "thought": rsp} # type: ignore

_Source = Literal[
    "Analyses of Records / Free Search", 
    "Analyses of Records / Search Person", 
    "Genealogical sources / Church Registers",
    "Genealogical sources / Civil State Registers",
    "Online Help Resources", 
    "Respond",
]

async def cond_what_source(state: AgentState) -> _Source:
    thought = state.get("thought", "== I dont need anything ==")
    scratch = state.get("scratch", "")
    available_data = state.get("available_data", AvailableData())
    tool_descr, tool_names = available_data.available_tools()
    tool_descr += "* 'Respond' if you think you are ready to respond to the user"
    tool_names.append("Respond")
    rsp = await (
        (LLM | StrOutputParser())
            .ainvoke(state["messages"] + [ what_source.format(
                scratch=scratch,
                tool_descr=tool_descr,
                tool_names=tool_names,
                thought=thought
            ) ])
    )
    return cast(_Source, rsp.strip())

async def step_help(state: AgentState) -> AgentState:
    thought = state.get("thought", "__ i do not have any question __")
    response = await AGATHA_HELP.ainvoke(input=thought)

    return {
        "call_tool": "Online Help Resources",
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
    
    try:
        substate = await SEARCH_IN_ANALYSES_OF_RECORDS.ainvoke({"messages": state["messages"] + [prompt]}) # type: ignore
        return {
            "call_tool": substate.get("call_tool"),
            "call_request": substate.get("call_request"),
            "call_data": substate.get("call_data"),
        } # type: ignore
    except Exception as e:
        return {
            "call_tool": "Analyses of records",
            "call_request": f"This tool cannot be used right now because: {e.args}",
            "call_data": f"This tool cannot be used right now because: {e.args}",
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

    try:
        substate = await SEARCH_IN_GENEALOGIC_SOURCES.ainvoke({"messages": state["messages"] + [prompt]}) # type: ignore

        return {
            "call_tool": substate.get("call_tool"),
            "call_request": substate.get("call_request"),
            "call_data": substate.get("call_data"),
        } # type: ignore
    except Exception as e:
        return {
            "call_tool": "Genealogical Sources",
            "call_request": f"This tool cannot be used right now because: {e.args}",
            "call_data": f"This tool cannot be used right now because: {e.args}",
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
    
======================================================================================
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
        .add_node("Respond", step_respond)
        .add_edge("Respond", END)
        # yes
        .add_node("what_info", step_what_info)
        .add_conditional_edges("what_info", cond_what_source)
        # analyses
        .add_node("Analyses of Records / Free Search", step_analyses_of_records)
        .add_edge("Analyses of Records / Free Search", "observation")
        # search person
        .add_node("Analyses of Records / Search Person", step_analyses_of_records)
        .add_edge("Analyses of Records / Search Person", "observation")
        # church
        .add_node("Genealogical sources / Church Registers", step_genealogy)
        .add_edge("Genealogical sources / Church Registers", "observation")
        # civil
        .add_node("Genealogical sources / Civil State Registers", step_genealogy)
        .add_edge("Genealogical sources / Civil State Registers", "observation")
        # help
        .add_node("Online Help Resources", step_help)
        .add_edge("Online Help Resources", "observation")
        #
        .compile()
)