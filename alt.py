"""An example to validate the behavior of the agent."""

from dotenv import load_dotenv

load_dotenv()

import asyncio  # noqa: E402

from agents.local_llm.agatha.graph import ASK_AGATHA  # noqa: E402


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
    
        Je sais que vous avez dans vos collections un acte de mariage dans lequel
        le peintre pierre paul rubens (ayant vécu à la fin du XIXe siècle) était témoin. Dans l'idéal 
        j'aimerais pouvoir mettre la main sur une copie numérique de ce document.
        Pouvez vous m'aider ? S'il n'y a pas moyen, pourriez vous au moins me dire 
        de qui c'était le marriage et quel lien il y avait entre ces personnes et le peintre ?

        Merci d'avance, 
        Malik
        """
    
    response = await ASK_AGATHA.ainvoke({"input": email}) # type: ignore
    messages = response["messages"][-1]
    print(messages.content)
    return ""


if __name__ == "__main__":
    asyncio.run(example_rubens())