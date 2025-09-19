"""An example to validate the behavior of the agent."""

from dotenv import load_dotenv

load_dotenv()

import asyncio  # noqa: E402

from langchain.agents import AgentExecutor, create_react_agent  # noqa: E402
from langchain_core.prompts import PromptTemplate  # noqa: E402

from agents.local_llm.agatha.graph import ask_agatha, find_act_details, find_digitized_document  # noqa: E402
from agents.local_llm.common.llm import LLM  # noqa: E402

system = PromptTemplate.from_template("""
        Your name is Arkey. You are an expert AI customer support at the 
        belgian state archive. You are known for being factual, and always 
        providing reliable information. Whenever you doubt, about a statement
        you wish to make (e.g. if you haven't had the opportunity to verify the
        data yourself), you prefer to be transparent about it rather than
        risking to give erroneous information.

        To complete your task, you can use the following tools: 
        {tools}
                           
        
        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Begin!

        Question: {input}
        Thought:{agent_scratchpad}
    """)

TOOLS = [find_act_details, find_digitized_document]
AGATHA_ = create_react_agent(
    LLM,
    tools=TOOLS,
    prompt=system,
)
AGATHA = AgentExecutor(
    name="Arkey",
    agent=AGATHA_,
    tools=TOOLS,
)

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
        le peintre pierre paul rubens était témoin. Dans l'idéal 
        j'aimerais pouvoir mettre la main sur une copie numérique de ce document.
        Pouvez vous m'aider ? S'il n'y a pas moyen, pourriez vous au moins me dire 
        de qui c'était le marriage et quel lien il y avait entre ces personnes et le peintre ?

        Merci d'avance, 
        Malik
        """
    
    response = await AGATHA.ainvoke({"input": email})

    print(response["output"])
    return response


if __name__ == "__main__":
    asyncio.run(example_rubens())