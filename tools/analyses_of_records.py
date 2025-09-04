"""Data structure and tools implementation to search in analyses of records on AGATHA.

Date: 2025-09-01
Author: X. Gillard
"""

from functools import cached_property
from typing import Annotated, Optional

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, ConfigDict, Field

from .agatha_common import Municipality, PeriodSelector
from .generated import AnalysesActRole, AnalysesActType, AnalysesProject

## Constants
BASE_URL  = "https://agatha.arch.be/search"
FORM_URL  = f"{BASE_URL}/analyses/results/"
AJAX_URL  = f"{BASE_URL}/analyses/ajax.php"


def _clean(x: str|None) -> str|None:
        """Clean the value of x to remove the unnecessary 'NN' values and replace them with None.
        
        Args:
            x (str|None): the value we wish to clean
        
        Returns: 
            str|None:
                - the same value as x when x is different from 'NN'
                - None whenever x is None or x == 'NN'
            
        Examples:
            >>> _clean('NN')

            >>> _clean("coucou")
            'coucou'

            >>> _clean(None)

        """

        return x if x != 'NN' else None


class AnalysesPerson(BaseModel):
    """Data about a person that was mentioned in an anlysed archives record.

    Attributes:
        name (str): full name of the person mentioned in the document
        title (Optional[str]): title of the person mentioned in the document (eg. Dr) if relevant.
        role (AnalysesActRole): the person's role
        birth_date (Optional[str]): person's birthdate if available
        birth_place (Optional[str]): person's place of birth if available
        death_date (Optional[str]): person's death date if available
        death_place (Optional[str]): person's place of death if available
        age (Optional[str]): the person's age when the act happened (if known).
        civil_status (Optional[str]): person's civil status if available
        residence_location (Optional[str]): person's residence location if available
        occupation (Optional[str]): job/occupation of that person (if known)
        remarks (Optional[str]): remarks about the person
    """
    
    name: str
    title: Optional[str] = None
    role: AnalysesActRole
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_place: Optional[str] = None
    age: Optional[str] = None
    civil_status: Optional[str] = None
    residence_location: Optional[str] = None
    occupation: Optional[str] = None
    remarks: Optional[str] = None


class AnalysesAct(BaseModel):
    """Description of an administrative act that took place in the past.

    Attrtibutes:
        act_id (str): globally unique identifier of this administrative act
        act_number (Optional[str]): act number that was used by the archive producer
        project (AnalysesProject): the project that led to the analysis of this record
        actplace (Optional[str]): the place where this act officially happened
        parish (Optional[str]): the parish where this act officially happened (if relevant)
        editorial_form (str): the type of document
        description (str): a brief description of this document
        act_date (str): the date when this administrative act actually took place.
        remarks (str): some remarks about this act
        persons (list[AnalysesPerson]): people mentioned in the document.
    """

    act_id: str
    act_number: Optional[str]
    project: AnalysesProject
    actplace: Optional[str]
    parish: Optional[str]
    editorial_form: str
    description: Optional[str]
    act_date: Optional[str]
    remarks: Optional[str]
    persons: list[AnalysesPerson] 


