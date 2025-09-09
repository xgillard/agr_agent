"""The purpose of this module is to provide some easy way to validate the current state of dev."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from agents.common import task  # noqa: E402
from agents.customer_support import customer_support  # noqa: E402

TODAY = datetime.today().strftime('%Y-%m-%d')

help_usr = task(f"""
    Date: {TODAY}

    Answer to the following user email with factual information.
    Be kind, use professional tone. 
    Make sure to formulate your final answer in the same language as the user's original email. 
""")

def exemple_bapteme() -> str:
    """Renvoie le résultat d'un exemple ou l'utilisateur demande un certificat de bapteme.
    
    Comme ce document concerne une personne encore vivante (ou du moins née après 1796), la
    réponse de l'agent devrait être que le cerificat de bapteme doit etre demandé aupres de
    la paroisse car il s'agit d'un document religieux qui n'a plus de valeur légale depuis
    1796.

    Returns:
        str: Le résultat d'un appel à l'agent en utilisant un faux email d'exemple à des fins de test.
    """

    response = (help_usr | customer_support).invoke({
        "input":
        """
        MAIL FROM: anne.trucmachin@gmail.com
        RCPT TO: contact@arch.be
        SUBJECT: Certificat de bapteme 
     
        Je voudrais retrouver le certificat de bapteme de mon fils jean-philippe
        qui a été baptisé a warneton.
     
        Merci d'avance,
        Anne
        """,
    })
    response = response["messages"][-1].content.split("[__FINAL_ANSWER__]")[-1]
    return response

def exemple_recherche() -> str:
    """Renvoie le résultat d'un exemple l'agent a tout pour faire la recherche.
    
    L'agent doit faire la recherche pour l'utilisateur et lui renvoyer un lien pertinent.

    Returns:
        str: Le résultat d'un appel à l'agent en utilisant un faux email d'exemple à des fins de test.
    """

    response = (help_usr | customer_support).invoke({
        "input":
        """
        MAIL FROM: anne.trucmachin@gmail.com
        RCPT TO: contact@arch.be
        SUBJECT: Je ne m'en sors pas 
     
        Je voudrais retrouver le certificat de décès de mon arrière arrière grand oncle qui est décédé
        à Sterrebeek en 1689 mais je n'ai vraiment aucune idée de la manière dont il faut que je m'y 
        prenne. Pourriez vous m'aider ?
     
        Merci d'avance,
        Anne
        """,
    })
    response = response["messages"][-1].content.split("[__FINAL_ANSWER__]")[-1]
    return response

def exemple_activation() -> str:
    """Renvoie le résultat d'un exemple dans lequel l'utilisateur se plaint d'avoir un compte inactif.
    
    L'agent doit alors activer le compte de l'utilisateur puis lui suggérer de réessayer de se connecter.

    Returns:
        str: Le résultat d'un appel à l'agent en utilisant un faux email d'exemple à des fins de test.
    """

    response = (help_usr | customer_support).invoke({
        "input":
        """
        MAIL FROM: anne.trucmachin@gmail.com
        RCPT TO: contact@arch.be
        SUBJECT: Votre site est tout pourri ya rien qui marche
    
        Ca fait 46 ans que je fais de la recherche généalogique et je n'ai jamais eu a faire a un site
        aussi pourri que le votre. On me demande toujours de me connecter et lorsque je le fais, 
        meme en utilisant mon login et mot de passe corrects, ca en marche pas. 
        Votre truc me rend completement zinin !
    
        Merci d'avance,
        Anne
        """,
    })
    response = response["messages"][-1].content.split("[__FINAL_ANSWER__]")[-1]
    return response

def exemple_redirect() -> str:
    """Renvoie le résultat d'un exemple dans lequel l'utilisateur pose une question non pertinente.
    
    L'agent doit alors poliment décliner la requête et (eventuellement) suggérer une idée de l'institution
    plus approprié à qui poser la question.

    Returns:
        str: Le résultat d'un appel à l'agent en utilisant un faux email d'exemple à des fins de test.
    """

    response = (help_usr | customer_support).invoke({
        "input":
        """
        MAIL FROM: malik.alkadem@gmail.com
        RCPT TO: contact@arch.be
        SUBJECT: Je ne m'en sors pas 
    
        Je coudry ressouar la pension de mon bou papa qu'il es né a algerie
        et mort a cause de la guerre de france. JE faire quoi ?
    
        Des coeur sur vous,
        malik
        """,
    })
    response = response["messages"][-1].content.split("[__FINAL_ANSWER__]")[-1]
    return response


def example_rubens()-> str:
    """Renvoie le résultat d'un exemple dans lequel l'utilisateur cherche à trouver le scan d'un acte.

    L'utilisateur veut trouver un acte de mariage dans lequel le célèbre peintre pierre paul rubens
    était témoin. Il faut commencer par chercher dans les analyses d'acte sur base des personnes
    puis retrouver le scan (ou essayer du moins) en faisant une recherche dans les sources généalogiques.

    Returns:
        str: Le résultat d'un appel à l'agent en utilisant un faux email d'exemple à des fins de test.
    """

    response = (help_usr | customer_support).invoke({
        "input":
        """
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
        """,
    })
    response = response["messages"][-1].content.split("[__FINAL_ANSWER__]")[-1]
    return response

def main():
    """Execute un ou plusieurs tests facilement."""
    print(example_rubens())
    print("#" * 80)
    #print(exemple_bapteme())
    #print("#" * 80)
    #print(exemple_redirect())
    #print("#" * 80)
    print(exemple_recherche())


if __name__ == "__main__":
    main()
