"""Prompts for the genealogical search workflows."""

from langchain_core.prompts import HumanMessagePromptTemplate

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
