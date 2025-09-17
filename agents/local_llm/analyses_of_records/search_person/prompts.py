"""The prompts related to the creation of a search person request."""

from langchain_core.prompts import HumanMessagePromptTemplate

from ....tools.analyses_of_records import AnalysesActRole

###### ADD PERSON WIZZARD ####################################################

family_name = HumanMessagePromptTemplate.from_template("""
{context}

< Instructions >
What is the **FAMILY NAME** of {full_name} ? (When unknown, respond with an empty string)
</ Instructions >
""")

first_name = HumanMessagePromptTemplate.from_template("""
{context}

< Instructions >
What is the **GIVEN NAME** of {full_name} ? (When unknown, respond with an empty string)
</ Instructions >
""")

job_name = HumanMessagePromptTemplate.from_template("""
{context}

< Instructions >
What is the **PROFESSION** (or occupation) of {full_name} ? (When unknown, respond with an empty string)
</ Instructions >
""")

role_name = HumanMessagePromptTemplate.from_template(f"""
{{context}}

< Instructions >
In the document you are searching, what was the role played by {{full_name}}
(choose one among the following propositions) ?

{AnalysesActRole.all_values()}
</ Instructions >
""")

###### SEARCH PERSON WIZZARD ####################################################
list_known_people = HumanMessagePromptTemplate.from_template("""
{context}

< Instructions >
List the full name of all people whoa participated in the act you are looking for.
When both a person's first and family name are unknown, do not list that persons.
</ Instructions >
""")
