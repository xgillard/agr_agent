"""Common utilities to design autonomous agents."""
from logging import Logger
from typing import Annotated
from functools import partial

from langchain.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool, render_text_description
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState


def _trace_llm(direction: str, name: str, state: MessagesState) -> None:
    """Loggue une étape d'interaction dans un graphe langgraph."""
    msg = state["messages"][-1]

    print(f"{direction} {name} ({msg.type}) {direction}")
    if hasattr(msg, "content"):
        print(msg.content)
    
    if hasattr(msg, "tool_calls"):
        tool_calls = msg.tool_calls
        for t in tool_calls:
            print(f"{t['name']} {t['args']}")



_SYTEM_TEMPLATE_WITH_TOOLS = """You are {role}

{backstory}
        
Your personal goal is: {goal}
You ONLY have access to the following tools, and should NEVER make up tools that are not listed here:

{tools}

**IMPORTANT**: 
As a first step, I want you to make a plan of how you intend to complete your taks.
You are only allowed to make use of your tools after you made the initial plan.
You may only use **ONE TOOL AT A TIME**.
Feel free to use each tool as many times as you need, ie. to ask different questions.
Feel free to refine your plan based on the information you find over time.

**FORMAT**:
- Insert your the marker [__FINAL_ANSWER__] before your best and final answer.
- Structure your reasoning as 'Plan' followed by a series of 'Thought' and 'Observation'.

"""


_TASK_TEMPLATE = """
Current Task: {input}

{{input}}
"""

def agent_system_prompt(
    role:      Annotated[str, "Role played by the agent"],
    goal:      Annotated[str, "Goal of the agent"],
    backstory: Annotated[str, "Backstory of the agent"],
    tools:     Annotated[list[BaseTool], "The list of tools that can be called by the agent"]
) -> str:
    """Create a system prompt template to give life to the agents."""
    descriptions = render_text_description(tools)
    tool_names   = [tool.name for tool in tools]
    return _SYTEM_TEMPLATE_WITH_TOOLS.format(
        role=role, 
        goal=goal, 
        backstory=backstory, 
        tools=descriptions, 
        tool_names=tool_names,
    )

def agent(
    name:      Annotated[str, "Name of the agent"],
    role:      Annotated[str, "Role played by the agent"],
    goal:      Annotated[str, "Goal of the agent"],
    backstory: Annotated[str, "Backstory of the agent"],
    tools:     Annotated[list[BaseTool], "The list of tools that can be called by the agent"],
    model:     Annotated[BaseLanguageModel, "The llm chat model which will be used to imperson the agent"],
    debug:     Annotated[bool, "A flag that indicates whether or not i want to trace every step of the graph"] = False,
) -> Runnable:
    """Create an agent that has been populated in a way that I like"""
    return create_react_agent(
        name  = name,
        model = model,
        tools = tools,
        prompt= agent_system_prompt(
            role = role,
            goal = goal,
            backstory = backstory,
            tools = tools,
        ),
        pre_model_hook  = partial(_trace_llm, ">>>>>>>>>>>>", name) if debug else None,
        post_model_hook = partial(_trace_llm, "<<<<<<<<<<<<", name) if debug else None,
    )

def task(
    description: str,
    #expected_outcome: str,
) -> ChatPromptTemplate:
    """Create a task for the agent to execute."""
    return ChatPromptTemplate.from_template(_TASK_TEMPLATE.format(input=description))