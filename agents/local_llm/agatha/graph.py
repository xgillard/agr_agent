"""graph that implements the simplified agatha workflow."""

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from ..analyze.free.graph import (
    ANALYSES_FREE,
)
from ..analyze.person.graph import (
    ANALYSES_PERSON,
)
from ..genea.church.graph import (
    GENEA_CHURCH,
)
from ..genea.civil.graph import (
    GENEA_CIVIL,
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

ASK_AGATHA = (
    StateGraph(AgentState)
        .add_edge(START, "Initialize")
        #
        .add_node("Initialize", step_initialize)
        .add_node("Set Objective", step_set_objective)
        .add_node("Formalize",  step_formalize)
        .add_node("Analyses of Records / Free Search", ANALYSES_FREE)
        .add_node("Analyses of Records / Search Person", ANALYSES_PERSON)
        .add_node("Genealogical sources / Church Registers", GENEA_CHURCH)
        .add_node("Genealogical sources / Civil State Registers", GENEA_CIVIL)
        .add_node("Online Help Resources", tool_online_help)
        .add_node("Respond", step_respond)
        .add_node("Observation", step_observation)
        #
        .add_conditional_edges("Initialize", cond_enough_info)
        .add_edge("Set Objective", "Formalize")
        .add_conditional_edges("Formalize", cond_what_tool)
        .add_edge("Analyses of Records / Free Search", "Observation")
        .add_edge("Analyses of Records / Search Person", "Observation")
        .add_edge("Genealogical sources / Church Registers", "Observation")
        .add_edge("Genealogical sources / Civil State Registers", "Observation")
        .add_edge("Online Help Resources", "Observation")
        .add_conditional_edges("Observation", cond_enough_info)
        .add_edge("Respond", END)
        .compile()
)