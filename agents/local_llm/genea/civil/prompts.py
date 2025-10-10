"""
Prompts specific to the enrichment of genea church request.
"""

from textwrap import (
    dedent,
)

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
)

analyse_doctype = SystemMessagePromptTemplate.from_template(
    dedent(
        """
        {context}
        
        ## Instructions
        We are formalizing your search criteria. For that purpose, we need to determine the kind record 
        we want to find.
                                                    
        Go through the list of document types. For each one, determine if it's a good fit to achieve the 
        **Current Partial Objective** using the given **Context** information. Explain your reasoning in 
        one sentence.

        ### Posssible Document Types
        Here is the list of possible document types:
        
        * **Birth certificates** (code 1)
        * **Wedding certificates** (code 2)
        * **Death certificates** (code 3)
        * **Additional register** (code BS_U): Supplement to a register containing exhibited documents (extracts) or notes.
        * **Adoption certificates** (code BS_A)
        * **Death annexes** (code BS_Ob): Extracts of deaths abroad or death declarations of missing persons 
            (after the World Wars) attached to death certificates.
        * **Divorce certificates** (code BS_E)
        * **Naturalisation certificates** (code BS_N)
        """ # noqa: E501
    )
)

select_doctype = SystemMessagePromptTemplate.from_template(
    dedent(
        """
        {context}
        
        ## Instructions
        We are formalizing your search criteria. For that purpose, we need to determine the kind record 
        we want to find. Based on your evaluation, at least one document type corresponding to the best
        choice. Pay attention to using the exact code as they are mentioned since they are case sensitive.

        ### Posssible Document Types
        Here is the list of possible document types:
        
        * **Birth certificates** (code 1)
        * **Wedding certificates** (code 2)
        * **Death certificates** (code 3)
        * **Additional register** (code BS_U): Supplement to a register containing exhibited documents (extracts) or notes.
        * **Adoption certificates** (code BS_A)
        * **Death annexes** (code BS_Ob): Extracts of deaths abroad or death declarations of missing persons 
            (after the World Wars) attached to death certificates.
        * **Divorce certificates** (code BS_E)
        * **Naturalisation certificates** (code BS_N)

        ### Your Evaluation
        {evaluation}
        """ # noqa: E501
    )
)