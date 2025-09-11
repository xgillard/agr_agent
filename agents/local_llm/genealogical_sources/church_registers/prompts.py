"""The prompts related to the searching in church registers."""

context = """
< Context >
You want to search the digitized copy of an administrative act in the 
genealogical sources of AGATHA.
</ Context >
"""

location = f"""
{context}

< Instructions >
Where did the act you are searching took place ? (Municipality)
</ Instructions >
"""

parish = f"""
{context}

< Instructions >
Where did the act you are searching took place ? (Municipality)
</ Instructions >
"""
