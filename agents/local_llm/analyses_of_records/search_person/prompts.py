"""The prompts related to the creation of a search person request."""

from tools.analyses_of_records import AnalysesActRole

###### ADD PERSON WIZZARD ####################################################

family_name = """
What is the **FAMILY NAME** of {full_name} ? (When unknown, respond with an empty string)
"""

first_name = """
What is the **FIRST NAME** of {full_name} ? (When unknown, respond with an empty string)
"""

job_name = """
What is the **PROFESSION** (or occupation) of {full_name} ? (When unknown, respond with an empty string)
"""

role_name = f"""
In the document you are searching, what was the role played by {{full_name}}
(choose one among the following propositions) ?

{AnalysesActRole.all_values()}
"""

###### SEARCH PERSON WIZZARD ####################################################
list_known_people = """
< Context >
You want to use the search_person_in_analyses_of_records because you know
some people that partake to the archived document you are looking for.
</ Context >

< Instructions >
List the full name of all people whoa participated in the act you are looking for.
When both a person's first and family name are unknown, do not list that persons.
</ Instructions >
"""
