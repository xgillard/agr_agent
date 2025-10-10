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
        
        * **birth or baptism certificate** (code 1)
        * **wedding certificate** (code 2)
        * **funeral / death certificate** (code 3)
        * **marriage exemption certificate** (code 12): Certificates of dispensations of marriage
            (Certificate by which an authority releases a person from an obligation or prohibition, 
            in this case the celebration of marriage.)
        * **marriage impediment certificate** (code 20): Certificates of impediment of marriage 
            (Certificate of objection to the marriage on the grounds of non-compliance with a condition 
            for the celebration of the marriage.)
        * **list of communiants** (code 11): List of communiants (Persons who have received the sacrament of eucharist)
        * **list of confirmands** (code 31): List of confirmands (Persons who have received the sacrament of confirmation)
        * **list of names** (code 23): List of person drawn up for an event (e.g. for Sunday prayers) 
            or for an association (e.g. membership list of a fraternity).
        * **memory masses** (code 56):  Memory masses (List of deceased persons for whom a church service 
            should be organised annually in memory and for the salvation of souls).
        * **status animarum** (code 28): List per street or district of the families in a parish 
            (state of souls), with information about the age of the residents, confirmation, ...
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
        choice.

        ### Posssible Document Types
        Here is the list of possible document types:
        
        * **birth or baptism certificate** (code 1)
        * **wedding certificate** (code 2)
        * **funeral / death certificate** (code 3)
        * **marriage exemption certificate** (code 12): Certificates of dispensations of marriage
            (Certificate by which an authority releases a person from an obligation or prohibition, 
            in this case the celebration of marriage.)
        * **marriage impediment certificate** (code 20): Certificates of impediment of marriage 
            (Certificate of objection to the marriage on the grounds of non-compliance with a condition 
            for the celebration of the marriage.)
        * **list of communiants** (code 11): List of communiants (Persons who have received the sacrament of eucharist)
        * **list of confirmands** (code 31): List of confirmands (Persons who have received the sacrament of confirmation)
        * **list of names** (code 23): List of person drawn up for an event (e.g. for Sunday prayers) 
            or for an association (e.g. membership list of a fraternity).
        * **memory masses** (code 56):  Memory masses (List of deceased persons for whom a church service 
            should be organised annually in memory and for the salvation of souls).
        * **status animarum** (code 28): List per street or district of the families in a parish 
            (state of souls), with information about the age of the residents, confirmation, ...

        ### Your Evaluation
        {evaluation}
        """ # noqa: E501
    )
)