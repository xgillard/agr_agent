"""The prompts related to the creation of a search person request."""

from tools.analyses_of_records import AnalysesActType, AnalysesProject

location = """
< Context >
You want to search a document using the search in analyses of records from AGATHA.
</ Context >

< Instructions >
Where did the act you are searching took place ? (Leave empty unless the information was explicitly given).
</ Instructions >
"""

period = """
< Context >
You want to search a document using the search in analyses of records from AGATHA.
</ Context >

< Instructions >
When did the act happen ? (Leave empty unless the information was explicitly given).
</ Instructions >
"""

act_type = f"""
< Context >
You want to search a document using the search in analyses of records from AGATHA.
</ Context >

< Instructions >
What is the kind of document you are searching ? Select the most appropriate value among the
following options: 

{AnalysesActType.all_values()}
</ Instructions >
"""

project_type = f"""
< Context >
You want to search a document using the search in analyses of records from AGATHA.
</ Context >

< Instructions >
What project led to the analysis of the document you are searching for ? Leave this
field empty unless this information was explicitly given to you. If you pick a value,
it must be one of the following options:

{AnalysesProject.all_values()}
</ Instructions >
"""