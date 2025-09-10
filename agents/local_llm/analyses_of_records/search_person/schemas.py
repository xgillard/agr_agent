"""Data types to implement the search person in analyses of records tool call."""

from langgraph.graph import MessagesState
from pydantic import BaseModel

from tools.analyses_of_records import (
    AnalysesActRole,
    PersonCriterion,
)

from ..common.schemas import SearchAnalysesState

###### ADD PERSON WIZZARD #######################################################

class AddPersonWizzardState(MessagesState, total=False):
    """The internal state of the wizzard process to add a person criterion.
    
    Attributes:
        full_name (str): the full name (or the way the person to add is known in the original unstructured output)
        
        first_name (str | None): the persons's first name if available (e.g. Jean, Jan, Michel, Xavier)
        family_name (str | None): the person's family name if available (e.g. Dupoont, Verbruggen)
        profession (str | None): the person's profession if known (e.g. farmer, accountant, housewive)
        act_role (AnalysesActRole | None): the role played by this person in the act we are searching for
    """

    full_name: str
    
    first_name: str | None
    family_name: str | None
    profession: str | None
    role: AnalysesActRole | None


class FirstName(BaseModel):
    """First name.
    
    Attributes:
        first_name (str|None): the first name
    """

    first_name: str | None = None


class FamilyName(BaseModel):
    """Family name.

    Attributes:
        family_name (str|None): the family name
    """

    family_name: str | None = None


class Profession(BaseModel):
    """Profession.
    
    Attributes:
        profession (str|None): the profession
    """

    profession: str | None = None


class RoleChoice(BaseModel):
    """Role choice.
    
    Attributes:
        role (AnalysesActRole | None): the selected role.
    """
    
    role: AnalysesActRole | None = None


###### SEARCH PERSON WIZZARD ####################################################
class ListOfPeople(BaseModel):
    """List of known people.
    
    Attributes:
        list_of_names (list[str]): the list of people
    """

    list_of_names: list[str]


class SearchPersonWizzardState(SearchAnalysesState, total=False):
    """The internal state of the wizzard process to create a search request.

    Attributes:
        known_people (list[str]): a list comprising the name of all the persons that should be added to
            the search request.
        persons (list(PersonCriterion)): the list of people that are used to retrieve a given act.
    """

    known_people: list[str]
    persons: list[PersonCriterion]

