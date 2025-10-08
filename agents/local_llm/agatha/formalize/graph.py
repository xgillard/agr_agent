"""graph for the formalization subflow."""

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from .schemas import (
    FormalizationState,
)
from .steps import (
    step_base_info,
    step_doctype,
    step_people_role,
    step_period_of_interest,
    step_synthesize,
)

FORMALIZE = (
    StateGraph(FormalizationState)
        .add_node("basic", step_base_info)
        .add_node("period", step_period_of_interest)
        .add_node("doctype", step_doctype)
        .add_node("people", step_people_role)
        .add_node("synthezize", step_synthesize)
        .add_edge(START, "basic")
        .add_edge(START, "period")
        .add_edge(START, "doctype")
        .add_edge("basic", "people")
        .add_edge(["period", "doctype", "people"], "synthezize")
        .add_edge("synthezize", END)
        .compile()
)
