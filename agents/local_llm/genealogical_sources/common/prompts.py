"""Prompts for the genealogical search workflows."""

from langchain_core.prompts import HumanMessagePromptTemplate

from .schemas import TypeOfDocument

municipality = HumanMessagePromptTemplate.from_template("""
{context}

< Instructions >
Where did the act you are searching took place ? Respond using the municipality
name only.
</ Instructions >
""")


year_period = HumanMessagePromptTemplate.from_template("""
{context}

< Instructions >
When did the act happen ? (Leave empty unless the information was explicitly given).
</ Instructions >
""")

document_type = HumanMessagePromptTemplate.from_template(f"""
{{context}}

< Note >
* Select {TypeOfDocument.ACTS} when you want to search the scan of an official actual act.
* Select {TypeOfDocument.INDEXES} when you want to search the scan of an index (long list of names)
* Select {TypeOfDocument.BOTH} when you want to search both in the acts as well as in the index registers
</ Note >

< Instructions >
What type of document do you want to retrieve ? Select one value among the following:
{TypeOfDocument.all_values()}
</ Instructions >
""")