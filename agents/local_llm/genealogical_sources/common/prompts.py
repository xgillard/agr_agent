"""Prompts for the genealogical search workflows."""

from langchain_core.prompts import HumanMessagePromptTemplate

municipality = HumanMessagePromptTemplate.from_template("""
{context}

< Instructions >
Where did the act you are searching took place ? (Municipality)
</ Instructions >
""")
