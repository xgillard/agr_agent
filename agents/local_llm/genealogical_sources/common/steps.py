"""Common workflow steps for genealogical search in agatha."""

from __future__ import annotations

from typing import TypeVar, cast

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.base import Runnable, RunnableLambda

from ....tools.agatha_common import (
    Municipality,
)
from ....tools.genealogy import AJAX_URL
from ...common.llm import LLM
from .prompts import (
    document_type,
    municipality,
    year_period,
)
from .schemas import (
    GeneaSearchState,
    SingleChoice,
    TypeOfDocument,
    YearPeriod,
)

_State = TypeVar("_State", bound=GeneaSearchState)

def step_municipality(context: str) -> Runnable[_State, _State]:
    """Generic step to fill the municipality field."""

    async def _step_municipality(state: _State) -> _State:
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
    
    return RunnableLambda(_step_municipality)


def step_fill_year_period(context: str) -> Runnable[_State, _State]:
    """Create a contextualized step to fill yearlt period.
    
    Args:
        context (str): the context in which this step will occur.
    """
    async def _step_fill_period(state: _State) -> _State:
        """Fill the search period."""

        period = cast(YearPeriod,
            await LLM
            .with_structured_output(YearPeriod)
            .ainvoke( state["messages"] + [ year_period.format(context=context) ])
        )
        return { "period": period } # type: ignore
    
    return RunnableLambda(_step_fill_period)


def step_type_of_doc(context: str) -> Runnable[_State, _State]:
    """Create a contextualized step to determine the desired type of doc.
    
    Args:
        context (str): the context in which this step will occur.
    """
    async def _step_type_of_doc(state: _State) -> _State:
        """Fill the search period."""

        choice = cast(SingleChoice[TypeOfDocument],
            await LLM
            .with_structured_output(SingleChoice[TypeOfDocument])
            .ainvoke( state["messages"] + [ document_type.format(context=context) ])
        )
        return { "type_of_doc": choice.choice } # type: ignore
    
    return RunnableLambda(_step_type_of_doc)
