import streamlit as st
from repo_cloner import RepoCloner
from vecdb_modules.vecdbv2 import VecDB
from agent.doc_agent import DocAgent


with st.container(border=True):

    st.title("Hi, Choose or Clone Github Repo")
    st.subheader("Clone/Pull Github Repo")

    label_btn_cols = st.columns([3, 1], vertical_alignment='bottom')

    repo_url = label_btn_cols[0].text_input("Repo URL")

    if label_btn_cols[1].button("Clone Repo", use_container_width=True, type='primary'):

        if repo_url:
            try:
                with st.spinner("Cloning the Repo...", show_time=True):

                    cohere_api_key = st.session_state.get("coher_api_key")
                    if cohere_api_key is None:
                        st.warning("You Should Set Coher API key.")
                        st.stop()

                    RepoCloner(repo_url)

                    st.session_state.repo_name_str = RepoCloner.extract_repo_name(
                        repo_url=repo_url)
                    st.success("Repo Cloned Successfully.")

                with st.spinner("Vectoring the Repo...", show_time=True):

                    cohere_api_key = st.session_state.get("coher_api_key")
                    if cohere_api_key is None:
                        st.warning("You Should Set Coher API key.")
                        st.stop()

                    vecdb = VecDB(
                        st.session_state.repo_name_str,
                        cohere_api_key=cohere_api_key)

                    vecdb.vectorize_db()

                st.success("Repo Vectorized Successfully.")

            except Exception as e:
                st.error(
                    f"Can't Cloning this Repo URL: Because this error {e}")

    all_repos_infos = RepoCloner.get_all_repos_info()

    st.subheader("Local Repos")
    repo_name = st.session_state.get('repo_name_str', None)
    index = 0
    if repo_name:
        index = list(all_repos_infos.keys()).index(repo_name)

    repo_name = st.selectbox(
        label="Select Repo Name",
        options=all_repos_infos.keys(),
        index=index,
    )

    st.session_state.repo_name_str = None

    if repo_name:
        st.subheader("Repo Info:")
        st.markdown(
            f"""
            **Repo URL:** {all_repos_infos[repo_name]['repo_url']}\n
            **Repo Local Path:** ```{all_repos_infos[repo_name]['repo_path']}```\n
            **Commit Hash:** ```{all_repos_infos[repo_name]['commit_hash']}```\n
            **Last Updated:** ```{all_repos_infos[repo_name]['last_updated']}```\n
            """
        )
        with st.expander("**Repo Structure:**"):
            st.code(all_repos_infos[repo_name]['repo_structure'])

    btns_cols = st.columns([1, 1, 1, 1])

    if btns_cols[0].button(
        label="Remove Repo",
        use_container_width=True,
        disabled=not bool(repo_name),
    ):
        @st.dialog("Removing Repo")
        def ensure_remove_repo():
            st.write(f"Are you Sure to remove this Repo: `{repo_name}`?")
            if st.columns([1, 1, 1])[2].button("Remove", use_container_width=True, type='primary'):
                RepoCloner.remove_repo(repo_name)  # type: ignore
                st.rerun()

        ensure_remove_repo()

    if btns_cols[2].button(
        "Pull Repo",
        use_container_width=True,
        disabled=not bool(repo_name)
    ):

        try:
            with st.spinner("Pulling the Repo...", show_time=True):
                RepoCloner(
                    all_repos_infos[repo_name]['repo_url']
                )
            st.success("Repo Pulled Successfully.")

            with st.spinner("Re-Vectoring the Repo...", show_time=True):

                cohere_api_key = st.session_state.get("coher_api_key")
                if cohere_api_key is None:
                    st.warning("You Should Set Coher API key.")
                    st.stop()

                vecdb = VecDB(repo_name, cohere_api_key=cohere_api_key)
                vecdb.vectorize_db()

                st.success("Repo Re-Vectorized Successfully.")

        except Exception as e:
            st.error(
                f"Can't Pull the Repo or Re-Vectorizes because of this error: {e}")

    if btns_cols[3].button(
            "Choose Repo",
            use_container_width=True,
        type='primary',
        disabled=not bool(repo_name)
    ):

        with st.spinner("Loading Repo from Disk...", show_time=True):

            gemini_api_key = st.session_state.get('gemini_api_key')

            if gemini_api_key is None:
                st.error("You Should Set Gemini API key First.")
                st.stop()

            else:
                st.session_state.agent = DocAgent(
                    repo_name=repo_name,
                    api_key=gemini_api_key
                )

        if gemini_api_key:
            st.success("Setting The Repo Doc Successfully.")
