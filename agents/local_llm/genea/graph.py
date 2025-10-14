from .church.graph import (
    genea_church_graph,
)
from .civil.graph import (
    genea_civil_graph,
)

def search_genea_graph(checkpointer = None, **kwargs):
    return (
        StateGraph(GeneaCivilState)
        .add_node("analyze", step_analyse)
        .add_node("select", step_select)
        .add_node("invoke", step_invoke)
        .add_edge(START, "analyze")
        .add_edge("analyze", "select")
        .add_edge("select", "invoke")
        .add_edge("invoke", END)
        .compile(checkpointer, **kwargs)
    )