class AnalysesSearchResponseDocument(BaseModel):
    """Description of a document in a raw response from Agatha.
    
    Note:
        The document response mixes concerns about the act itself and
        the people that are mentioned in the act. Plus, it uses a columnar
        format for the persons data which I think could be made more obvious
        if the data that belong together were grouped together. Which is
        why, I have only adopted a restricted subset of the information
        I intend to use in a downstream simplified version of the document.

        Additionally, it is important to note that in many case the value 'NN'
        is being used to mention that no data is available. Which is why i propose
        to filter those values out in the simplified version of the data model.
        
    Attrtibutes:
        # attributes that directly relate to the act itself
        act_id (str): globally unique identifier of this administrative act
        act_number (Optional[str]): act number that was used by the archive producer
        project (AnalysesProject): the project that led to the analysis of this record
        actplace (Optional[str]): the place where this act officially happened
        parish (Optional[str]): the parish where this act officially happened (if relevant)
        editorial_form (str): the type of document
        description (str): a brief description of this document
        act_date (str): the date when this administrative act actually took place.
        remarks (str): some remarks about this act
        # attributes relating to the persons that are mentioned in the act
        person_name (list[str]): list of names of the persons mentioned in the document
        person_title (list[str] | None): title of the persons mentioned in the document (eg. Dr)
        person_birth_date (list[str] | None): birthdates of the people mentioned in the document
        person_birth_place (list[str] | None): places of births of the people mentioned in the document
        person_death_date (list[str] | None): death date of these people
        person_death_place (list[str] | None): dath place of these people
        person_residence_location (list[str] | None): location where these people used to reside
        person_civil_status (list[str] | None): civil statuses of thes people
        person_remarks (list[str] | None): remarks about each of those people
        person_occupation (list[str] | None): the job of those people
        person_role_code (list[str]): the role each person played in the act
        person_age (list[str] | None): the age of all people when the act happened.
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    # attributes that belong to the act description itself.
    act_id: Annotated[str, Field(alias="ACT_ID")]
    act_number: Annotated[Optional[str], Field(alias="ACT_NUMBER")] = None
    project: Annotated[AnalysesProject, Field(alias="PROJECT_ID")]
    actplace: Annotated[Optional[str], Field(alias="ACTPLACE_STRING")] = None
    parish: Annotated[Optional[str], Field(alias="PARISH")] = None
    editorial_form: Annotated[str, Field(alias="EDITORIALFORM_ENG")]
    description: Annotated[str, Field(alias="ACT_DESCRIPTION")]
    act_date: Annotated[Optional[str], Field(alias="ACTDATE")] = None
    remarks: Annotated[Optional[str], Field(alias="REMARKS_ACT")] = None
    # attributes relating to the persons that are mentioned in the act
    person_name: Annotated[list[str], Field(alias="FULL_NAME")]
    person_title: Annotated[list[str] | None, Field(alias="TITLE_PERSON")] = None
    person_birth_date: Annotated[list[str] | None, Field(alias="BIRTHDATE")] = None
    person_birth_place: Annotated[list[str] | None, Field(alias="BIRTHPLACE")] = None
    person_death_date: Annotated[list[str] | None, Field(alias="DEATHDATE")] = None
    person_death_place: Annotated[list[str] | None, Field(alias="DEATHPLACE")] = None
    person_residence_location: Annotated[list[str] | None, Field(alias="RESIDENCE")] = None
    person_civil_status: Annotated[list[str] | None, Field(alias="CIVILSTATUS")] = None
    person_remarks: Annotated[list[str] | None, Field(alias="REMARKS_PERSON")] = None
    person_occupation: Annotated[list[str] | None, Field(alias="OCCUPATION")] = None
    person_role_code: Annotated[list[str], Field(alias="ACTROLE_CODE")]
    person_age: Annotated[list[str] | None, Field(alias="AGE")] = None

    @property
    def act(self) -> AnalysesAct:
        """Return a simplified representation of this act (no people)."""

        return AnalysesAct(
            act_id=self.act_id,
            act_number = _clean(self.act_number),
            project = self.project,
            actplace = _clean(self.actplace),
            parish = _clean(self.parish),
            editorial_form = self.editorial_form,
            description = _clean(self.description),
            act_date = _clean(self.act_date),
            remarks = _clean(self.remarks),
            persons = self.persons,
        )
    
    @cached_property
    def persons(self) -> list[AnalysesPerson]:
        """Return a list of persons that are mentioned in the document."""

        return [
            AnalysesPerson(
                name = name,
                title= _clean(self.person_title[i]) if self.person_title else None,
                role = AnalysesActRole.from_code(self.person_role_code[i]),
                birth_date = _clean(self.person_birth_date[i]) if self.person_birth_date else None,
                birth_place = _clean(self.person_birth_place[i]) if self.person_birth_place else None,
                death_date = _clean(self.person_death_date[i]) if self.person_death_date else None,
                death_place = _clean(self.person_death_place[i]) if self.person_death_place else None,
                age = _clean(self.person_age[i]) if self.person_age else None,
                civil_status = _clean(self.person_civil_status[i]) if self.person_civil_status else None,
                residence_location = _clean(self.person_residence_location[i]) if self.person_residence_location else None,  # noqa: E501
                occupation =  _clean(self.person_occupation[i]) if self.person_occupation else None,
                remarks = _clean(self.person_remarks[i]) if self.person_remarks else None,
            )
            for i, name in enumerate(self.person_name)
        ]


class AnalysesFreeSearchRequest(BaseModel):
    """A request to perform a free search in the analyses of records.

    Attributes:
        search_terms (str | None): Keyword(s) to define the search: e.g. person, building, object, place, etc.
            Example:
                The results of a search for the word “brasseur” (brewer) will include records mentioning a person named
                “Brasseur”, records mentioning someone practising the profession of brewer, and notarial deeds in which
                the word “brasseur” is mentioned in the description and/or remarks.
            Note:
                Inverted commas may be used for exact searches. The search engine will then display the keywords in the
                same order as indicated in the search field.

                Example:
                    - Without inverted commas = vente moulin (sale mill) > the search engine looks for the
                        occurrence of the words “vente” and “moulin” regardless of the order or presence of 
                        these keywords together.
                    - With inverted commas = “Vente moulin” > the engine searches only scans for those occurrences 
                        of the terms in which the keywords Vente moulin are written together and in the same order.
            Note:
                You can use asterisk (*) and a question mark (?) to search for names that match one or more characters
                at the beginning or at the end of a search term (*) or for which a letter is not known (?).
                
                Example:
                    - *Mart* will match Demarteau, Jacquemart, Martin or Martens.
                    - De ?oninck for De Coninck or De Koninck.
        location (str | None): In most cases, the municipality where the document was created or a municipality 
            linked to a person (e.g. place of birth or death).

            Note:
                It is possible that a volunteer has made a spelling error (e.g. Arhcennes instead of Archennes), 
                that the old spelling of a place name was used (e.g. Messency instead of Messancy) 
                or that a place name has been translated (e.g. Graafschap Namen instead of Comté de Namur).
                The list of results may contain analyses of records drawn up in the place searched for 
                (visible the 'actplace' field of the document responses) 
                or analyses of records in which the place searched for is mentioned as the place of birth of a deceased 
                person or in remarks on the sale of an estate in this place.
        period (PeriodSelector): a specifier for the kind of period you wish to search 
            (exact date, between, before, after).
        start_date (str | None): Exact date of the record (format DD/MM/YYYY), start date (or year) of the 
            interval in which one or more records were created.
        end_date (str | None): End date (or year) of the interval in which one or more records were created.
        act_type (AnalysesActType | None): Written documents that record a change of status (baptism, marriage, burial,
            conscription, etc.) and have legal value (notarial act, judgment, etc.).
        project (AnalysesProject | None): List of projects executed by volunteers or staff of the State Archives.
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    search_terms: Annotated[str | None, Field(alias="SHORT_ALL_TEXTS")] = None
    location:     Annotated[str | None, Field(alias="ALL_PLACES")] = None
    period:       Annotated[PeriodSelector, Field(alias="CHOOSE_DATE_PERIODE")] = PeriodSelector.BETWEEN
    start_date:   Annotated[str | None, Field(alias="exactYear")] = None
    end_date:     Annotated[str | None, Field(alias="SHOW_PERIODE")] = None
    act_type:     Annotated[AnalysesActType | None, Field(alias="ACTTYPE")] = None
    project:      Annotated[AnalysesProject | None, Field(alias="PROJECT_ID")] = None


