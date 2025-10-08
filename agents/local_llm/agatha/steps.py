"""steps that implements the simplified agatha workflow."""

from textwrap import (
    indent,
)
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
    AnalysesActRole,
    AnalysesActType,
)
from ..common.llm import (
    LLM,
)
from .prompts import (
    analyze_tool,
    enough_information,
    reasoning_step,
    respond,
    search_terms,
    select_tool,
    summarize,
    system_prompt,
    what_objective,
)
from .schemas import (
    AgentState,
    AvailableData,
    PersonData,
)

AGATHA_HELP = agatha_help()

def step_initialize(state: AgentState) -> AgentState:
    messages  = state.get("messages", [])
    if not messages:
        messages = [system_prompt]

    messages += [ HumanMessage(state["input"]) ]
    return { # type: ignore
        "input": state["input"],
        "messages": messages,
    }


def cond_enough_info(state: AgentState) -> Literal["Respond", "Set Objective"]:
    # circuit breaker
    n = state.get("n", 0) 
    if n >= 5:
        return "Respond"
    
    context = _build_context(state)
    response= (
        LLM.with_structured_output(
            {"properties": {"choice": {"enum": ["yes", "no"]}}}
        )
        .invoke(state["messages"] + [
            enough_information.format(
                context=context
            )
        ])
    )
    return "Respond" if response.get("choice", "no").lower() == "no" else "Set Objective"


def _build_context(state: AgentState) -> str:
    """Build a self-contained context for use in prompts."""

    user_rq   = state.get("input")
    scratch   = state.get("scratch")
    objective = state.get("thought")
    
    context = f"# User Request\n{user_rq}\n"
    
    if scratch:
        context += f"\n# Research\n{scratch}\n"
    
    if objective:
        context += f"\n# Current Objective\n{objective}\n"

    if context:
        context = f"\n< Context >\n{context}\n</ Context >\n"
    
    return context

def step_set_objective(state: AgentState) -> AgentState:
    n = state.get("n", 0) 

    rsp =  (LLM | StrOutputParser()).invoke(
        [ what_objective.format(
            context     = _build_context(state),
            tools_descr = AvailableData.all_tools(),
        ) ]
    )
    return {"n": n+1, "thought": rsp} # type: ignore


_Tool = Literal[
    "Analyses of Records / Free Search", 
    "Analyses of Records / Search Person", 
    "Genealogical sources / Church Registers",
    "Genealogical sources / Civil State Registers",
    "Online Help Resources",
]

class ToolChoice(BaseModel):
    tool_name: _Tool

def cond_what_tool(state: AgentState) -> _Tool:
    context = _build_context(state)
    #
    available_data = state.get("available_data", AvailableData())
    tool_descr, tool_names = available_data.available_tools()

    evaluation = (LLM | StrOutputParser()).invoke(
        state["messages"] + [
            analyze_tool.format(
                context=context,
                tool_descr=tool_descr,
            )
        ]
    )
    rsp = cast(ToolChoice,  (
        LLM .with_structured_output(ToolChoice)
            .invoke(
            [ select_tool.format(
                context=context,
                tool_descr=tool_descr,
                evaluation=evaluation,
                tool_names=tool_names,
            ) ])
    ))
    return cast(_Tool, rsp.tool_name)

def tool_genea_church(state: AgentState) -> AgentState:
    data = cast(AvailableData, state.get("available_data"))

    act_types = None

    match data.type_of_record_code:
        case (AnalysesActType.BIRTH_CERTIFICATES.code 
            | AnalysesActType.BAPTISM_CERTIFICATES.code 
            | AnalysesActType.BIRTH_ANNOUNCEMENT.code):
            act_types = [ParishActType.BAPTISM]

        case (AnalysesActType.NOTICES_OF_MARRIAGE.code
            | AnalysesActType.MARRIAGE_ANNOUNCEMENTS.code
            | AnalysesActType.MARRIAGE_CERTIFICATES.code
            | AnalysesActType.MARRIAGE_SETTLEMENT.code):
            act_types = [ParishActType.WEDDING]

        case (AnalysesActType.FUNERAL_CERTIFICATES.code
            | AnalysesActType.DEATH_CERTIFICATES.code
            | AnalysesActType.DEATH_NOTICE.code
            | AnalysesActType.MORTUARY_AND_MOURNING_CARD.code
            | AnalysesActType.MORTUARY_INVENTORY.code):
            act_types = [ParishActType.DEATH]

    assert(data.municipality_name is not None)
    municipality = Municipality.by_name(name=data.municipality_name, ajax=AJAX_URL, return_single_best_match=True)
    parishes = municipality.parishes(AJAX_URL) if municipality is not None else []

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

    if municipality is None:
        return { # type: ignore
            "call_tool": "Genealogical sources / Church Registers",
            "call_request": call_request,
            "call_data": "Unknown municipality. Did you use french or dutch spelling ?",
        }
    else:
        call_data = genealogy_search_church_registers_prior_to_1796(**call_request) # type: ignore
        return { # type: ignore
            "call_tool": "Genealogical sources / Church Registers",
            "call_request": call_request,
            "call_data": call_data,
        }

