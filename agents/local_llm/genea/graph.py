from typing import (
    Annotated,
    Literal,
    cast,
)

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from ..agatha.schemas import (
    AgentState,
    BaseCriteria,
    PeriodOfInterest,
)
from .church.graph import (
    genea_church_graph,
)
from .civil.graph import (
    genea_civil_graph,
)


def merge(left: list, right: list) -> list:
    return [
        *left,
        *right,
    ]

class GeneaState(AgentState):
    call_data: Annotated[list, merge] # type: ignore

GeneaSource = Literal["Church", "Civil", "Both"]

async def genea(state: AgentState) -> GeneaSource:
    crit = cast(BaseCriteria, state.get("criteria", BaseCriteria()))
    poi = crit.period_of_interest or PeriodOfInterest()
    bgin= poi.min_date_formatted_as_yyyy_mm_dd or ""
    end = poi.max_date_formatted_as_yyyy_mm_dd or ""
    byr = 0
    eyr = 9999 
    try:
        byr = int(bgin[:4])
    except Exception:
        pass
    #
    try: 
        eyr = int(end[:4])
    except Exception:
        pass
    
    value = 0

    if byr <= 1796:
        value += 1
    if eyr >= 1796:
        value += 2

    match value:
        case 1:
            return "Church"
        case 2: 
            return "Civil"
        case 3: 
            return "Both"
        case _:
            raise ValueError("impossible value")


def idempotent(state: GeneaState) -> GeneaState:
    return state

def search_genea_graph(checkpointer = None, **kwargs):
    civil = genea_civil_graph(checkpointer, **kwargs)
    church= genea_church_graph(checkpointer, **kwargs)

    return (
        StateGraph(GeneaState)
        .add_node("Civil", civil)
        .add_node("Church", church)
        #
        .add_node("Both", idempotent)
        .add_node("partial-Civil", civil)
        .add_node("partial-Church", church)
        #
        .add_conditional_edges(START, genea)
        .add_edge("Civil", END)
        .add_edge("Church", END)
        .add_edge("Both", "partial-Civil")
        .add_edge("Both", "partial-Church")
        .add_edge(["partial-Civil", "partial-Church"], END)
        .compile(checkpointer, **kwargs)
    )