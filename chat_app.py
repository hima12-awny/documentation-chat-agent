import streamlit as st
from chat_ui_handler import ChatHandler


st.title("Documentation Agent - Chat with Any Repo :robot_face:")
st.markdown(
    "Chat with our AI assistant to get information about your Github Repo.")

if 'agent' not in st.session_state:
    st.header("You Should Choose First Repo from Prepare Repo to Chat Based on it.")
    st.stop()


if st.sidebar.button(
    "Clear Messages",
):
    st.session_state.agent.clear_chat_hist()


st.session_state.ui_agent = ChatHandler()


st.session_state.ui_agent.render_chat()


if prompt := st.chat_input("Type your message here..."):

    st.session_state.ui_agent.handle_prompt(
        prompt=prompt
    )

# st.session_state.ui_agent.track_hist()
