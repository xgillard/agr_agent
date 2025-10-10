from langgraph.graph import END, START, StateGraph

from ..common.schemas import (
    AnalysesState,
)
from ..common.steps import (
    step_analyse_doctype,
    step_search_term,
    step_select_doctype,
    tool_analyses_free_search,
)

ANALYSES_FREE = (
    StateGraph(AnalysesState)
    .add_node("analyse_doctype", step_analyse_doctype)
    .add_node("select_doctype", step_select_doctype)
    .add_node("search term", step_search_term)
    .add_node("invoke", tool_analyses_free_search)
    #
    .add_edge(START, "analyse_doctype")
    .add_edge("analyse_doctype", "select_doctype")
    .add_edge(START, "search term")
    .add_edge([
        "select_doctype", "search term"
    ], "invoke")
    .add_edge("invoke", END)
    .compile()
)