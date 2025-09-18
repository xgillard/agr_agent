"""Graph to implement the overarching AGATHA interactions workflow."""

from typing import (
    Literal,
    cast,
)

from langchain_core.messages import (
    AIMessage,
)
from langchain_core.output_parsers import (
    StrOutputParser,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from pydantic import (
    BaseModel,
)

from ..analyses_of_records.graph import SEARCH_IN_ANALYSES_OF_RECORDS
from ..common.llm import (
    LLM,
)
from ..common.schemas import (
    AgathaToolState,
    SingleChoice,
)
from ..genealogical_sources.graph import SEARCH_IN_GENEALOGIC_SOURCES
from .prompts import (
    describe_intent,
    summarize,
    triage,
)
from .schemas import (
    AgathaSearchEngine,
)


async def step_describe_intent(state: AgathaToolState) -> AgathaToolState:
    """Describe the intent behind the call to agatha."""

    intent = await (LLM | StrOutputParser()).ainvoke(state['messages'] + [describe_intent] )
    return {"messages": AIMessage(intent)} # type: ignore


async def step_triage(state: AgathaToolState) -> Literal["genealogy", "analyses"]:
    """Route requests to the appropriate subflow."""

    intent = state.get("intent", "I dont know what")
    routing = cast(SingleChoice[AgathaSearchEngine], 
                   await (
                       LLM
                        .with_structured_output(SingleChoice[AgathaSearchEngine])
                        .ainvoke(
                            state["messages"] +
                            [ triage.format(intent = intent) ]
                        )
                   )
    )
    match routing.choice:
        case AgathaSearchEngine.ANALYSES:
            return "analyses"
        case AgathaSearchEngine.GENEALOGY:
            return "genealogy"


def _format_raw_data(state: AgathaToolState) -> str:
    """Format the raw data in an appropriate way.
    
    Returns:
        str: a formatted representation of the raw call data.
    """
    
    call_data = state.get("call_data")
    call_text = "== no data found =="
    
    if call_data is None:
        call_data = []

    if isinstance(call_data, BaseModel):
        call_text = call_data.model_dump_json(by_alias=False, exclude_none=True)
    else:
        call_data = cast(list, call_data)
        call_text = f"[ {','.join(m.model_dump_json(by_alias=False, exclude_none=True) for m in call_data)} ]"
    return call_text

async def step_deliver_response(state: AgathaToolState) -> AgathaToolState:
    """Deliver the raw data as an AI message."""

    raw_data = _format_raw_data(state)
    summary  = await (
        (LLM | StrOutputParser())
            .ainvoke(
                state["messages"] + 
                [ summarize.format(
                    raw_data = raw_data,
                ) ]
            )
    )

    return { # type: ignore
        "messages": AIMessage(summary),
    }

ASK_AGATHA = (
    StateGraph(AgathaToolState)
        .add_node("describe_intent", step_describe_intent)
        .add_node("analyses", SEARCH_IN_ANALYSES_OF_RECORDS)
        .add_node("genealogy", SEARCH_IN_GENEALOGIC_SOURCES)
        .add_node("deliver_response", step_deliver_response)
        #
        .add_edge(START, "describe_intent")
        .add_conditional_edges("describe_intent", step_triage)
        .add_edge("analyses", "deliver_response")
        .add_edge("genealogy", "deliver_response")
        .add_edge("deliver_response", END)
        #
        .compile()
)