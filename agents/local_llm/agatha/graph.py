"""Graph to implement the overarching AGATHA interactions workflow."""

from typing import (
    Literal,
    cast,
)

from langchain.tools import tool
from langchain_core.messages import (
    HumanMessage,
)
from langchain_core.output_parsers import (
    StrOutputParser,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from pydantic_core import (
    to_json,
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
    summarize,
    triage,
)
from .schemas import (
    AgathaSearchEngine,
)


class SingleChoiceAgathaSearchEngine(SingleChoice[AgathaSearchEngine]):
    pass 

async def step_triage(state: AgathaToolState) -> Literal["genealogy", "analyses"]:
    """Route requests to the appropriate subflow."""

    routing = cast(SingleChoiceAgathaSearchEngine, 
                   await (
                       LLM
                        .with_structured_output(SingleChoiceAgathaSearchEngine)
                        .ainvoke(state["messages"] +[ triage ])
                   )
    )
    match routing.choice:
        case AgathaSearchEngine.ANALYSES:
            return "analyses"
        case AgathaSearchEngine.GENEALOGY:
            return "genealogy"

async def step_deliver_response(state: AgathaToolState) -> AgathaToolState:
    """Deliver the raw data as an AI message."""

    raw_data = to_json(
        state.get("call_data", "__ no data found __"),
        indent=4,
        by_alias=False,
        exclude_none=True,
        bytes_mode="utf8"
    ).decode("utf8")

    summary  = await (
        (LLM | StrOutputParser())
        .ainvoke( state["messages"] + [ summarize.format(raw_data = raw_data) ] )
    )

    return { # type: ignore
        "output": summary
    }

ASK_AGATHA = (
    StateGraph(AgathaToolState)
        .add_node("analyses", SEARCH_IN_ANALYSES_OF_RECORDS)
        .add_node("genealogy", SEARCH_IN_GENEALOGIC_SOURCES)
        .add_node("deliver_response", step_deliver_response)
        #
        .add_conditional_edges(START, step_triage)
        .add_edge("analyses", "deliver_response")
        .add_edge("genealogy", "deliver_response")
        .add_edge("deliver_response", END)
        #
        .compile()
)


@tool(parse_docstring=True)
async def ask_agatha(user_story: str) -> str:
    """Search in AGATHA, the online portal of the Belgian State Archives.

    AGATHA offers the following capabilities:

    * Find the details of an official act based on the *content* of that act. For instance, 
        if you know the name of some people that were involved in that act or if you know some specific 
        keyword that might help retrieve the act you need. This tool is particularly useful when 
        you need to answer the questions *WHO*, *WHERE*, *WHEN* or *WHAT*. 

    * Find digitized scans of the original registers where official acts have been consigned. This is often
        helpful in order to find the scan of a specifi act. In order to use this tool, you need to know some 
        details about the register (or act) you wish to find. Namely, you need to know:
          - _WHAT KIND OF DOCUMENT_ you wish to retrieve
          - _WHERE_ the act happened
          - _WHEN_ it happened (at least have an idea of the date range) 
        
        Please note that using the identifier of an act is of absolutely *NO USE* when searching for
        a scan. The afore mentioned details must be repeated for that purpose.

    **IMPORTANT**
    The input of this tool must be formated as a user story that provides the necessary context. 
    It should adhere to one of the following schemas.

        - I want to find the details of [WHAT] where [RELEVANT FACTS].
        - I want to find a digitized scan of [WHAT] that happened in [LOCATION] in [YEAR].
        - I want to find a digitized scan of [WHAT] that happened in [LOCATION] between [YEAR] and [YEAR].
        - I want to find a digitized scan of [WHAT] that happened in [LOCATION] before [YEAR].
        - I want to find a digitized scan of [WHAT] that happened in [LOCATION] after [YEAR].

    Args: 
        user_story (str): the research you with to perform in AGATHA, formulated as a detailed user story.
    """

    response = cast(AgathaToolState, await (
        ASK_AGATHA.ainvoke({"messages": [HumanMessage(user_story)]}) # type: ignore
    ))
    return response["output"]

