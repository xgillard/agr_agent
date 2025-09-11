"""Workflow to search in church registers prior to 1796."""

from typing import (
    TypeVar,
    cast,
)

from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, START, StateGraph

from ....tools.agatha_common import Municipality
from ....tools.genealogy import AJAX_URL
from ...common.llm import LLM
from ...common.steps import (
    step_fill_period,
)
from ..common.prompts import (
    municipality,
)
from .prompts import (
    context,
    parish,
)
from .schemas import (
    SearchChurchRegisterState,
    StrList,
)

T = TypeVar("T", bound=SearchChurchRegisterState)

async def step_municipality(state: T) -> T:
    """fill the municipality."""

    mun_name = cast(str, await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + 
        [ municipality.format(context=context) ]
    ))

    mun = Municipality.by_name(mun_name, AJAX_URL, return_single_best_match=True)
    if mun is None:
        raise ValueError("municipality cannot be left empty")
    else:
        return { # type: ignore
            "municipality": mun
        }


async def step_parish(state: T) -> T: 
    """Fill the parish."""

    mun = state.get("municipality")
    par = cast(Municipality, mun).parishes(AJAX_URL) if mun is not None else []
    if len(par) <= 1:
        return {"parish": par} # type: ignore
    else:
        par_name = cast(StrList, await (
            LLM.with_structured_output(StrList)
            .ainvoke(
                state["messages"] + 
                [ parish.format(context=context, parish=[p.place_name for p in par]) ]
            ))
        )
        par = [
            p for p in par if p.place_name.lower() in par_name.lst
        ]
        return {"parish": par} # type: ignore
    


SEARCH_CHURCH_REGISTERS = (
    # TODO: add edges
    # TODO: add missing steps (index type, act type, other record_type)
    StateGraph(SearchChurchRegisterState)
        .add_node("municipality", step_municipality)
        .add_node("parish", step_parish)
        .add_node("period", step_fill_period(context=context))
        # FIXME: edges
        .add_edge(START, "municipality")
        .add_edge("municipality", END)
        .compile()
)