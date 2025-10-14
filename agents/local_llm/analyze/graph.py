from langgraph.graph import END, START, StateGraph

from ..common.schemas import (
    AnalysesState,
)
from .steps import (
    step_analyse_doctype,
    step_select_doctype,
    tool_analyses,
)


def search_analyses_graph(checkpointer = None, **kwargs):
    return (
        StateGraph(AnalysesState)
        .add_node("analyse_doctype", step_analyse_doctype)
        .add_node("select_doctype", step_select_doctype)
        .add_node("invoke", tool_analyses)
        #
        .add_edge(START, "analyse_doctype")
        .add_edge("analyse_doctype", "select_doctype")
        .add_edge("select_doctype",  "invoke")
        .add_edge("invoke", END)
        .compile(checkpointer, **kwargs)
    )