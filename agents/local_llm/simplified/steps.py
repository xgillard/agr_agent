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
from pydantic_core import (
    to_json,
)
from pydantic import (
    BaseModel,
)
from ...tools.agatha_common import (
    Municipality,
)
from ...tools.agatha_help import (
    agatha_help,
)
from ...tools.analyses_of_records import (
    AnalysesFreeSearchRequest,
    AnalysesSearchPersonRequest,
    PersonCriterion,
    free_search_in_analyses_of_records,
    search_person_in_analyses_of_records,
)
from ...tools.genealogy import (
    AJAX_URL,
    CivilActType,
    ParishActType,
    genealogy_search_church_registers_prior_to_1796,
    genealogy_search_civil_state_registers,
)
from ...tools.generated import (
    AnalysesActType,
)
from ..common.llm import (
    LLM,
)
from .prompts import (
    formalize,
    respond,
    search_terms,
    summarize,
    system_prompt,
    what_objective,
    what_tool,
)
from .schemas import (
    AgentState,
    AvailableData,
    PersonData,
)

AGATHA_HELP = agatha_help()

async def step_initialize(state: AgentState) -> AgentState:
    messages = [ 
        system_prompt,
        HumanMessage(state["input"])
    ]

    return { # type: ignore
        "messages": messages,
    }

async def step_formalize(state: AgentState) -> AgentState:
    scratch   = state.get("scratch")
    available = state.get("available_data")

    context   = ""
    if scratch is not None:
        context += f"\n< Context >\n{scratch}\n</ Context >\n"
    
    if available is not None:
        context += f"\n< Previously >\n{available.model_dump_json(exclude_none=True, indent=4)}\n</ Previously >\n"
    
    available = cast(AvailableData, await (
        LLM.with_structured_output(AvailableData)
        .ainvoke(state["messages"] + [formalize.format(input=context)])
    ))

    return { # type: ignore
        "available_data": available, 
    }


async def step_set_objective(state: AgentState) -> AgentState:
    n = state.get("n", 0) 
    scratch = state.get("scratch", "")
    available_data = state.get("available_data", AvailableData())
    tool_descr, tool_names = available_data.available_tools()
    rsp = await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + [ what_objective.format(
            scratch=scratch,
            available_data=available_data.model_dump_json(exclude_none=True, indent=4),
            tools_descr=tool_descr,
            tool_names=tool_names,
        ) ]
    )
    return {"n": n+1, "thought": rsp} # type: ignore


_Tool = Literal[
    "Analyses of Records / Free Search", 
    "Analyses of Records / Search Person", 
    "Genealogical sources / Church Registers",
    "Genealogical sources / Civil State Registers",
    "Online Help Resources", 
    "Respond",
]

class ToolChoice(BaseModel):
    tool_name: _Tool

async def cond_what_tool(state: AgentState) -> _Tool:
    # circuit breaker
    n = state.get("n", 0) 
    if n >= 5:
        return "Respond"
    
    scratch = state.get("scratch", "")
    thought = state.get("thought", "I am done.")
    #
    available_data = state.get("available_data", AvailableData())
    tool_descr, tool_names = available_data.available_tools()
    #
    tool_descr += "* 'Respond' if you think you are ready to respond to the user"
    tool_names.append("Respond")

    rsp = cast(ToolChoice, await (
        LLM .with_structured_output(ToolChoice)
            .ainvoke(state["messages"] + [ what_tool.format(
                scratch=scratch,
                tool_descr=tool_descr,
                tool_names=tool_names,
                thought=thought
            ) ])
    ))
    return cast(_Tool, rsp.tool_name)

async def tool_genea_church(state: AgentState) -> AgentState:
    data = cast(AvailableData, state.get("available_data"))

    act_types = None

    match data.type_of_record:
        case (AnalysesActType.BIRTH_CERTIFICATES 
            | AnalysesActType.BAPTISM_CERTIFICATES 
            | AnalysesActType.BIRTH_ANNOUNCEMENT):
            act_types = [ParishActType.BAPTISM]

        case (AnalysesActType.NOTICES_OF_MARRIAGE
            | AnalysesActType.MARRIAGE_ANNOUNCEMENTS
            | AnalysesActType.MARRIAGE_CERTIFICATES
            | AnalysesActType.MARRIAGE_SETTLEMENT):
            act_types = [ParishActType.WEDDING]

        case (AnalysesActType.FUNERAL_CERTIFICATES
            | AnalysesActType.DEATH_CERTIFICATES
            | AnalysesActType.DEATH_NOTICE
            | AnalysesActType.MORTUARY_AND_MOURNING_CARD
            | AnalysesActType.MORTUARY_INVENTORY):
            act_types = [ParishActType.DEATH]

    municipality = Municipality.by_name(data.municipality_name, AJAX_URL, return_single_best_match=True)
    parishes = municipality.parishes(AJAX_URL)

    if data.parish_name is not None:
        parishes = [ p for p in parishes if data.parish_name in p.place_name.lower() ]
    
    call_request = dict(
        municipality=municipality,
        parishes=parishes,
        act_types=act_types,
        start_year=data.from_year,
        end_year=data.until_year,
        #other_types=other_types,
        #index_types=,
        #period_selector=
    )

    unk_mun = "Unknown municipality. Did you use french or dutch spelling ?"
    call_data = genealogy_search_church_registers_prior_to_1796(**call_request) if municipality is not None else unk_mun

    return {
        "call_tool": "Genealogical sources / Church Registers",
        "call_request": call_request,
        "call_data": call_data,
    }

