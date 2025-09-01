"""The tools that can be used by agents"""


from .agatha_help import agatha_knowledge
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
    agatha_knowledge,
    genealogy_search_church_registers_prior_to_1796,
    genealogy_search_civil_state_registers,
    # useful types to re-export
    CivilActType,
    CivilIndex,
    GenealogyDocument,
    OtherCivilActType,
    OtherParishActType,
    ParishActType,
    ParishIndex,
]