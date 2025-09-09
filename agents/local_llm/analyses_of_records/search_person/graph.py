"""Implement the logic to call a search_person_in_analyses_of_records as if the agent went through a wizzard."""

from typing import cast

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from tools.analyses_of_records import (
    AnalysesSearchPersonRequest,
    PersonCriterion,
    search_person_in_analyses_of_records,
)

from ..common_steps import (
    find_location,
    find_period,
    find_project,
    find_record_type,
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

LLM = init_chat_model(
    model = "mistral-small:24b",
    model_provider = "ollama",
)

###### ADD PERSON WIZZARD ####################################################

def find_family_name(state: AddPersonWizzardState) -> AddPersonWizzardState:
    rsp = cast(FamilyName, 
        (LLM.with_structured_output(FamilyName))
        .invoke( 
            state["outer_context"] + 
            [ HumanMessage(family_name.format(full_name=state["full_name"])) ]
        )
    )
    return {"family_name": rsp.family_name}

def find_first_name(state: AddPersonWizzardState) -> AddPersonWizzardState:
    rsp = cast(FirstName,
        (LLM.with_structured_output(FirstName))
        .invoke( 
            state["outer_context"] + 
            [ HumanMessage(first_name.format(full_name=state["full_name"])) ]
        )
    )
    return {"first_name": rsp.first_name}

def find_job(state: AddPersonWizzardState) -> AddPersonWizzardState:
    rsp = cast(Profession,
        (LLM.with_structured_output(Profession))
        .invoke( 
            state["outer_context"] + 
            [ HumanMessage(job_name.format(full_name=state["full_name"])) ]
        )
    )
    return {"profession": rsp.profession}

def find_role(state: AddPersonWizzardState) -> AddPersonWizzardState:
    rsp = cast(RoleChoice,
        (LLM.with_structured_output(RoleChoice))
        .invoke( 
            state["outer_context"] + 
            [ HumanMessage(role_name.format(full_name=state["full_name"])) ]
        )
    )
    return {"role": rsp.role} if rsp else {}

__ADD_PERSON_WIZZARD = (
    StateGraph(AddPersonWizzardState)
        .add_node("find_family_name", find_family_name)
        .add_node("find_first_name", find_first_name)
        .add_node("find_job", find_job)
        .add_node("find_role", find_role)
        #
        .add_edge(START, "find_family_name")
        .add_edge(START, "find_first_name")
        .add_edge(START, "find_job")
        .add_edge(START, "find_role")
        .add_edge([
            "find_family_name",
            "find_first_name",
            "find_job",
            "find_role",
        ], END)
        #
        .compile()
)

###### SEARCH PERSON WIZZARD ####################################################
def list_people(state: SearchPersonWizzardState) -> SearchPersonWizzardState:
    """List the people."""

    known_people = cast(ListOfPeople,
        LLM
        .with_structured_output(ListOfPeople)
        .invoke( state["outer_context"] + [ HumanMessage( list_known_people ) ])
    )
    return { "known_people": known_people.list_of_names }

def add_pers_wizzard(state: SearchPersonWizzardState) -> SearchPersonWizzardState:
    """Goes through all the steps of the add person wizard state"""
    
    persons = []
    for p in state["known_people"]:
        substate = AddPersonWizzardState(full_name=p, outer_context=state["outer_context"])
        sub = __ADD_PERSON_WIZZARD.invoke(substate)  # type: ignore[arg-type]
        crit = PersonCriterion(
            family_name=sub["family_name"],
            first_name=sub["first_name"],
            profession=sub["profession"],
            role=sub["role"],
        )
        persons.append(crit)

    return {"persons": persons}

def call_tool(state: SearchPersonWizzardState) -> SearchPersonWizzardState:
    """Performs a call to the Agatha tool"""
    call = search_person_in_analyses_of_records(
        AnalysesSearchPersonRequest(
            persons=state["persons"],
            location=state["location"],
            period=state["period_selector"],
            start_date=state["start_date"],
            end_date=state["end_date"],
        )
    )
    return {"call_data": call}

SEARCH_PERSON_IN_ANALYSES_OF_RECORDS = (
    StateGraph(SearchPersonWizzardState)
        .add_node("list_people", list_people)
        .add_node("add_persons", add_pers_wizzard)
        .add_node("find_location", find_location)
        .add_node("find_period", find_period)
        .add_node("find_act_type", find_record_type)
        .add_node("find_project", find_project)
        .add_node("call_tool", call_tool)
        #
        .add_edge(START, "list_people")
        .add_edge(START, "find_location")
        .add_edge(START, "find_period")
        .add_edge(START, "find_act_type")
        .add_edge(START, "find_project")
        .add_edge("list_people", "add_persons")
        .add_edge(
            [
                "add_persons",
                "find_location",
                "find_period",
                "find_act_type",
                "find_project"
            ], "call_tool")
        .add_edge("call_tool", END)
        #
        .compile()
)
