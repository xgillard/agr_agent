"""The prompts related to the creation of a search person request."""

from .schemas import AnalysesOfRecordsTool

triage = f"""
< Context >
You want to search a document using the search in analyses of records capabilities 
from AGATHA. For this purpose, the platform offers two possibilities:

* "{AnalysesOfRecordsTool.FREE_SEARCH._value_}" which you should use when you want 
    to conduct a 'general search' using keywords to retrieve a document.

* "{AnalysesOfRecordsTool.SEARCH_PERSON._value_}" which should be used to conduct
    targeted search, for the case when you know the name of people who were involved
    (+ posibly their role) in the act you are searching for.
</ Context >

< Instruction >
Which tool would you like to use among these two ?
</ Instruction >
"""