class SimplifiedAnalysesSearchResponse(BaseModel):
    """A free search response from the call to agatha.
    
    Attributes:
        nb_matches_total (int): the total number of identified matches. If len(docs) < nb_total_matches
            then it means that you did not receive all of the available results, but only the first few.
            This is likely to mean that you need to refine your search in order to narrow the scope of 
            the matched documents.
        docs (list[AnalysesAct]): the description of the documents that were found.
    """

    nb_matches_total: int
    docs: list[AnalysesAct]


class AnalysesSearchResponse(BaseModel):
    """A raw search response from the call to agatha.
    
    Attributes:
        numFound (int): the number of results corresponding to the search request
        start (int): offset of the 1st document in the complete list of possible results
        docs (list[AnalysesSearchResponseDocument]): the list of actual documents that
            matched with the user's search request.
    """

    numFound: int
    start: int
    docs: list[AnalysesSearchResponseDocument]

    @cached_property
    def simplified(self) -> SimplifiedAnalysesSearchResponse:
        """Return a simplfied representation of this search response."""

        return SimplifiedAnalysesSearchResponse(
            nb_matches_total = self.numFound,
            docs = [ d.act for d in self.docs ]
        )

@tool(parse_docstring=True)
def free_search_in_analyses_of_records(req: AnalysesFreeSearchRequest) -> SimplifiedAnalysesSearchResponse:
    """This is the way to perform a general search in the analyses of records. 

    Note: 
        This correspond to using the "Free search" tab in the Analyses of records section of the AGATA website.
    
    The Analyses of records search engine is the result of decades of work by our numerous volunteers and thestaff 
    of the State Archives. Thousands of pages of archives have been systematically analysed to provide asuccinct 
    description of the document (content, date, place). In addition, the names of all the people mentionedin the 
    document were noted, and if possible other data such as place of residence, profession, date of birth,etc.

    Most of the information available via the search engine comes from genealogical documents, such as church registers 
    and civil status registers. But the search engine also allows access to analyses of notarial deeds,building permits,
    property records, militia registers, foreigners' files, etc.

    Args: 
        req (AnalysesFreeSearchRequest): request object comprising all the search criterion to perform a free search
            in the analyses of records

    Returns:
        SimplifiedAnalysesSearchResponse: a response comprising the total number of identified matches corresponding
            to the given search criteria as well as the (up to 20 first) records that have been found.
    
    Raises:
        requests.exceptions.RequestException: whenever something goes wrong with the search on agatha.
    """
    data = req.model_dump(by_alias=True, exclude_none=True)

    if req.location:
        location = Municipality.by_name(
            req.location, 
            ajax=AJAX_URL, 
            return_single_best_match=True
        )

        if location is not None:
            data["ALL_PLACES"] = location.value
    
    data["CHOOSE_DATE_PERIODE"] = req.period.code
    data["WHICH_TAB"] = "FREE"
    ##
    search  = requests.post(FORM_URL, data = data)
    cookies = dict(search.cookies)
    ## fetch results
    results = requests.post(AJAX_URL, 
                      data = {
                          "method": "getResults", 
                          "pageSize": 20, 
                          "pageNumber": 1,
                      },
                      cookies = cookies)

    return AnalysesSearchResponse(**(results.json()["response"])).simplified


