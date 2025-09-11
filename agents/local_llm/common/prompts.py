"""Prompts to implement common steps accross tools used by AGATHA."""

from langchain.prompts import (
    HumanMessagePromptTemplate,
)

period = HumanMessagePromptTemplate.from_template("""
{context}

< Instructions >
When did the act happen ? (Leave empty unless the information was explicitly given).
</ Instructions >
""")
