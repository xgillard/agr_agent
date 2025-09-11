from typing import TypeVar, cast

from langchain_core.runnables.base import Runnable, RunnableLambda

from .llm import LLM
from .prompts import period
from .schemas import AgathaToolState, Period

# anything that extends agatha tool state
T = TypeVar("T", bound=AgathaToolState)

def step_fill_period(context: str) -> Runnable[T, T]:
    """Create a contextualized step to fill period.
    
    Args:
        context (str): the context in which this step will occur.
    """
    async def _step_fill_period(state: T) -> T:
        """Fill the search period."""

        when = cast(Period,
            await LLM
            .with_structured_output(Period)
            .ainvoke( state["messages"] + [ period.format(context=context) ])
        )
        return { 
            "period_selector": when.selector, 
            "start_date": when.start_date,
            "end_date": when.end_date,
        } # type: ignore
    
    return RunnableLambda(_step_fill_period)
