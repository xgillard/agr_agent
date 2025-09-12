"""The prompts related to the searching in church registers."""

from langchain_core.messages import HumanMessage
from langchain_core.prompts import HumanMessagePromptTemplate

from ....tools.genealogy import (
    OtherParishActType,
    ParishActType,
    ParishIndex,
)

context = """
< Context >
You want to search the digitized copy of an administrative act in the 
genealogical sources of AGATHA.
</ Context >
"""

parish = HumanMessagePromptTemplate.from_template("""
{context}

< Instructions >
What is the name of the parish where the act has taken place ? Select one or 
more options among: 
{parishes}
</ Instructions >
""")


act_type = HumanMessage(f"""
{context}
                                                       
< Instructions >
What type of records do you wish to retrieve ? Select 0, 1 or more options
among the following:
{ParishActType.all_values()}
</ Instructions >
""")

other_type = HumanMessage(f"""
{context}
                                                       
< Instructions >
What type of records do you wish to retrieve ? Select 0, 1 or more options
among the following:
{OtherParishActType.all_values()}
</ Instructions >
""")

index_type = HumanMessage(f"""
{context}
                                                       
< Instructions >
Which indexes should be considered during your research ? Select 0, 1 or more 
options among the following:
{ParishIndex.all_values()}
</ Instructions >
""")
