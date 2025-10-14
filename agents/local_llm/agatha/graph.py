"""graph that implements the simplified agatha workflow."""

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from ..analyze.graph import (
    search_analyses_graph,
)
from ..genea.graph import (
    search_genea_graph,
)
from .schemas import (
    AgentState,
)
from .steps import (
    cond_enough_info,
    cond_what_tool,
    step_formalize,
    step_initialize,
    step_observation,
    step_respond,
    step_set_objective,
    tool_online_help,
)


def ask_agatha_graph(checkpointer = None, **kwargs):
    return (
        StateGraph(AgentState)
            .add_edge(START, "Initialize")
            #
            .add_node("Initialize", step_initialize)
            .add_node("Set Objective", step_set_objective)
            .add_node("Formalize",  step_formalize)
            .add_node("Analyses of Records", search_analyses_graph(checkpointer, **kwargs))
            .add_node("Genealogical sources", search_genea_graph(checkpointer, **kwargs))
            .add_node("Online Help Resources", tool_online_help)
            .add_node("Respond", step_respond)
            .add_node("Observation", step_observation)
            #
            .add_conditional_edges("Initialize", cond_enough_info)
            .add_edge("Set Objective", "Formalize")
            .add_conditional_edges("Formalize", cond_what_tool)
            .add_edge("Analyses of Records", "Observation")
            .add_edge("Genealogical sources", "Observation")
            .add_edge("Online Help Resources", "Observation")
            .add_conditional_edges("Observation", cond_enough_info)
            .add_edge("Respond", END)
            .compile(checkpointer, **kwargs)
    )