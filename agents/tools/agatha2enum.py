"""This script generates the code for some enumerated types from the agatha html code.

Date: 2025-09-02
Author: X. Gillard
"""

import re
import unicodedata
from dataclasses import dataclass
from textwrap import dedent, indent

import bs4
import requests

# The pattern i use to process html select options
PATTERN = re.compile('<option value="(?P<value>[^"]+)">(?P<name>[^<]+)</option>')

# The format i use to output a valid enumeration class
FORMAT  = """
class {enum_name}(StrEnum):
    \"\"\"{descr}.

    Note:
        This class has been auto-generated from the html data from
        the AGATHA website.

    Attributes:
        {attrs_doc}
    \"\"\" # noqa: E501

    {members}

    @property
    def code(self) -> str:
        \"\"\"The code that is being used to represent this enum by the AGATHA api.
        
        Returns:
            str: the code that is used by the underlying AGATHA API.
        \"\"\"

        match self:{code_cases}
    
    @staticmethod
    def from_code(code: str) -> "{enum_name}":
        \"\"\"Converts the code internally used by AGATHA to represent this value.

        This method is basically the inverse of what the code property yields.

        Args:
            code (str): The code used by the AGATHA api to represent this value.
        
        Returns:
            {enum_name}: the enum value corresponding to the AGATHA code.
        
        Raises:
            ValueError: when the given code has no known correspondence.
        \"\"\"

        match code:{from_cases}
            case _:
                raise ValueError(f"Code '{{code}}' has no known correspondance in {enum_name}")
        
    @classmethod    
    def all_values(cls) -> list[str]:
      \"\"\"Return all the authorized values for this enum.
      
      Returns:
        list[str]: all the authorized values for this enum.
      \"\"\"
      return [ v._value_ for v in cls.__members__.values() ]
    
    @classmethod
    def all_codes(cls) -> list[str]:
      \"\"\"Return all the authorized codes for this enum.
      
      Returns:
        list[str]: all the authorized codes for this enum.
      \"\"\"
      return [ v.code for v in cls.__members__.values() ]

"""

CASE_FORMAT = """case {name}.{k}: 
    return "{v[1]}" """

FROM_CASE_FORMAT = """case "{v[1]}": 
    return {name}.{k}"""

@dataclass
class Target:
    """An enum generation target (that is, the description of an enum to be generated)

    Attributes:
        id (str): the identifier of the select html element
        name (str): the name of the newly generated enum class
        descr (str): the description of the newly generated class.
        label_as_name (str): should the label be converted to an enum name, or should the code be used instead.
    """

    id: str
    name: str
    descr: str
    label_as_name: bool = True


def enum_name(x: str) -> str:
    """Turn a string into an attribute name that can be used in an enum.
    
    Args:
        x (str): the string we want to turn into an enumeration.

    Returns: 
        str: A string that corresponds to 'x' but has been reformated so that
            it can be the name of an entry in an enumerated type.
        
    Example:
        >>> enum_name("coucou ca va")
        'COUCOU_CA_VA'
    """

    x = x.strip()
    x = x.replace("'s", "")
    x = x.replace("'", "")
    x = x.replace("(", "")
    x = x.replace(")", "")
    x = x.replace("-", "_")
    x = x.replace("/", "or")
    x = re.sub(r"\s+", "_", x)
    return x.upper()

def html_to_enum(target: Target, html: str) -> str:
    """Create an enumeration class based on the html code from AGATHA.

    Args: 
        name (str): the name we want to use for our enumeration.
        descr (str): the description we wish to use for the role of our enumeration.
        html (str): the html code coming from AGATGA.

    Returns: 
        str: a string comprising the code for an enumeration matching the descriptions
            given in the agatha html code
    """

    data = {}
    for match in PATTERN.finditer(html):
        groups = match.groupdict()
        val = unicodedata.normalize("NFC", groups["value"])
        nam = unicodedata.normalize("NFC", groups["name"])

        data[enum_name(nam if target.label_as_name else val)] = (nam, val)

    attrs_doc = "\n        ".join(
        f"{k} (str): {v[0]}" for k,v in data.items()
    )

    members = "\n    ".join( f"{k} = \"{v[0] if target.label_as_name else v[1]}\"" for k,v in data.items() )

    code_cases = "\n" + indent(
        "\n".join(
            CASE_FORMAT.format(name=target.name, k=k, v=v)
            for k,v in data.items()
        ),
        "            "
    )
    from_cases = "\n" + indent(
        "\n".join(
            FROM_CASE_FORMAT.format(name=target.name, k=k, v=v)
            for k,v in data.items()
        ),
        "            "
    )
    return FORMAT.format(
        enum_name=target.name, 
        descr=indent(target.descr, "    ").strip(),
        attrs_doc=attrs_doc,
        members=members,
        code_cases=code_cases,
        from_cases=from_cases
        )


def enumerations_from_agatha(url: str, targets: list[Target]) -> list[str]:
    """Create a list of enumeration types directly from the agatha source code.

    Args:
        url (str): the url of the page wher this enum can be found.

    """

    document = bs4.BeautifulSoup(requests.get(url).text, "html.parser")
    results = []
    for target in targets:
        found = document.find("select", attrs={"id": target.id})
        clazz = html_to_enum(
            target = target,
            html=str(found),
        )
        results.append(clazz)
    return results

if __name__ == "__main__":
    with open("./agents/tools/generated.py", "w", encoding="utf8") as f:
        print("\"\"\"Autogenerated datatypes to interact with AGATHA.", file=f)
        print(file=f)
        print("Author: `uv run tools/agatha2enum.py`", file=f)
        print("\"\"\"", file=f)
        print(file=f)
        print("from enum import StrEnum", file=f)
        print(file=f)

        analyses = enumerations_from_agatha(
            "https://agatha.arch.be/search/analyses/",
            [
                Target(
                    id = "ACTTYPE_FREE",
                    name = "AnalysesActType",
                    descr= dedent("""
                        Written documents that record a change of status (baptism, marriage, burial, conscription, etc.)
                        and have legal value (notarial act, judgment, etc.).
                        """),
                ),
                Target(
                    id = "PROJECT_FREE",
                    name = "AnalysesProject",
                    descr= "List of projects executed by volunteers or staff of the State Archives.",
                    label_as_name=False,
                ),
                Target(
                    id    = "ROLE",
                    name  = "AnalysesActRole",
                    descr = "The role somebody played in the context of an official act.",
                    label_as_name=True,
                ),
            ]
        )

        generated = "\n\n".join(analyses)
        print(generated, file=f)

