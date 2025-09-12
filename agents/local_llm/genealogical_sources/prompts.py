"""The prompts related to the searching in the genealogical sources."""

from langchain_core.messages import HumanMessage

from .schemas import GeneaTool

triage = HumanMessage(f"""
< Context >
You want to search digitized document using the search in genealogic sources
capabilities from AGATHA. For this purpose, the platform offers two possibilities:

* "{GeneaTool.CHURCH_REGISTERS._value_}" which you should use when you want 
    to search a document that was created **PRIOR TO** anno 1796.

* "{GeneaTool.CIVIL_STATE_REGISTERS._value_}" which you should use when you want 
    to search a document that was created **AFTER** anno 1796. 
</ Context >

< Instruction >
Which tool would you like to use among these two ?
</ Instruction >
""")