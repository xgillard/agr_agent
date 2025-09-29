"""An Arkey demo done with streamlit."""

import asyncio

import streamlit as st

from agents.local_llm.agatha.graph import ASK_AGATHA

# continue from here: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/chat-response-feedback

async def ask_agatha(content: str) -> str:
    state = await ASK_AGATHA.ainvoke({"input": content})
    return state.get("messages")[-1].content


async def main():
    #### THIS IS WHERE UI starts
    st.title("Arkey -- Demo")

    with st.form("my_form"):
        text = st.text_area(
            "Enter text:",
            "Le bon roi dagobert avait-il sa culotte à l'envers ?",
        )

        submitted = st.form_submit_button("Submit")
        if submitted:
            st.info(await ask_agatha(text))

if __name__ == "__main__":
    asyncio.run(main())