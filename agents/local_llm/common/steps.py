from typing import TypeVar, cast

from langchain_core.messages import AIMessage
from pydantic import BaseModel

from .schemas import AgathaToolState

# anything that extends agatha tool state
T = TypeVar("T", bound=AgathaToolState)

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