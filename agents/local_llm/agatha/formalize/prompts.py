"""prompts to implements the formalization workflow."""

from textwrap import (
    dedent,
)

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
)

base_info = SystemMessagePromptTemplate.from_template(
    dedent(
        """
        {context}

        < Instructions >
        Formalize your search criteria.

        Whenever you mention a municipality name, it MUST USE either 
        the French or the Dutch spelling of that name.

        When a data is unknown, just leave it out. The goal is to formalize only what you know
        or wish to use as criterion during your search.
        </ Instructions >

        < Examples >
        >>> I would like to find the birth certificate of Wim Van Piperzeel
        >>> who was born in Sterrebeek in the early 1800.
        ```
        {{
            "municipality_name_in_french_or_dutch": "Sterrebeek",
            "people": [
                {{ "first_name": "Wim", "family_name": "Van Piperzeel"}}
            ],
        }}
        ```

        >>> I would like to find the marriage notice of my great grand father Olivier Outsiplout
        >>> and his wife Maria Hermans.
        ```
        {{
            "people": [
                {{ "first_name": "Olivier", "family_name": "Olivier Outsiplout" }},
                {{ "first_name": "Maria", "family_name": "Hermans" }},
            ],
        }}
        ```
        </ Examples >
        """
    )
)

period_of_interest = SystemMessagePromptTemplate.from_template(
    dedent(
        """
        {context}

        < Instructions >
        What period you you wish to use in your search criteria.

        When a data is unknown, just leave it out.
        </ Instructions >

        < Examples >
        >>> I would like to find the birth certificate of Wim Van Piperzeel
        >>> who was born in Sterrebeek in the early 1800.
        ```
        {{
            "min_date_formatted_as_yyyy_mm_dd": "1800-01-01",
            "max_date_formatted_as_yyyy_mm_dd": "1810-12-31"
        }}
        ```

        >>> I would like to find the marriage notice of my great grand father Olivier Outsiplout
        >>> and his wife Maria Hermans.
        ```
        {{
            "min_date_formatted_as_yyyy_mm_dd": none,
            "max_date_formatted_as_yyyy_mm_dd": none
        }}
        ```
        </ Examples >
        """
    )
)

analyse_doc_type = SystemMessagePromptTemplate.from_template(
    dedent(
        """
        {context}
        
        < Instructions >
        We are formalizing your search criteria. For that purpose, we need to determine the kind record 
        we want to find.
                                                    
        Go through the list of document types. For each one, determine if it's a good fit to achieve the 
        **Current Partial Objective** using the given **Context** information. Explain your reasoning in one sentence.
        </ Instructions >

        < Note >
        Here is the list of possible document types:
        {type_of_record_code_desc}

        **IMPORTANT** 
        Baptism-related documents types and baptism-related roles CANNOT BE USED find records posterior to anno 1796.
        Searching a Baptism certificate, or searching a Baptised-Child in 1797 or after is GUARANTEED TO FAIL.
        </ Note >
        """
    )
)

select_doc_type = SystemMessagePromptTemplate.from_template(
    dedent(
        """
        {context}
        
        < Instructions >
        We are formalizing your search criteria. For that purpose, we need to determine the kind record 
        we want to find. Based on your evaluation, state which document type code is the single best choice.

        Please be extra-careful to use the appropriate code as they are case sensitive. 
        </ Instructions >

        < Note >
        Here is the list of possible document types:
        {type_of_record_code_desc}

        **IMPORTANT** 
        Baptism-related documents types CANNOT BE USED find records posterior to anno 1796.
        Searching a Baptism certificate, or searching a Baptised-Child in 1797 or after is GUARANTEED TO FAIL.
        </ Note >

        < YourEvaluation >
        {evaluation}
        </ YourEvaluation >
        """
    )
)

analyse_person_role = SystemMessagePromptTemplate.from_template(
    dedent(
        """
        {context}
        
        < Instructions >
        We are formalizing your search criteria. For that purpose, we need to determine the role played by {who}.
                                                    
        Go through the list of person roles. For each one, determine if it's a good fit to achieve the 
        **Current Partial Objective** using the given **Context** information. Explain your reasoning in one sentence.
        </ Instructions >

        < Note >
        Here is the list of possible document types:
        {type_of_roles_code_desc}

        **IMPORTANT** 
        Baptism-related roles CANNOT BE USED find records posterior to anno 1796.
        Searching a Baptism certificate, or searching a Baptised-Child in 1797 or after is GUARANTEED TO FAIL.
        </ Note >
        """
    )
)

select_person_role = SystemMessagePromptTemplate.from_template(
    dedent(
        """
        {context}
        
        < Instructions >
        We are formalizing your search criteria. For that purpose, we need to determine the role played by {who}.
                                                    
        Based on your evaluation, state which document type code is the single best choice.

        Please be extra-careful to use the appropriate code as they are case sensitive. 
        </ Instructions >

        < Note >
        Here is the list of possible document types:
        {type_of_roles_code_desc}

        **IMPORTANT** 
        Baptism-related roles CANNOT BE USED find records posterior to anno 1796.
        Searching a Baptism certificate, or searching a Baptised-Child in 1797 or after is GUARANTEED TO FAIL.
        </ Note >

        < YourEvaluation >
        {evaluation}
        </ YourEvaluation >
        """
    )
)
