"""The prompts related to the creation of a search person request."""

from langchain_core.messages import HumanMessage
from langchain_core.prompts import HumanMessagePromptTemplate

from ....tools.analyses_of_records import AnalysesActRole

###### ADD PERSON WIZZARD ####################################################

family_name = HumanMessagePromptTemplate.from_template("""
< Instructions >
What is the **FAMILY NAME** of {full_name} ? (When unknown, respond with an empty string)
</ Instructions >
""")

first_name = HumanMessagePromptTemplate.from_template("""
< Instructions >
What is the **GIVEN NAME** of {full_name} ? Note that this might be compound, eg 'Jean Michel'.
(When unknown, respond with an empty string)
</ Instructions >
""")

job_name = HumanMessagePromptTemplate.from_template("""
< Instructions >
What is the **PROFESSION** (or occupation) of {full_name} ? (When unknown, respond with an empty string)
</ Instructions >
""")

role_name = HumanMessagePromptTemplate.from_template(f"""
< Instructions >
In the document you are searching, what was the role played by {{full_name}}
(choose one among the following propositions) ?

{AnalysesActRole.all_values()}
</ Instructions >
""")

###### SEARCH PERSON WIZZARD ####################################################
list_known_people = HumanMessage("""
< Instructions >
List the full name of all people who participated in the act you are looking for.

Constraints:
    * When both a person's first and family name are unknown, do not list that persons.
    * Only list people that have explicitly been mentioned above.
</ Instructions >
""")
