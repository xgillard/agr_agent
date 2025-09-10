"""The prompts related to the creation of a search person request."""

search_terms = """
< Context >
You want to use the free_search_in_analyses_of_records feture of AGATHA because 
you would like to perform a general search to retrieve documents based on their
content.
</ Context >

< Instructions >
What keywords to you wish to use in order to carry your search ?
</ Instructions >

< Examples >
The results of a search for the word “brasseur” (brewer) will include records mentioning a person
named “Brasseur”, records mentioning someone practising the profession of brewer, and notarial deeds in
which the word “brasseur” is mentioned in the description and/or remarks.

Inverted commas may be used for exact searches. The search engine will then display the keywords in the
same order as indicated in the search field.
Example:
- Without inverted commas = vente moulin (sale mill) > the search engine looks for the occurrence of
the words “vente” and “moulin” regardless of the order or presence of these keywords together.
- With inverted commas = “Vente moulin” > the engine searches only scans for those occurrences of
the terms in which the keywords
Vente moulin are written together and in the same order.

It is also possible to use an asterisk (*) and a question mark (?) to search for names that match one or more
characters at the beginning or end of a search term (*) or for which a letter is not known (?).
Example:
- *Mart* for Demarteau, Jacquemart, Martin or Martens.
- De ?oninck for De Coninck or De Koninck.
</ Examples >
"""
