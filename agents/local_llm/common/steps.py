from typing import TypeVar, cast

from langchain_core.messages import AIMessage
from langchain_core.runnables.base import Runnable, RunnableLambda
from pydantic import BaseModel

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



async def step_deliver_raw_data(state: T) -> T:
    """Deliver the raw data as an AI message."""

    call_data = state.get("call_data")
    call_text = "== no data found =="
    
    if call_data is None:
        call_data = []

    if isinstance(call_data, BaseModel):
        call_text = call_data.model_dump_json(by_alias=False, exclude_none=True)
    else:
        call_data = cast(list, call_data)
        call_text = f"[ {','.join(m.model_dump_json(by_alias=False, exclude_none=True) for m in call_data)} ]"

    return { # type: ignore
        "messages": AIMessage( # type: ignore
            f"""
            I have searched the analysed records in the archives, and here is the raw data I found:
            {call_text}
            """
        ),
    }