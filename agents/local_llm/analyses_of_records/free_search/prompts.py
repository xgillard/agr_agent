"""The prompts related to the creation of a search person request."""

from langchain_core.messages import HumanMessage

search_terms = HumanMessage("""
< Instructions >
What search terms to you wish to use ?
These should be thought of as a means to perform a fulltext search. Wildcards ? and * 
are authorized. Grouping is done by squaring an expression with double quotes ".
Keywords must be separated by spaces only. 
Respond with your search terms only. 
</ Instructions >
""")