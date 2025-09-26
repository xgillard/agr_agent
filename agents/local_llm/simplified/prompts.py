"""prompts to implements the simplified agatha workflow."""

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langchain_core.prompts import (
    StringPromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)

system_prompt = SystemMessage(
"""Your name is Arkey. You are an expert AI customer support at the 
belgian state archive. You are known for being factual, and always
providing reliable information. Whenever you doubt, about a statement
you wish to make (e.g. if you haven't had the opportunity to verify the
data yourself), you prefer to be transparent about it rather than
risking to give erroneous information.
""")

formalize = HumanMessagePromptTemplate.from_template("""
{input}

< Instructions >
Formalize the data that has been given to you. 

Whenever you mention a municipality name, it MUST USE either 
the French or the Dutch spelling of that name.

When a data is unknown, just leave it out. The goal is to formalize only what you know.
</ Instructions >

< Examples >
>>> I would like to find the birth certificate of Wim Van Piperzeel
>>> who was born in Sterrebeek in the early 1800.
```
{{
    "municipality_name": "Sterrebeek",
    "type_of_record": "Birth certificates",
    "people": [
        {{ "first_name": "Wim", "family_name": "Van Piperzeel", "role": "Child"}}
    ],
    "from_year": 1800,
    "until_year": 1810,
}}
```

>>> I would like to find the marriage notice of my great grand father Olivier Outsiplout.
```
{{
    "type_of_record": "Notices of marriage",
    "people": [
        {{ "first_name": "Olivier", "family_name": "Olivier Outsiplout", "role": "Groom"}}
    ],
}}
```
</ Examples >
""")


what_objective = HumanMessagePromptTemplate.from_template(
"""
< Context >
{scratch}
</ Context >

< AvailableData >
{available_data}
</ AvailableData >

< Tools >
{tools_descr}
</ Tools >

< Instructions >
What is your current partial objective ?

Your response must be formatted as a user story that provides all the necessary context.
It should adhere to one of the following schemas:

    - I want to find the help section about [WHAT] in the user manual.
    - I want to find the FAQ section related to [TOPIC].
    - I want to find the details of [WHAT] where [RELEVANT FACTS].
    - I want to find the details of [WHAT] where [RELEVANT FACTS] in [YEAR].
    - I want to find the details of [WHAT] where [RELEVANT FACTS] between [YEAR] and [YEAR].
    - I want to find the details of [WHAT] where [RELEVANT FACTS] before [YEAR].
    - I want to find the details of [WHAT] where [RELEVANT FACTS] after [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [MUNICIPALITY] in [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [MUNICIPALITY] between [YEAR] and [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [MUNICIPALITY] before [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [MUNICIPALITY] after [YEAR].
    - I want to stop and send my definitive response to the user.

**Notes**
    * All placeholders from the templates must be instantiated with known facts. Hence, if a template you want 
        to uses requires data which you have not explicitly seen before, it means that you CANNOT USE THAT TEMPLATE. 
    * When specifying a date range in your user story, be as specific as possible (2-3 years).
        Any period that is longer than that will lead to incomplete results as the full list might be truncated.    

You can only search for ONE piece of information at a time. So you can only express one single user 
story in your response.
</ Instructions >
""")

what_tool = HumanMessagePromptTemplate.from_template(
""""
< Context >
{scratch}
</ Context >

< Tools >
{tool_descr}
</ Tools >

< Instructions >
What tool will you use to find the information required to deal with the following user story ?
{thought}

(Select one option among: {tool_names})
</ Instructions >
""")

search_terms = HumanMessage("""
< Instructions >
What search terms to you wish to use ?
These should be thought of as a means to perform a fulltext search. Wildcards ? and * 
are authorized. Grouping is done by squaring an expression with double quotes ".
Keywords must be separated by spaces only. 
Respond with your search terms only. 
</ Instructions >
""")


respond = HumanMessagePromptTemplate.from_template("""
< Context >
{scratch}
</ Context >
< Instructions >
Respond to the user's original request.
</ Instructions>
""")

summarize = HumanMessagePromptTemplate.from_template("""
< Context >
Here is my reasoning so far:
{scratch}
</ Context >
                                                     
< LatestSearch >
Thought: {thought}
                                                     
Action: I have used {call_tool} with the following parameters:
{call_request}
                                                     
Observation: Here is the raw data from the original sources
{call_data}
</ LatestSearch >

< Instructions >
Summarize the relevant information from the latest search so that I can memorize only those facts which are
relevant to satisfying the original user's request. Feel free to make any observation you deem
useful about the data. Feel free to revise your plan as needed according to the data you have.
</ Instructions >
                                                     
< Note >
Whenever a date mentioned in the results is in a far away future (e.g. 2999-12-31), it has to be interpreted
as a placeholder for a date that is not known.
</ Note >
""")
