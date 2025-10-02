"""An Arkey demo done with streamlit."""

import streamlit as st

from agents.local_llm.agatha.graph import ASK_AGATHA

# continue from here: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/chat-response-feedback

avatar = "./avatar.png"

def main():
    #### THIS IS WHERE UI starts
    st.header("Ask Agatha", divider="green")

    messages = st.container()
    if prompt := st.chat_input("Le bon roi dagobert avait-il sa culotte à l'envers ?"):
        messages.chat_message("human").write(prompt)

        with messages.status("Working on your case") as status:
            try:
                state = None
                for update in ASK_AGATHA.stream({"input": prompt}, stream_mode="values"):
                    if objective := update.get("thought"):
                        status.update(label=objective)
                    
                    state = update
                status.update(state="complete")
                messages.chat_message("assistant", avatar=avatar).write(state["messages"][-1].content)
            except Exception:
                status.update(state="error")

if __name__ == "__main__":
    main()