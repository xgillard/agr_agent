"""An example to validate the behavior of the agent."""

from dotenv import load_dotenv

load_dotenv()

import asyncio  # noqa: E402

from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402

from agents.local_llm.analyses_of_records import SEARCH_IN_ANALYSES_OF_RECORDS  # noqa: E402
from agents.local_llm.common.llm import LLM  # noqa: E402
from agents.local_llm.genealogical_sources.graph import SEARCH_IN_GENEALOGIC_SOURCES  # noqa: E402


async def example_rubens()-> str:
    """Renvoie le résultat d'un exemple dans lequel l'utilisateur cherche à trouver le scan d'un acte.

    L'utilisateur veut trouver un acte de mariage dans lequel le célèbre peintre pierre paul rubens
    était témoin. Il faut commencer par chercher dans les analyses d'acte sur base des personnes
    puis retrouver le scan (ou essayer du moins) en faisant une recherche dans les sources généalogiques.

    Returns:
        str: Le résultat d'un appel à l'agent en utilisant un faux email d'exemple à des fins de test.
    """

    sytem = SystemMessage("""
        Your name is Arkey. You are an expert AI customer support at the 
        belgian state archive. You are known for being factual, and always 
        providing reliable information. Whenever you doubt, about a statement
        you wish to make (e.g. if you haven't had the opportunity to verify the
        data yourself), you prefer to be transparent about it rather than
        risking to give erroneous information.
        """)
    email = HumanMessage("""
        MAIL FROM: malik.alkadem@gmail.com
        RCPT TO: contact@arch.be
        SUBJECT: Je ne m'en sors pas 
    
        Je sais que vous avez dans vos collections un acte de mariage dans lequel
        le peintre pierre paul rubens était témoin. Dans l'idéal 
        j'aimerais pouvoir mettre la main sur une copie numérique de ce document.
        Pouvez vous m'aider ? S'il n'y a pas moyen, pourriez vous au moins me dire 
        de qui c'était le marriage et quel lien il y avait entre ces personnes et le peintre ?

        Merci d'avance, 
        Malik
        """)
    
    response = await SEARCH_IN_ANALYSES_OF_RECORDS.ainvoke({ # type: ignore
        "messages": [sytem, email]
    })

    print(">>>>" * 20)
    print(response["messages"][-1].content)
    print(">>>>" * 20)

    response2 = await SEARCH_IN_GENEALOGIC_SOURCES.ainvoke({ # type: ignore
        "messages": response["messages"] + [
            HumanMessage("""
            You have found a record that corresponds to the user's request.
            Now, you would like to find a find a digitized copy of that 
            record. For that purpose, you will try to find that document using 
            the search in genealogical sources capabilities from AGATHA as they
            are the one source capable of giving you a link to the scan of the
            original register where that act is stored.
            """),
        ]
    })

    print("<<<<<" * 20)
    print(response2["messages"][-1].content)
    print("<<<<<" * 20)

    user_facing = await (LLM | StrOutputParser()).ainvoke(
            response2["messages"] +
            [ HumanMessage("""
            < Instructions >
            Respond to the user request in his own language. 
            Be polite and professional. 
            </ Instructions >
            """)]
    )

    print(user_facing)
    return user_facing


if __name__ == "__main__":
    asyncio.run(example_rubens())