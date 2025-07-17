from dotenv import load_dotenv

load_dotenv()

from agents.customer_support import customer_support
from agents.common import task
from langchain_core.output_parsers import StrOutputParser


help_usr = task("""
    Answer to the following user email with factual information.
    Be kind, use professional tone. 
    Make sure to formulate your final answer in the same language as the user's original email. 
""")

def main():
    response = (help_usr | customer_support).invoke(
        """
        MAIL FROM: anne.trucmachin@gmail.com
        RCPT TO: contact@arch.be
        SUBJECT: Je ne m'en sors pas 

        Bonjour, je n'arrive plus à faire de recherches sur le site des AGR. J'obtiens le message 
        "Ce compte n'a pas encore été activé. Veuillez cliquer sur le lien d'activatione envoyé par mail." 
        mais je n'ai pas reçu ce mail! Ce blocage est récent (depuis le passage à AGATHA). 
        On a changé le mot de passe mais le blocage persiste.
        Merci de faire le nécessaire.
        Bien à vous,
        Anne Hainaux
        """,
    )
    response = response["messages"][-1].content.split("[__FINAL_ANSWER__]")[1]
    print("##" * 80)
    print(response)


if __name__ == "__main__":
    main()
