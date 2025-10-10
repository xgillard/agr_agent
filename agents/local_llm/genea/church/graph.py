from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from .schemas import (
    GeneaChurchState,
)
from .steps import (
    step_analyse,
    step_invoke,
    step_select,
)

GENEA_CHURCH = (
    StateGraph(GeneaChurchState)
    .add_node("analyze", step_analyse)
    .add_node("select", step_select)
    .add_node("invoke", step_invoke)
    .add_edge(START, "analyze")
    .add_edge("analyze", "select")
    .add_edge("select", "invoke")
    .add_edge("invoke", END)
    .compile()
)