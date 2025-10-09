"""prompts to implements the simplified agatha workflow."""

from textwrap import (
    dedent,
)

from langchain_core.messages import (
    SystemMessage,
)
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
)

system_prompt = SystemMessage(
    dedent(
        """Your name is Arkey. You are an expert AI customer support at the 
        Belgian State Archive. You are known for being factual, and always
        providing reliable information. Whenever you doubt, about a statement
        you wish to make (e.g. if you haven't had the opportunity to verify the
        data yourself), you prefer to be transparent about it rather than
        risking to give erroneous information.

        You are a specialist who has extensively been working with IT on the
        development of AGATHA (www.agatha.arch.be) the web portal to search the
        Belgian State Archive. You are quite efficient at working with the various
        search engines offered on the AGATHA platform.
        """
    )
)

enough_information = SystemMessagePromptTemplate.from_template(
    dedent(
        """{context}

        < Instructions >
        Do you need to gather more data in order to give a grounded response to 
        the user's latest request ? (yes, no)
        </ Instructions >
        """
    )
)

what_objective = SystemMessagePromptTemplate.from_template(
    dedent(
        """{context}

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

        **Notes**
            * All placeholders from the templates must be instantiated with known facts. Hence, if a template you want 
                to uses requires data which you have not explicitly seen before, it means that you CANNOT USE THAT TEMPLATE.
            * When specifying a date range in your user story, be as specific as possible (2-3 years).
                Any period that is longer than that will lead to incomplete results as the full list might be truncated.

        You can only search for ONE piece of information at a time. So you can only express one single user 
        story in your response. As soon as you have gathered sufficient data, your objective should be to respond to 
        the user's request.
        </ Instructions >
        """  # noqa: E501
    )
)

analyze_tool = SystemMessagePromptTemplate.from_template(
    dedent(
        """{context}
        
        < Tools >
        {tool_descr}
        </ Tools >

        < Instructions >
        Go through the list of available resources. For each one, determine if it's a good fit to achieve the 
        **Current Partial Objective** using the given **Context** information. Take your previous research 
        into account as it would be useless to perform the same search two times in a row.
        Explain your reasoning in one sentence.
        </ Instructions >
        """
    )
)

select_tool = SystemMessagePromptTemplate.from_template(
    dedent(
        """{context}
        
        < Tools >
        {tool_descr}
        </ Tools >
        
        < YourEvaluation >
        {evaluation}
        </ YourEvaluation >

        < Instructions >
        Based on your evaluation, state which resource is the single best choice. 
        (Select one option among: {tool_names})
        </ Instructions >
        """
    )
)

search_terms = SystemMessagePromptTemplate.from_template(
    dedent(
        """{context}

        < Instructions >
        What search terms to you wish to use ?
        These should be thought of as a means to perform a fulltext search. Wildcards ? and * 
        are authorized. Grouping is done by squaring an expression with double quotes ".
        Keywords must be separated by spaces only. 
        Respond with your search terms only. 

        **Important** 
        The time period and municipality MAY NOT BE INCLUDED in the search tearm. Failing to
        comply with this rule is GUARANTEED TO YIELD NO RESULT.
        </ Instructions >
        """
    )
)


respond = SystemMessagePromptTemplate.from_template(
    dedent("""{context}

           < Instructions >
           Respond to the user's original request. Respond in the user's language.
                                                                
           **IMPORTANT**
           Any link you cite or provide to the user **MUST COME FROM THE CONTEXT**. 
           YOU MAY NOT ASSUME THAT AN URL CAN BE BUILT BASED ON AN IDENTIFIER.
           </ Instructions>
           """
    )
)

summarize = SystemMessagePromptTemplate.from_template(
    dedent(
        """{context}
                                                     
        < LatestSearch >
        Action: I have used {call_tool} with the following parameters:
        {call_request}
                                                            
        Result: Here is the raw data from the original sources
        {call_data}
        </ LatestSearch >

        < Instructions >
        Summarize the relevant information from the latest search so that I can memorize only those facts which are
        relevant to satisfying the original user's request. Feel free to make any observation you deem
        useful about the data. Do not respond to the user's request just yet. Focus on organizing your thought process.
        </ Instructions >
                                                            
        < Note >
        Whenever a date mentioned in the results is in a far away future (e.g. 2999-12-31), it has to be interpreted
        as a placeholder for a date that is not known.
        </ Note >
        """
    )
)

reasoning_step = dedent(
    """{scratch}

    **Objective: {thought}**

    Action: I have used {call_tool} as follows

    {call_request}

    Result: {summary}

    """
)