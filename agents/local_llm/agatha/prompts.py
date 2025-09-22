"""Prompts for the react-style agent that interacts with agatha."""

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langchain_core.prompts import (
    HumanMessagePromptTemplate,
)

from .schemas import (
    DataSource,
    YesNo,
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
"""In order to accomplish your task, you can use the following resources as often as you like:

   * analyses_of_records: this will let you find the details of an official act based on the *content* 
       of that act. For instance, if you know the name of some people that were involved in that act 
       or if you know some specific keyword that might help retrieve the act you need. This tool is 
       particularly useful when you need to answer the questions *WHO*, *WHERE*, *WHEN* or *WHAT*.

   * digitized_registers: this will let you find digitized scans of the original registers where 
       official acts have been consigned. This is often helpful in order to find the scan of a specific
       act. In order to use this tool, you need to know some details about the register (or act) you
       wish to find. Namely, you need to know:

           - _WHAT KIND OF DOCUMENT_ you wish to retrieve
           - _WHERE_ the act happened
           - _WHEN_ it happened (at least have an idea of the date range) 
                   
       Please note that using the identifier of an act is of absolutely *NO USE* when searching for
       a scan. The afore mentioned details must be repeated for that purpose. 

   * help_resources: this will let you search information in the user manuals and FAQ sections of
       the AGATHA platform. This is mostly useful to answer *HOW DO I ...* questions.
""")


system_prompt = SystemMessage(f"{persona}\n\n{tool_descr}")

decide = HumanMessage(f"""
Do you think it would be useful to use your tools before to answer to the user ? ({YesNo.all_values()})
""")

what_information = HumanMessage(
"""What information do you need to find ? 
(You can use previous search results -- if any -- to refine your request)

Your response must be formatted as a user story that provides all the necessary context.
It should adhere to one of the following schemas:

    - I want to find the help section about [WHAT] in the user manual.
    - I want to find the FAQ section related to [TOPIC].
    - I want to find the details of [WHAT] where [RELEVANT FACTS].
    - I want to find a digitized scan of [WHAT] that happened in [LOCATION] in [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [LOCATION] between [YEAR] and [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [LOCATION] before [YEAR].
    - I want to find a digitized scan of [WHAT] that happened in [LOCATION] after [YEAR].
""")

what_source = HumanMessage(
f""""
< Context >
{tool_descr}
</ Context >

< Instructions >
What tool will you use to find information ? 
(Select one option among: {DataSource.all_values()})
</ Instructions >
""")

summarize = HumanMessagePromptTemplate.from_template("""
< Context >
I have searched in the available sources, and here is what I found: 
{raw_data}
< Context >

< Instructions >
Summarize the relevant information out loud so that I can memorize only those facts which are
relevant to satisfying the original user's request. Feel free to make any observation you deem
useful about the data.
</ Instructions >
""")

respond = HumanMessage("Respond to the user's original request.")