def tool_genea_civil(state: AgentState) -> AgentState:
    data = cast(AvailableData, state.get("available_data"))

    act_types = None

    match data.type_of_record_code:
        case (AnalysesActType.BIRTH_CERTIFICATES.code 
            | AnalysesActType.BIRTH_ANNOUNCEMENT.code):
            act_types = [CivilActType.BIRTH]

        case (AnalysesActType.NOTICES_OF_MARRIAGE.code
            | AnalysesActType.MARRIAGE_ANNOUNCEMENTS.code
            | AnalysesActType.MARRIAGE_CERTIFICATES.code
            | AnalysesActType.MARRIAGE_SETTLEMENT.code):
            act_types = [CivilActType.WEDDING]

        case (AnalysesActType.FUNERAL_CERTIFICATES.code
            | AnalysesActType.DEATH_CERTIFICATES.code
            | AnalysesActType.DEATH_NOTICE.code
            | AnalysesActType.MORTUARY_AND_MOURNING_CARD.code
            | AnalysesActType.MORTUARY_INVENTORY.code
            | AnalysesActType.JUDICIAL_DEATH_DECLARATION.code):
            act_types = [CivilActType.DEATH]

    assert(data.municipality_name is not None)
    municipality = Municipality.by_name(name=data.municipality_name, ajax=AJAX_URL, return_single_best_match=True)
    call_request = dict(
        municipality=municipality,
        act_types=act_types,
        start_year=data.from_year,
        end_year=data.until_year,
        #other_types=other_types,
        #index_types=,
        #period_selector=
    )

    if municipality is None:
        return { # type: ignore
            "call_tool": "Genealogical sources / Civil State Registers",
            "call_request": call_request,
            "call_data": "Unknown municipality. Did you use french or dutch spelling ?",
        }
    else:
        call_data = genealogy_search_civil_state_registers(**call_request) # type: ignore
        return { # type: ignore
            "call_tool": "Genealogical sources / Civil State Registers",
            "call_request": call_request,
            "call_data": call_data,
        }

def tool_analyses_free_search(state: AgentState) -> AgentState:
    data = cast(AvailableData, state.get("available_data"))
    context = _build_context(state)

    terms =  (
        (LLM | StrOutputParser())
            .invoke([search_terms.format(context=context)])
    )

    call_request = AnalysesFreeSearchRequest(
        search_terms=terms,
        location=data.municipality_name,
        start_year=data.from_year,
        end_year=data.until_year,
        act_type=AnalysesActType.from_code(data.type_of_record_code) if data.type_of_record_code is not None else None,
        # project
    )

    call_data = free_search_in_analyses_of_records(call_request)
    
    return { # type: ignore
        "call_tool": "Analyses of Records / Free Search",
        "call_request": call_request,
        "call_data": call_data,
    }

def __as_criterion(p: PersonData) -> PersonCriterion:
    return PersonCriterion(
        family_name=p.family_name,
        first_name=p.first_name,
        profession=p.profession,
        role=AnalysesActRole.from_code(p.role_code) if p.role_code is not None else None,
    )

def tool_analyses_search_person(state: AgentState) -> AgentState:
    data = cast(AvailableData, state.get("available_data"))

    persons = [ __as_criterion(p) for p in data.people if p] if data.people else []
    call_request = AnalysesSearchPersonRequest(
        persons=persons,
        location=data.municipality_name,
        start_year=data.from_year,
        end_year=data.until_year,
        act_type=AnalysesActType.from_code(data.type_of_record_code) if data.type_of_record_code is not None else None,
        #project=,
    )

    call_data = search_person_in_analyses_of_records(call_request)
    
    return { # type: ignore
        "call_tool": "Analyses of Records / Search Person",
        "call_request": call_request,
        "call_data": call_data,
    }

def tool_online_help(state: AgentState) -> AgentState:
    thought = state.get("thought", "__ i do not have any question __")
    response =  AGATHA_HELP.invoke(input=thought)

    return {
        "call_tool": "Online Help Resources",
        "call_request": thought,
        "call_data": response,
    } # type: ignore

def step_respond(state: AgentState) -> AgentState:
    context = _build_context(state)
    rsp =  (LLM | StrOutputParser()).invoke(
        [ respond.format(context=context) ]
    )
    return {"messages": AIMessage(rsp), "output": rsp} # type: ignore

def step_observation(state: AgentState) -> AgentState:
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

    summary  =  (
        (LLM | StrOutputParser())
        .invoke( [ 
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

    return { "scratch": scratch, "thought": None, "call_data": None } # type: ignore

