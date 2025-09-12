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
    municipality,
)
from .schemas import (
    GeneaSearchState,
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
