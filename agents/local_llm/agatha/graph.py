"""Graph to implement the overarching AGATHA interactions workflow."""

from typing import (
    Literal,
    cast,
)

from langchain.tools import tool
from langchain_core.messages import (
    AIMessage,
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
    summarize,
    triage,
)
from .schemas import (
    AgathaSearchEngine,
)


async def step_triage(state: AgathaToolState) -> Literal["genealogy", "analyses"]:
    """Route requests to the appropriate subflow."""

    routing = cast(SingleChoice[AgathaSearchEngine], 
                   await (
                       LLM
                        .with_structured_output(SingleChoice[AgathaSearchEngine])
                        .ainvoke(state["messages"] +[ triage ])
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
                state["messages"] + [ summarize.format(raw_data = raw_data) ]
            )
    )

    return { # type: ignore
        "output": AIMessage(summary),
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
    The input of this tool must be formated as a SCRUM-like user story (ie: "As a .... I want to .... so that ....").

    Args: 
        user_story (str): the research you with to perform in AGATHA, formulated as a SCRUM user story.
    """

    response = cast(AgathaToolState, await (
        ASK_AGATHA.ainvoke({"messages": [HumanMessage(user_story)]}) # type: ignore
    ))
    return response["output"]


@tool(parse_docstring=True)
async def find_act_details(user_story: str) -> str:
    """Find the details of an official act based on the *content* of that act. 
    
    For instance, if you know the name of some people that were involved in that act or if you know some specific 
    keyword that might help retrieve the act you need. This tool is particularly useful when 
    you need to answer the questions *WHO*, *WHERE*, *WHEN* or *WHAT*. 

    **IMPORTANT**
    The input of this tool must be formated as a SCRUM-like user story (ie: "As a .... I want to .... so that ....").

    Args: 
        user_story (str): the research you with to perform in AGATHA, formulated as a SCRUM user story.
    """

    response = cast(AgathaToolState, await (
        ASK_AGATHA.ainvoke({"messages": [HumanMessage(user_story)]}) # type: ignore
    ))
    return response["output"]

@tool(parse_docstring=True)
async def find_digitized_document(
    user_story: str, 
    kind_of_document: str,
    location: str,
    period: str,
    ) -> str:
    """Find digitized scans of the original registers where official acts have been consigned. 
    
    This is often helpful in order to find the scan of a specific act. In order to use this tool, 
    you need to know some details about the register (or act) you wish to find. Namely, you need 
    to know:
          - _WHAT KIND OF DOCUMENT_ you wish to retrieve
          - _WHERE_ the act happened
          - _WHEN_ it happened (at least have an idea of the date range) 
    
    Args: 
        user_story (str): the research you with to perform in AGATHA, formulated as a SCRUM user story.
        kind_of_document (str): the kind of documents you wish to retrieve.
        location (str): the location where it happened. This includes the municipality + the parish if you know it.
        period (str): an approximate date range when it might have happened if you know it.

    """

    question = f"""
    {user_story}

    ## Meta Data
    Kind of Document: {kind_of_document}
    Location: {location}
    period: {period}
    """

    response = cast(AgathaToolState, await (
        ASK_AGATHA.ainvoke({"messages": [HumanMessage(question)]}) # type: ignore
    ))
    return response["output"]