class PersonCriterion(BaseModel):
    """The data used to find a given person during a search person request.
    
    Attributes:
        name (Optional[str]): Name of the person sought, which may be a compound name (with a hyphen) 
            or several names in a row.

            Use this search field to enter the last name of the person you are looking for. 
            It is also possible to search for compound names (e.g. Lemercier or Petit-Jean).
            It is also possible to use an asterisk (*) and a question mark (?) to search for names that 
            match one or more characters at the beginning or end of a search term (*) 
            or for which a letter is not known (?).

            Example:
                - *Mart* for Demarteau, Jacquemart, Martin or Martens.
                - De ?oninck for De Coninck or De Koninck.
                
            Important: Don't forget to search using alternative spellings!
                
                Examples: 
                    - Dupont or Dupond 
                    - Fontaine or Fonteine.
            Note:        
                In notarial deeds or war damages files, for example, institutions are often 
                mentioned as stakeholders. These institutions have been included in the database 
                in the name field and can therefore also be found using this search field.
                
                Example: 
                    Société belge de tissage or Fabrique d'église de Notre-Dame.
                    
            Note:
                If both the last name and first name are given, the search engine will search for the combination 
                of the two names and only those results will be shown in which both last and first name occur together
                in an analysis. If only the last name or first name is entered and the other field remains empty, 
                the search will be based onthe completed field only. 
                As a result, the number of results will be higher and therefore less relevant.
        first_name (Optional[str]): First name of the person sought, which may be hyphenated 
            or composed of several first names (e.g. Catherine or Jacques François).
            
            Note:
                It is also possible to use an asterisk (*) and a question mark (?) to search for names that 
                match one or more characters at the beginning or end of a search term (*) or for which a letter 
                is not known (?).
                
                Example:
                    - An* for Anne, Anthony or Anne Marie.
                    - So??ie for Sofie or Sophie.
                    
            Note:
                Please note that the search engine does not translate first names. 
                It may therefore be necessary to searchseparately for the French, Dutch or Latin version of a name.
                
                Example: 
                    For the first name Antoine, also search for Antoon or Antonius (Dutch and Latin translation 
                    respectively).
                
                And don't forget to search using other spellings!
                
                Examples: 
                    - Elisabeth or Elizabeth 
                    - Mark or Marc
                    
                Whenever both the last name and first name are given, the search engine will search for the combination 
                of the two names and only those results will be shown in which both last and first name occur together
                in an analysis. If only the last name or first name is entered and the other field remains empty, the 
                search will be based on the completed field only. 
                As a result, the number of results will be higher and therefore less relevant.
        profession (Optional[str]): Activity or function held by the person sought.

                Note:
                    It is possible that a volunteer madea spelling mistake (e.g. 'tapisier' instead of 'tapissier'), 
                    that the old spelling of a profession was used (e.g.'laboureur' instead of 'agriculteur') 
                    or that a profession was translated (e.g. 'Naaister' [NL] instead of'couturière' [FR]).
        role (AnalysesActRole): Each person named in the document is assigned a “role”.
            
            Example: 
                In a marriage certificate, the roles are 'groom' and 'bride'. 
                Depending on which details were recorded,the father and mother of the couple, witnesses, 
                legitimate children and/or a previous partner may also bespecified. 
                Which roles are mentioned depends on the type of record described. 
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    # note: a suffix _2, _3 etc... must be added to all the persons that are searched for in addtion to 
    #  the first person when creating the request data 
    name: Annotated[Optional[str], Field(alias="NAME")] = None
    first_name: Annotated[Optional[str], Field(alias="FIRST_NAME")] = None
    # note: if a match is found, I must also populate "JOB_ID" else I should leave it empty with value = -1
    profession: Annotated[Optional[str], Field(alias="JOB")] = None
    role: Annotated[Optional[AnalysesActRole], Field(alias="ROLE")] = None

class AnalysesSearchPersonRequest(BaseModel):
    """A request to perform search document mentioning some given persons.

    Attributes:
        persons (str | None): The list of persons you wish to find in the act you are searching for.
        location (str | None): In most cases, the municipality where the document was created or a municipality 
            linked to a person (e.g. place of birth or death).

            Note:
                It is possible that a volunteer has made a spelling error (e.g. Arhcennes instead of Archennes), 
                that the old spelling of a place name was used (e.g. Messency instead of Messancy) 
                or that a place name has been translated (e.g. Graafschap Namen instead of Comté de Namur).
                The list of results may contain analyses of records drawn up in the place searched for 
                (visible the 'actplace' field of the document responses) 
                or analyses of records in which the place searched for is mentioned as the place of birth of a deceased 
                person or in remarks on the sale of an estate in this place.
        period (PeriodSelector): a specifier for the kind of period you wish to search 
            (exact date, between, before, after).
        start_date (str | None): Exact date of the record (format DD/MM/YYYY), start date (or year) of the 
            interval in which one or more records were created.
        end_date (str | None): End date (or year) of the interval in which one or more records were created.
        act_type (AnalysesActType | None): Written documents that record a change of status (baptism, marriage, burial,
            conscription, etc.) and have legal value (notarial act, judgment, etc.).
        project (AnalysesProject | None): List of projects executed by volunteers or staff of the State Archives.
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    persons:      list[PersonCriterion]
    location:     Annotated[str | None, Field(alias="ALL_PLACES")] = None
    period:       Annotated[PeriodSelector, Field(alias="CHOOSE_DATE_PERIODE")] = PeriodSelector.BETWEEN
    start_date:   Annotated[str | None, Field(alias="exactYear")] = None
    end_date:     Annotated[str | None, Field(alias="SHOW_PERIODE")] = None
    act_type:     Annotated[AnalysesActType | None, Field(alias="ACTTYPE")] = None
    project:      Annotated[AnalysesProject | None, Field(alias="PROJECT_ID")] = None


def search_person_in_analyses_of_records(req: AnalysesSearchPersonRequest) -> None:
    """Find documents about a person using their last name and/or first name in the specific fields provided. 

    Note:
        This corresponds to using the 'Search a Person' tab from the analyses of records section on Agatha.
    
    The database already contains 42 million names and is continuously enriched! So it may feel as if you we 're looking
    for a needle in a haystack! To find the person you are looking for, we recommend using 
    search_person_in_analyses_of_records. This search is recommended for finding a person using their last name 
    and/or first name in the specific fields provided. 
    
    The more precise the search criteria, the more relevant the results! 
    BUT... The more search criteria you use,the less likely you are to get results!

    Args: 
        req (AnalysesFreeSearchRequest): request object comprising all the search criterion to perform a free search
            in the analyses of records

    Returns:
        SimplifiedAnalysesSearchResponse: a response comprising the total number of identified matches corresponding
            to the given search criteria as well as the (up to 20 first) records that have been found.
    
    Raises:
        requests.exceptions.RequestException: whenever something goes wrong with the search on agatha.
    """

    # TODO
    ...