async def tool_genea_civil(state: AgentState) -> AgentState:
    data = cast(AvailableData, state.get("available_data"))

    act_types = None

    match data.type_of_record:
        case (AnalysesActType.BIRTH_CERTIFICATES 
            | AnalysesActType.BIRTH_ANNOUNCEMENT):
            act_types = [CivilActType.BAPTISM]

        case (AnalysesActType.NOTICES_OF_MARRIAGE
            | AnalysesActType.MARRIAGE_ANNOUNCEMENTS
            | AnalysesActType.MARRIAGE_CERTIFICATES
            | AnalysesActType.MARRIAGE_SETTLEMENT):
            act_types = [CivilActType.WEDDING]

        case (AnalysesActType.FUNERAL_CERTIFICATES
            | AnalysesActType.DEATH_CERTIFICATES
            | AnalysesActType.DEATH_NOTICE
            | AnalysesActType.MORTUARY_AND_MOURNING_CARD
            | AnalysesActType.MORTUARY_INVENTORY
            | AnalysesActType.JUDICIAL_DEATH_DECLARATION):
            act_types = [CivilActType.DEATH]

    municipality = Municipality.by_name(data.municipality_name, AJAX_URL, return_single_best_match=True)
    call_request = dict(
        municipality=municipality,
        act_types=act_types,
        start_year=data.from_year,
        end_year=data.until_year,
        #other_types=other_types,
        #index_types=,
        #period_selector=
    )

    unk_mun = "Unknown municipality. Did you use french or dutch spelling ?"
    call_data = genealogy_search_civil_state_registers(**call_request) if municipality is not None else unk_mun
    
    return {
        "call_tool": "Genealogical sources / Civil State Registers",
        "call_request": call_request,
        "call_data": call_data,
    }

async def tool_analyses_free_search(state: AgentState) -> AgentState:
    data = cast(AvailableData, state.get("available_data"))

    terms = await (
        (LLM | StrOutputParser())
            .ainvoke(state["messages"] + [search_terms])
    )

    call_request = AnalysesFreeSearchRequest(
        search_terms=terms,
        location=data.municipality_name,
        start_year=data.from_year,
        end_year=data.until_year,
        act_type=data.type_of_record,
        # project
    )

    call_data = free_search_in_analyses_of_records(call_request)
    
    return {
        "call_tool": "Analyses of Records / Free Search",
        "call_request": call_request,
        "call_data": call_data,
    }

def __as_criterion(p: PersonData) -> PersonCriterion:
    return PersonCriterion(
        family_name=p.family_name,
        first_name=p.first_name,
        profession=p.profession,
        role=p.role,
    )

async def tool_analyses_search_person(state: AgentState) -> AgentState:
    data = cast(AvailableData, state.get("available_data"))


    persons = [ __as_criterion(p) for p in data.people if p]
    call_request = AnalysesSearchPersonRequest(
        persons=persons,
        location=data.municipality_name,
        start_year=data.from_year,
        end_year=data.until_year,
        act_type=data.type_of_record,
        #project=,
    )

    call_data = search_person_in_analyses_of_records(call_request)
    
    return {
        "call_tool": "Analyses of Records / Search Person",
        "call_request": call_request,
        "call_data": call_data,
    }

async def tool_online_help(state: AgentState) -> AgentState:
    thought = state.get("thought", "__ i do not have any question __")
    response = await AGATHA_HELP.ainvoke(input=thought)

    return {
        "call_tool": "Online Help Resources",
        "call_request": thought,
        "call_data": response,
    } # type: ignore

async def step_respond(state: AgentState) -> AgentState:
    scratch = state.get("scratch", "I just know the answer")
    rsp = await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + [ respond.format(scratch=scratch) ]
    )
    return {"messages": AIMessage(rsp), "output": rsp} # type: ignore

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

Objective: {thought}
Action: I have used {call_tool} as follows
{call_request}
Result: {summary}

    """

    return { "scratch": scratch, "thought": None, "call_data": None } # type: ignore

