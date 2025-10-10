from textwrap import (
    dedent,
)

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
)

from ....tools.generated import (
    AnalysesActRole,
    AnalysesActType,
)

analyse_doc_type = SystemMessagePromptTemplate.from_template(
    dedent(
        f"""
        {{context}}
        
        ## Instructions
        We are formalizing your search criteria. For that purpose, we need to determine the kind record 
        we want to find.
                                                    
        Go through the list of document types. For each one, determine if it's a good fit to achieve the 
        **Current Partial Objective** using the given **Context** information. Explain your reasoning in one sentence.

        ### Posssible Document Types
        Here is the list of possible document types:

        {AnalysesActType.code_descriptions()}
        """
    )
)

select_doc_type = SystemMessagePromptTemplate.from_template(
    dedent(
        f"""
        {{context}}
        
        ## Instructions
        We are formalizing your search criteria. For that purpose, we need to determine the kind record 
        we want to find. Based on your evaluation, state which document type code is the single best choice.

        Please be extra-careful to use the appropriate code as they are case sensitive. 

        ### Posssible Document Types
        Here is the list of possible document types:

        {AnalysesActType.code_descriptions()}

        ### Your Evaluation
        {{evaluation}}
        """
    )
)


analyse_person_role = SystemMessagePromptTemplate.from_template(
    dedent(
        f"""
        {{context}}
        
        ## Instructions
        We are formalizing your search criteria. For that purpose, we need to determine the role played by {{who}}.
                                                    
        Go through the list of person roles. For each one, determine if it's a good fit to achieve the 
        **Current Partial Objective** using the given **Context** information. Explain your reasoning in one sentence.

        ### Possible Roles
        Here is the list of possible roles:
        {AnalysesActRole.code_descriptions()}
        """
    )
)

select_person_role = SystemMessagePromptTemplate.from_template(
    dedent(
        f"""
        {{context}}
        
        ## Instructions
        We are formalizing your search criteria. For that purpose, we need to determine the role played by {{who}}.
                                                    
        Based on your evaluation, state which document type code is the single best choice.

        Please be extra-careful to use the appropriate code as they are case sensitive. 

        ### Possible Roles
        Here is the list of possible roles:
        {AnalysesActRole.code_descriptions()}

        ### Your Evaluation
        {{evaluation}}
        """
    )
)

search_terms = SystemMessagePromptTemplate.from_template(
    dedent(
        """
        {context}

        ## Instructions
        What search terms to you wish to use ?
        These should be thought of as a means to perform a fulltext search. Wildcards ? and * 
        are authorized. Grouping is done by squaring an expression with double quotes ".
        Keywords must be separated by spaces only. 
        Respond with your search terms only. 

        ### IMPORTANT
        SOME ELEMENTS MAY NOT BE INCLUDED IN THE SEARCH TERM. These include:
        
            * Municipality name
            * Time period
            * Act type
        
        WHENEVER THIS RULE IS NOT RESPECTED, SEARCH IS GUARANTEED TO YIELD NO RESULT.
        """
    )
)
