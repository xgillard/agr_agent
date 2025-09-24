"""The prompts related to the creation of a search person request."""

from langchain_core.messages import (
    HumanMessage,
)

from ....tools.analyses_of_records import AnalysesActType, AnalysesProject

location = HumanMessage("""
< Instructions >
Where did the act you are searching took place ? 
Respond using the municipality name only. Municipality name must use the French or Dutch spelling.
Leave empty unless the information was explicitly given.
</ Instructions >
""")

period = HumanMessage("""
< Instructions >
When did the act happen ? Leave empty unless the information was explicitly given.
</ Instructions >
""")

act_type = HumanMessage(f"""
< Instructions >
What is the kind of document you are searching ? Select the most appropriate value among the
following options: 

{AnalysesActType.all_values()}
</ Instructions >
""")

project_type = HumanMessage(f"""
< Instructions >
What project led to the analysis of the document you are searching for ? Select one or more
options among: 

{AnalysesProject.all_values()}

**WARNING** 
Leave this field empty unless you are absolutely certain about the id of the project that 
led to the analysis of the document you search.
</ Instructions >
""")