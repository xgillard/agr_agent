"""An Arkey demo done with streamlit."""

import asyncio

import streamlit as st

from agents.local_llm.agatha.graph import ask_agatha_graph

# continue from here: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/chat-response-feedback

avatar = "./avatar.png"

ASK_AGATHA = ask_agatha_graph()

@st.fragment
def render_page_header():
    """Render the page header with title and all generic info."""
    
    st.set_page_config(page_title="Ask Agatha", page_icon=avatar)
    st.image(avatar, width=100)
    st.title("Ask Agatha")
    st.divider()

@st.fragment
def render_conversation(parent):
    """Render the user's conversation with AI bot."""

    convers = st.session_state.get("messages", [])
    for msg in convers:
        if msg.type == "system":
            continue
        elif msg.type in ["assistant", "ai"]:
            parent.chat_message("assistant", avatar=avatar).write(msg.content)
        else:
            parent.chat_message(msg.type).write(msg.content)

def async_run(coro):
    """Evite le probleme: event loop is closed."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Exécute la coroutine jusqu'à ce qu'elle soit terminée
    return loop.run_until_complete(coro)

async def for_each_update(status, stream):
    state = None
    async for update in stream:
        if objective := update.get("thought"):
            status.update(label=objective)
        else:
            status.update(label="Thinking")
        if context := update.get("scratch"):
            st.write(context)
        state = update
    return state

def render_status(parent, stream) -> str:
    """Render the 'thinking' status bar.
    
    Args:
        stream: streaming iterator for the events occuring during the thinking process.
    """

    with parent.status("Working on your case") as status:
        with st.empty():
            try:
                state = async_run(for_each_update(status, stream))
                status.update(state="complete")
                # 
                st.session_state["messages"] = state["messages"]
                st.session_state["scratch"] = state["scratch"]
                return state["messages"][-1].content
            except Exception as e:
                status.update(state="error", label="Oops... something went wrong")
                st.write(f":red[{repr(e)}]")
                return "Oops... an error has happened. Sorry"

def main():
    #### THIS IS WHERE UI starts
    render_page_header()
    
    messages = st.container()
    render_conversation(messages)
    
    if prompt := st.chat_input("Le bon roi dagobert avait-il sa culotte à l'envers ?"):
        request = ASK_AGATHA.astream({
                "input": prompt, 
                "messages": st.session_state.get("messages", []), 
                "scratch": st.session_state.get("scratch", "")
            },
            stream_mode="values"
        )
        
        messages.chat_message("user").write(prompt)   
        response = render_status(messages, request)
        messages.chat_message("assistant", avatar=avatar).write(response)

if __name__ == "__main__":
    main()