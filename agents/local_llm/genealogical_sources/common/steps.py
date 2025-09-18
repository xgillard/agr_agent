"""Common workflow steps for genealogical search in agatha."""

from __future__ import annotations

from typing import TypeVar, cast

from langchain_core.output_parsers import StrOutputParser

from ....tools.agatha_common import (
    Municipality,
)
from ....tools.genealogy import AJAX_URL
from ...common.llm import LLM
from ...common.schemas import SingleChoice
from .prompts import (
    document_type,
    municipality,
    year_period,
)
from .schemas import (
    GeneaSearchState,
    TypeOfDocument,
    YearPeriod,
)

_State = TypeVar("_State", bound=GeneaSearchState)

async def step_municipality(state: _State) -> _State:
    """fill the municipality."""
    
    mun_name = cast(str, await (LLM | StrOutputParser()).ainvoke(
        state["messages"] + [ municipality ]
    ))

    mun = Municipality.by_name(mun_name, AJAX_URL, return_single_best_match=True)
    if mun is None:
        raise ValueError("municipality cannot be left empty")
    else:
        return { # type: ignore
            "municipality": mun
        }


async def step_fill_year_period(state: _State) -> _State:
    """Fill the search period."""
    
    period = cast(YearPeriod,
        await LLM
        .with_structured_output(YearPeriod)
        .ainvoke( state["messages"] + [ year_period ])
    )
    return { "period": period } # type: ignore

async def step_type_of_doc(state: _State) -> _State:
    """Fill the search period."""

    choice = cast(SingleChoice[TypeOfDocument],
        await LLM
        .with_structured_output(SingleChoice[TypeOfDocument])
        .ainvoke( state["messages"] + [ document_type ])
    )
    return { "type_of_doc": choice.choice } # type: ignore
