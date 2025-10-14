"""An example to validate the behavior of the agent."""

import asyncio

from agents.local_llm.agatha.graph import ask_agatha_graph

ASK_AGATHA = ask_agatha_graph()


async def example_rubens()-> str:
    """Renvoie le résultat d'un exemple dans lequel l'utilisateur cherche à trouver le scan d'un acte.

    L'utilisateur veut trouver un acte de mariage dans lequel le célèbre peintre pierre paul rubens
    était témoin. Il faut commencer par chercher dans les analyses d'acte sur base des personnes
    puis retrouver le scan (ou essayer du moins) en faisant une recherche dans les sources généalogiques.

    Returns:
        str: Le résultat d'un appel à l'agent en utilisant un faux email d'exemple à des fins de test.
    """

    email = """
        MAIL FROM: malik.alkadem@gmail.com
        RCPT TO: contact@arch.be
        SUBJECT: Je ne m'en sors pas 
    
        Pourriez vous me donner le lien vers un scan de l'acte de mariage lors duquel
        Pierre Paul Rubens était témoin. Le Pierre Paul Rubens que je cherche était 
        aussi peintre, mais il ne s'agit pas du célèbre primitif flamand. Il s'agit
        d'un homonyme ayant vécu à la fin du XIXs.

        Merci d'avance, 
        Malik
        """
    
    rsp = None
    async for msg in ASK_AGATHA.astream({"input": email}, stream_mode="updates"): # type: ignore
        rsp = msg
        if 'Observation' in msg:
            print("**" * 60)
            print(msg["Observation"]["scratch"])
            print("**" * 60)

    print("$$" * 60)
    print(rsp["Respond"]["messages"].content) # type: ignore
    print("$$" * 60)
    return ""


if __name__ == "__main__":
    asyncio.run(example_rubens())