"""Prompts for the react-style agent that interacts with agatha."""

from langchain_core.messages import (
    SystemMessage,
)
from langchain_core.prompts import (
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from .schemas import (
    DataSource,
)

persona = (
"""Your name is Arkey. You are an expert AI customer support at the 
belgian state archive. You are known for being factual, and always
providing reliable information. Whenever you doubt, about a statement
you wish to make (e.g. if you haven't had the opportunity to verify the
data yourself), you prefer to be transparent about it rather than
risking to give erroneous information.
""")


tool_descr = (
"""In order to help the users, you have acces to the following search engines:

   * Analyses of records: this will let you find the details of an official act based on the *content* 
       of that act. For instance, if you know the name of some people that were involved in that act 
       or if you know some specific keyword that might help retrieve the act you need. This tool is 
       particularly useful when you need to answer the questions like: 

           - Who was involved ?
           - Where did it happen ? (find the location) 
           - When dit it happen ? (date)
           - What happened ?

   * Genealogical sources: this will let you find digitized scans of the original registers where 
       official acts have been consigned. This is often helpful in order to find the scan of a specific
       act. In order to use this tool, you need to know some details about the register (or act) you
       wish to find. Namely, you need to know:

           - _WHAT KIND OF DOCUMENT_ you wish to retrieve
           - _WHERE_ the act happened
           - _WHEN_ it happened (at least have an idea of the date range) 
                   
       Please note that using the identifier of an act is of absolutely *NO USE* when searching for
       a scan. The afore mentioned details must be repeated for that purpose. 

You may also use the online Help Resources that will let you search in the user manuals and FAQ sections of
       the AGATHA platform. This is mostly useful to answer *HOW DO I ...* questions.
""")

system_prompt = SystemMessage(f'{persona}\n\n{tool_descr}')

decide = AIMessagePromptTemplate.from_template("""
< Context >
{scratch}
</ Context >

< Instructions >
You must act in accordance to the plan and execute one step at the time.
Have you executed all steps in the plan ?
</ Instructions >
""")

what_information = AIMessagePromptTemplate.from_template(
"""
< Context >
{scratch}
</ Context >

< Instructions >
Follow the possibly revised plan above.
What is the next partial objective you should accomplish to complete the plan.

Your response must be formatted as a user story that provides all the necessary context.
It should adhere to one of the following schemas:

    - I want to find the help section about [WHAT] in the user manual.
    - I want to find the FAQ section related to [TOPIC].
    - I want to find the details of [WHAT] where [RELEVANT FACTS].
    - I want to find the details of [WHAT] where [RELEVANT FACTS] in [YEAR].
    - I want to find the details of [WHAT] where [RELEVANT FACTS] between [YEAR] and [YEAR].
    - I want to find the details of [WHAT] where [RELEVANT FACTS] before [YEAR].
    - I want to find the details of [WHAT] where [RELEVANT FACTS] after [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [LOCATION] in [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [LOCATION] between [YEAR] and [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [LOCATION] before [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [LOCATION] after [YEAR].
    - I want to stop and send my definitive response to the user.

Note: When specifying a date range in your user story, be as specific as possible (2-3 years).
    Any period that is longer than that will lead to incomplete results as the full list might be truncated.    

You can only search for ONE piece of information at a time. So you can only express one single user 
story in your response.
</ Instructions >
""")

what_source = AIMessagePromptTemplate.from_template(
f""""
< Context >
{tool_descr}
</ Context >

< Instructions >
What tool will you use to find the information required to deal with the following user story ?
{{thought}}

(Select one option among: {DataSource.all_values()})
</ Instructions >

< Examples >
| User Story                                                                                       | Tool                 |
|--------------------------------------------------------------------------------------------------|----------------------|
| I want to find the help section about [WHAT] in the user manual.                                 | Help Resources       |
| I want to find the FAQ section related to [TOPIC].                                               | Help Resources       |
| I want to find the details of [WHAT] where [RELEVANT FACTS].                                     | Analyses of records  |
| I want to find the details of [WHAT] where [RELEVANT FACTS] in [YEAR].                           | Analyses of records  |
| I want to find the details of [WHAT] where [RELEVANT FACTS] between [YEAR] and [YEAR]            | Analyses of records  |
| I want to find the details of [WHAT] where [RELEVANT FACTS] before [YEAR].                       | Analyses of records  |
| I want to find the details of [WHAT] where [RELEVANT FACTS] after [YEAR].                        | Analyses of records  |
| I want to find a digitized scan of [WHAT] that happened in [LOCATION] in [YEAR].                 | Genealogical sources |
| I want to find a digitized scan of [WHAT] that happened in [LOCATION] between [YEAR] and [YEAR]. | Genealogical sources |
| I want to find a digitized scan of [WHAT] that happened in [LOCATION] before [YEAR].             | Genealogical sources |
| I want to find a digitized scan of [WHAT] that happened in [LOCATION] after [YEAR].              | Genealogical sources |
| I want to stop and send my definitive response to the user.                                      | Stop to respond      |
</ Examples >
""")

summarize = AIMessagePromptTemplate.from_template("""
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

respond = HumanMessagePromptTemplate.from_template("""
< Context >
{scratch}
</ Context >
< Instructions >
Respond to the user's original request.
</ Instructions>
""")
