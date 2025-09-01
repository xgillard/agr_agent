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
    Please note that humans rarely live longer than 100 years.
    Make sure to formulate your final answer in the same language as the user's original email. 
""")

def main():
    #response = (help_usr | customer_support).invoke(
    #    """
    #    MAIL FROM: anne.trucmachin@gmail.com
    #    RCPT TO: contact@arch.be
    #    SUBJECT: Certificat de bapteme 
    # 
    #    Je voudrais retrouver le certificat de bapteme de mon fils jean-philippe
    #    qui a été baptisé a warneton.
    # 
    #    Merci d'avance,
    #    Anne
    #    """,
    #)
    response = (help_usr | customer_support).invoke(
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
    )
    ##### ALT #################################
    #response = (help_usr | customer_support).invoke(
    #    """
    #    MAIL FROM: anne.trucmachin@gmail.com
    #    RCPT TO: contact@arch.be
    #    SUBJECT: Votre site est tout pourri ya rien qui marche
    #
    #    Ca fait 46 ans que je fais de la recherche généalogique et je n'ai jamais eu a faire a un site
    #    aussi pourri que le votre. On me demande toujours de me connecter et lorsque je le fais, 
    #    meme en utilisant mon login et mot de passe corrects, ca en marche pas. 
    #    Votre truc me rend completement zinin !
    #
    #    Merci d'avance,
    #    Anne
    #    """,
    #)
    #response = (help_usr | customer_support).invoke(
    #    """
    #    MAIL FROM: malik.alkadem@gmail.com
    #    RCPT TO: contact@arch.be
    #    SUBJECT: Je ne m'en sors pas 
    #
    #    Je coudry ressouar la pension de mon bou papa qu'il es né a algerie
    #    et mort a cause de la guerre de france. JE faire quoi ?
    #
    #    Des coeur sur vous,
    #    malik
    #    """,
    #)
    response = response["messages"][-1].content.split("[__FINAL_ANSWER__]")[-1]
    print("##" * 80)
    print(response)


if __name__ == "__main__":
    main()
