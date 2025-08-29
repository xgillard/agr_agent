"""The tools that can be used by agents"""


from .agatha_help import agatha_knowledge
from .genealogy import (
    CivilActType,
    OtherCivilActType,
    CivilIndices,
    ParishActType,
    OtherParishActType,
    ParishIndices,
    GenealogyDocument,
    genealogy_search_civil_state_registers,
    genealogy_search_church_registers_prior_to_1796,
)

__ALL__ = [
    agatha_knowledge,
    genealogy_search_church_registers_prior_to_1796,
    genealogy_search_civil_state_registers,
]