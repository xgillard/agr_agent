"""Prompts to implement the overarching AGATHA interactions workflow."""

from langchain_core.messages import HumanMessage
from langchain_core.prompts import HumanMessagePromptTemplate

from .schemas import AgathaSearchEngine

agatha_offering = """
AGATHA offers the following search engines:

* ANALYSES: which you should call when you would like to find an official act based on the *content*
    of that act. For instance, if you know the name of some people that were involved in that act or
    if you know some specific keyword that might help retrieve the act you need. This tool is
    particularly useful when you need to answer the questions *WHO*, *WHERE*, *WHEN* or *WHAT*.

* GENEALOGY: which you should call when you would like to find scans of the original registers where
    the act is consigned. This tool is only useful if you know **WHERE** and **WHEN** the act you 
    search has occured.
"""


triage = HumanMessage(f"""
< Context >
You now need to decide where to look in AGATHA. {agatha_offering}
</ Context >

< Instructions >
What tool do you want to consult ? Select one of the following: 
{AgathaSearchEngine.all_values()}
</ Instructions >
""")

summarize = HumanMessagePromptTemplate.from_template("""
< Instructions >
Considering your current objective (latest user story), and considering 
that the following is the raw result of your search in AGATHA, respond to
your question.
{raw_data}

Summarize the information which is helpful to satisfy your current objective.
Do not answer the original user's request just yet. Focus on your current
objective only.
</ Instructions >
""")