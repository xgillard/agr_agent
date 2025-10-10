from langgraph.graph import END, START, StateGraph

from ..common.schemas import (
    AnalysesState,
)
from ..common.steps import (
    step_analyse_doctype,
    step_people_role,
    step_select_doctype,
    tool_analyses_search_person,
)

ANALYSES_PERSON = (
    StateGraph(AnalysesState)
    .add_node("analyse_doctype", step_analyse_doctype)
    .add_node("select_doctype", step_select_doctype)
    .add_node("people role", step_people_role)
    .add_node("invoke", tool_analyses_search_person)
    #
    .add_edge(START, "analyse_doctype")
    .add_edge("analyse_doctype", "select_doctype")
    .add_edge(START, "people role")
    .add_edge([
        "select_doctype", "people role"
    ], "invoke")
    .add_edge("invoke", END)
    .compile()
)