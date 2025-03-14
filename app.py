import streamlit as st

st.set_page_config(
    page_title="Documentation Agent - Chat with Any Repo",
    page_icon=":sparkles:",
    layout="wide"
)


with st.sidebar.container(border=True):
    st.subheader("Set APIs Keys:")

    GEMINI_API_KEY = st.text_input(
        label="Gemini Api Key",
        type='password',
    )

    COHER_API_KEY = st.text_input(
        label="Coher Api Key",
        type='password',
    )

    if st.columns([1, 1, 1])[2].button(
        'Set',
        disabled=not (GEMINI_API_KEY and COHER_API_KEY),
        use_container_width=True,
        type='primary'
    ):
        st.session_state.gemini_api_key = GEMINI_API_KEY
        st.session_state.coher_api_key = COHER_API_KEY

        st.success("You Can now Chat")


pg = st.navigation(
    [
        st.Page("data_prep_app.py", title='Data Preparation',
                icon='🛠️'),
        st.Page("chat_app.py", title="Chat", icon='🤖'),
    ]
)


pg.run()
