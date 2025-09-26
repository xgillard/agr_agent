"""graph that implements the simplified agatha workflow."""

from langgraph.graph import END, START, StateGraph

from .schemas import (
    AgentState,
)
from .steps import (
    cond_what_tool,
    step_formalize,
    step_initialize,
    step_observation,
    step_respond,
    step_set_objective,
    tool_analyses_free_search,
    tool_analyses_search_person,
    tool_genea_church,
    tool_genea_civil,
    tool_online_help,
)

ASK_AGATHA = (
    StateGraph(AgentState)
        .add_edge(START, "Initialize")
        #
        .add_node("Initialize", step_initialize)
        .add_node("Formalize",  step_formalize)
        .add_node("Set Objective", step_set_objective)
        .add_node("Analyses of Records / Free Search", tool_analyses_free_search)
        .add_node("Analyses of Records / Search Person", tool_analyses_search_person)
        .add_node("Genealogical sources / Church Registers", tool_genea_church)
        .add_node("Genealogical sources / Civil State Registers", tool_genea_civil)
        .add_node("Online Help Resources", tool_online_help)
        .add_node("Respond", step_respond)
        .add_node("Observation", step_observation)
        #
        .add_edge("Initialize", "Formalize")
        .add_edge("Formalize", "Set Objective")
        .add_conditional_edges("Set Objective", cond_what_tool)
        .add_edge("Analyses of Records / Free Search", "Observation")
        .add_edge("Analyses of Records / Search Person", "Observation")
        .add_edge("Genealogical sources / Church Registers", "Observation")
        .add_edge("Genealogical sources / Civil State Registers", "Observation")
        .add_edge("Online Help Resources", "Observation")
        .add_edge("Observation", "Formalize")
        .add_edge("Respond", END)
        .compile()
)