"""The prompts related to the searching in church registers."""

from langchain_core.prompts import HumanMessagePromptTemplate

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

act_type = HumanMessagePromptTemplate.from_template("""
{context}
                                                       
< Instructions >
What type of records do you wish to retrieve ? Select 0, 1 or more options
among the following:
{record_types}
</ Instructions >
""")

index_type = HumanMessagePromptTemplate.from_template("""
{context}
                                                       
< Instructions >
Which indexes should be considered during your research ? Select 0, 1 or more 
options among the following:
{index_types}
</ Instructions >
""")