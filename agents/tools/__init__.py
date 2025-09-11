"""The tools that can be used by agents"""


from .agatha_help import agatha_knowledge
from .analyses_of_records import (
    tool_free_search_in_analyses_of_records,
    tool_search_person_in_analyses_of_records,
)
from .genealogy import (
    CivilActType,
    CivilIndex,
    GenealogyDocument,
    OtherCivilActType,
    OtherParishActType,
    ParishActType,
    ParishIndex,
    genealogy_search_church_registers_prior_to_1796,
    genealogy_search_civil_state_registers,
)

__ALL__ = [
    # help
    agatha_knowledge,
    # genealogy
    genealogy_search_church_registers_prior_to_1796,
    genealogy_search_civil_state_registers,
    #
    tool_free_search_in_analyses_of_records,
    tool_search_person_in_analyses_of_records,
    # useful types to re-export
    CivilActType,
    CivilIndex,
    GenealogyDocument,
    OtherCivilActType,
    OtherParishActType,
    ParishActType,
    ParishIndex,
]