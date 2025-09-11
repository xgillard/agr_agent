"""The prompts related to the creation of a search person request."""

from langchain_core.prompts import HumanMessagePromptTemplate

context = """
< Context >
You want to use the free_search_in_analyses_of_records feture of AGATHA because 
you would like to perform a general search to retrieve documents based on their
content.
</ Context >
"""

search_terms = HumanMessagePromptTemplate.from_template("""
{context}

< Instructions >
What search terms to you wish to use ?
These should be thought of as a means to perform a fulltext search. Wildcards ? and * 
are authorized. Grouping is done by squaring an expression with double quotes ".
Keywords must be separated by spaces only. 
Respond with your search terms only. 
</ Instructions >
""")