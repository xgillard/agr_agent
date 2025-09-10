"""Implement the logic to call a search_person_in_analyses_of_records as if the agent went through a wizzard."""

import asyncio
from typing import cast

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from tools.analyses_of_records import (
    AnalysesSearchPersonRequest,
    PersonCriterion,
    search_person_in_analyses_of_records,
)

from ..common.llm import LLM
from ..common.steps import (
    step_deliver_raw_data,
    step_fill_location,
    step_fill_period,
    step_fill_project,
    step_fill_record_type,
)
from .prompts import (
    family_name,
    first_name,
    job_name,
    list_known_people,
    role_name,
)
from .schemas import (
    AddPersonWizzardState,
    FamilyName,
    FirstName,
    ListOfPeople,
    Profession,
    RoleChoice,
    SearchPersonWizzardState,
)

###### ADD PERSON WIZZARD ####################################################

async def step_fill_family_name(state: AddPersonWizzardState) -> AddPersonWizzardState:
    rsp = cast(FamilyName, 
        await (LLM.with_structured_output(FamilyName))
        .ainvoke( 
            state["messages"] + 
            [ HumanMessage(family_name.format(full_name=state["full_name"])) ]
        )
    )
    return {"family_name": rsp.family_name} # type: ignore

async def step_fill_first_name(state: AddPersonWizzardState) -> AddPersonWizzardState:
    rsp = cast(FirstName,
        await (LLM.with_structured_output(FirstName))
        .ainvoke( 
            state["messages"] + 
            [ HumanMessage(first_name.format(full_name=state["full_name"])) ]
        )
    )
    return {"first_name": rsp.first_name} # type: ignore

async def step_fill_job(state: AddPersonWizzardState) -> AddPersonWizzardState:
    rsp = cast(Profession,
        await (LLM.with_structured_output(Profession))
        .ainvoke( 
            state["messages"] + 
            [ HumanMessage(job_name.format(full_name=state["full_name"])) ]
        )
    )
    return {"profession": rsp.profession} # type: ignore

async def step_fill_role(state: AddPersonWizzardState) -> AddPersonWizzardState:
    rsp = cast(RoleChoice,
        await (LLM.with_structured_output(RoleChoice))
        .ainvoke( 
            state["messages"] + 
            [ HumanMessage(role_name.format(full_name=state["full_name"])) ]
        )
    )
    return {"role": rsp.role} if rsp else {} # type: ignore

__ADD_PERSON_WIZZARD = (
    StateGraph(AddPersonWizzardState)
        .add_node("fill_family_name", step_fill_family_name)
        .add_node("fill_first_name", step_fill_first_name)
        .add_node("fill_job", step_fill_job)
        .add_node("fill_role", step_fill_role)
        #
        .add_edge(START, "fill_family_name")
        .add_edge(START, "fill_first_name")
        .add_edge(START, "fill_job")
        .add_edge(START, "fill_role")
        .add_edge([
            "fill_family_name",
            "fill_first_name",
            "fill_job",
            "fill_role",
        ], END)
        #
        .compile()
)

###### SEARCH PERSON WIZZARD ####################################################
async def step_list_people(state: SearchPersonWizzardState) -> SearchPersonWizzardState:
    """List the people."""

    known_people = cast(ListOfPeople,
        await LLM
        .with_structured_output(ListOfPeople)
        .ainvoke( state["messages"] + [ HumanMessage( list_known_people ) ])
    )
    return { "known_people": known_people.list_of_names } # type: ignore

async def _substep_add_person(person: str, messages: list) -> PersonCriterion:
    """Run the add person wizzard for one single person.
    
    Args:
        person (str): the name or ... whatever means the llm has used to identify someone.
        messages (list): the outer conversation between user and llm.
        
    Returns:
        PersonCriterion: a means to encode that person into a search request.
    """

    sub = AddPersonWizzardState(full_name=person, messages=messages)
    sub = cast(AddPersonWizzardState, 
               await __ADD_PERSON_WIZZARD.ainvoke(sub))  # type: ignore[arg-type]
    return PersonCriterion(
        family_name=sub["family_name"],
        first_name=sub["first_name"],
        profession=sub["profession"],
        role=sub["role"],
    )

async def step_add_pers_wizzard(state: SearchPersonWizzardState) -> SearchPersonWizzardState:
    """Goes through all the steps of the add person wizard state"""
    outer = state["messages"]
    tasks = [_substep_add_person(p, outer) for p in state["known_people"]]
    persons = await asyncio.gather( *tasks )
    return {"persons": persons} # type: ignore

async def step_call_tool(state: SearchPersonWizzardState) -> SearchPersonWizzardState:
    """Performs a call to the Agatha tool"""

    request = AnalysesSearchPersonRequest(
        persons=state["persons"],
        location=state["location"],
        period=state["period_selector"],
        start_date=state["start_date"],
        end_date=state["end_date"],
        act_type=state["act_type"],
        project=state["project"],
    )
    call = search_person_in_analyses_of_records(request)
    return {"call_data": call} # type: ignore

SEARCH_PERSON_IN_ANALYSES_OF_RECORDS = (
    StateGraph(SearchPersonWizzardState)
        .add_node("list_people", step_list_people)
        .add_node("add_persons", step_add_pers_wizzard)
        .add_node("fill_location", step_fill_location)
        .add_node("fill_period", step_fill_period)
        .add_node("fill_act_type", step_fill_record_type)
        .add_node("fill_project", step_fill_project)
        .add_node("call_tool", step_call_tool)
        .add_node("deliver_raw_data", step_deliver_raw_data)
        #
        .add_edge(START, "list_people")
        .add_edge(START, "fill_location")
        .add_edge(START, "fill_period")
        .add_edge(START, "fill_act_type")
        .add_edge(START, "fill_project")
        .add_edge("list_people", "add_persons")
        .add_edge(
            [
                "add_persons",
                "fill_location",
                "fill_period",
                "fill_act_type",
                "fill_project"
            ], "call_tool")
        .add_edge("call_tool", "deliver_raw_data")
        .add_edge("deliver_raw_data", END)
        #
        .compile()
)
