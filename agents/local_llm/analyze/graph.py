from langgraph.graph import END, START, StateGraph

from .schemas import (
    AnalysesState,
)
from .steps import (
    cond_use_keywords,
    cond_use_persons_norole,
    cond_use_persons_role,
    step_analyse_doctype,
    step_select_doctype,
    tool_analyses_free_keywords,
    tool_analyses_free_names_only,
    tool_analyses_persons_norole,
    tool_analyses_persons_role,
)


def step_do_nothing(state): 
    return state

def search_analyses_graph(checkpointer = None, **kwargs):
    return (
        StateGraph(AnalysesState)
        .add_node("analyse_doctype", step_analyse_doctype)
        .add_node("select_doctype", step_select_doctype)
        .add_node("Free Names Only", tool_analyses_free_names_only)
        .add_node("Keywords", tool_analyses_free_keywords)
        .add_node("Persons NoRole", tool_analyses_persons_norole)
        .add_node("Persons Role", tool_analyses_persons_role)
        .add_node("__END__", step_do_nothing)
        #
        .add_edge(START, "analyse_doctype")
        .add_edge("analyse_doctype", "select_doctype")
        .add_edge("select_doctype",  "Free Names Only")
        .add_conditional_edges("Free Names Only", cond_use_keywords)
        .add_conditional_edges("Keywords", cond_use_persons_norole)
        .add_conditional_edges("Persons NoRole", cond_use_persons_role)
        .add_edge("Persons Role", "__END__")
        .add_edge("__END__", END)
        .compile(checkpointer, **kwargs)
    )