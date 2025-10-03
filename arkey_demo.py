"""An Arkey demo done with streamlit."""

import streamlit as st

from agents.local_llm.agatha.graph import ASK_AGATHA

# continue from here: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/chat-response-feedback

avatar = "./avatar.png"


def main():
    #### THIS IS WHERE UI starts
    st.set_page_config(page_title="Ask Agatha", page_icon=avatar)
    
    st.image(avatar, width=100)
    st.title("Ask Agatha")
    st.write(":green[--]")
    
    messages = st.container()
    convers  = st.session_state.get("messages", [])
    if prompt := st.chat_input("Le bon roi dagobert avait-il sa culotte à l'envers ?"):
        for msg in convers:
            print(msg.type)
            if msg.type == "system":
                continue
            elif msg.type in ["assistant", "ai"]:
                messages.chat_message("assistant", avatar=avatar).write(msg.content)
            else:
                messages.chat_message(msg.type).write(msg.content)
        
        messages.chat_message("human").write(prompt)

        with messages.status("Working on your case") as status:
            try:
                state = None
                for update in ASK_AGATHA.stream({"input": prompt, "messages": convers}, stream_mode="values"):
                    if objective := update.get("thought"):
                        status.update(label=objective)
                    if context := update.get("scratch"):
                        with st.empty():
                            st.write(context)
                    state = update
                status.update(state="complete")
                # 
                convers = state["messages"]
                st.session_state["messages"] = convers
                messages.chat_message("assistant", avatar=avatar).write(convers[-1].content)
            except Exception as e:
                status.update(state="error", label="Oops... something went wrong")
                st.write(f":red[{repr(e)}]")


if __name__ == "__main__":
    main()