"""The prompts related to the searching in civil registers after 1796."""

from langchain_core.messages import HumanMessage

from ....tools.genealogy import (
    CivilActType,
    CivilIndex,
    OtherCivilActType,
    OtherCivilIndex,
)

context = """
< Context >
You want to use the "search in genealogical sources" capabilities from AGATHA
because you think that finding the appropriate register will help you retrieve
the digitized copy of an administrative act you wish to find.
</ Context >
"""

act_type = HumanMessage(f"""
{context}
                                                       
< Instructions >
What type of document do you wish to retrieve ? Select 0, 1 or more options
among the following:
{CivilActType.all_values()}
</ Instructions >
""")

other_type = HumanMessage(f"""
{context}
                                                       
< Instructions >
What type of document do you wish to retrieve ? Select 0, 1 or more options
among the following:
{OtherCivilActType.all_values()}
</ Instructions >
""")

index_type = HumanMessage(f"""
{context}
                                                       
< Instructions >
Which indexes should be considered during your research ? Select 0, 1 or more 
options among the following:
{CivilIndex.all_values()}
</ Instructions >
""")


other_index_type = HumanMessage(f"""
{context}
                                                       
< Instructions >
Which indexes should be considered during your research ? Select 0, 1 or more 
options among the following:
{OtherCivilIndex.all_values()}
</ Instructions >
""")