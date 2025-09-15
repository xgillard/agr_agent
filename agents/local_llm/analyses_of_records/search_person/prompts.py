"""The prompts related to the creation of a search person request."""

from langchain_core.prompts import HumanMessagePromptTemplate

from ....tools.analyses_of_records import AnalysesActRole

###### ADD PERSON WIZZARD ####################################################

family_name = HumanMessagePromptTemplate.from_template("""
What is the **FAMILY NAME** of {full_name} ? (When unknown, respond with an empty string)
""")

first_name = HumanMessagePromptTemplate.from_template("""
What is the **FIRST NAME** of {full_name} ? (When unknown, respond with an empty string)
""")

job_name = HumanMessagePromptTemplate.from_template("""
What is the **PROFESSION** (or occupation) of {full_name} ? (When unknown, respond with an empty string)
""")

role_name = HumanMessagePromptTemplate.from_template(f"""
In the document you are searching, what was the role played by {{full_name}}
(choose one among the following propositions) ?

{AnalysesActRole.all_values()}
""")

###### SEARCH PERSON WIZZARD ####################################################
list_known_people = """
{context}

< Instructions >
List the full name of all people whoa participated in the act you are looking for.
When both a person's first and family name are unknown, do not list that persons.
</ Instructions >
"""
