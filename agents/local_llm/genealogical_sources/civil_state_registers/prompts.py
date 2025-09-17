"""The prompts related to the searching in civil registers after 1796."""

from langchain_core.prompts import HumanMessagePromptTemplate

from ....tools.genealogy import (
    CivilActType,
    CivilIndex,
    OtherCivilActType,
    OtherCivilIndex,
)

act_type = HumanMessagePromptTemplate.from_template(f"""
{{context}}
                                                       
< Instructions >
What type of document do you wish to retrieve ? Select 0, 1 or more options
among the following:
{CivilActType.all_values()}
</ Instructions >
""")

other_type = HumanMessagePromptTemplate.from_template(f"""
{{context}}
                                                       
< Instructions >
What type of document do you wish to retrieve ? Select 0, 1 or more options
among the following:
{OtherCivilActType.all_values()}
</ Instructions >
""")

index_type = HumanMessagePromptTemplate.from_template(f"""
{{context}}
                                                       
< Instructions >
Which indexes should be considered during your research ? Select 0, 1 or more 
options among the following:
{CivilIndex.all_values()}
</ Instructions >
""")


other_index_type = HumanMessagePromptTemplate.from_template(f"""
{{context}}
                                                       
< Instructions >
Which indexes should be considered during your research ? Select 0, 1 or more 
options among the following:
{OtherCivilIndex.all_values()}
</ Instructions >
""")