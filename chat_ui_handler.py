import streamlit as st
from time import sleep

from google.genai.types import Content, Part, GenerateContentResponse

from agent.response_formatter import ResponseFormatter, ContextSourceFormatter
from agent.doc_agent import DocAgent
from source_component import SourceCard


class ChatHandler:
    def __init__(self) -> None:

        self.agent: DocAgent = st.session_state.agent

        if self.agent is None:
            raise Exception("The Repo Name must be Not Be None")

        self.chat_hist = []
        self.src_card_render = SourceCard()

    def render_user_msg(self, msg: Content | str) -> None:

        if isinstance(msg, Content):
            msg = msg.parts[0].text  # type: ignore

        st.chat_message('user').markdown(msg)

    def render_sources(self, context_sources: list[ContextSourceFormatter]) -> None:

        st.subheader("Sources")

        cols = st.columns(4)

        for src_i, src in enumerate(context_sources):
            with cols[src_i % 4]:
                self.src_card_render.render(
                    src.model_dump()
                )

    def render_ai_msg(
            self,
            msg: ResponseFormatter,
            i: int | None = None
    ) -> int:

        if msg is None:
            st.write(self.agent.get_chat_hist())

        with st.chat_message("ai"):
            st.markdown(msg.ai_response)

            if msg.search_query and i:
                with st.expander("Search In Repo with..."):
                    st.write(msg.search_query)

                    rag_results = self.chat_hist[i+1].text
                    st.container(border=True).write(rag_results)

                msg = self.chat_hist[i+2].parsed
                st.markdown(msg.ai_response)

                i += 2

            if msg.context_sources:
                self.render_sources(msg.context_sources)

        return i or 0

    def render_chat(self) -> None:
        self.chat_hist = self.agent.get_chat_hist()
        chat_len = len(self.chat_hist)

        i = 0
        while i < chat_len:
            msg = self.chat_hist[i]

            if isinstance(msg, Content):
                self.render_user_msg(msg)

            elif isinstance(msg, GenerateContentResponse):
                i = self.render_ai_msg(msg.parsed, i)  # type: ignore

            i += 1

    def stream_markdown(self, text: str, delay: float = .001) -> None:

        plc = st.empty()
        rendered_text = ''
        for chr in text:
            rendered_text += chr
            plc.markdown(rendered_text, unsafe_allow_html=True)
            sleep(delay)

    def handle_prompt(self, prompt: str) -> None:

        self.render_user_msg(prompt)

        with st.chat_message('ai'):

            with st.spinner("Thinking...", show_time=True):
                response: ResponseFormatter = self.agent.generate_response(
                    prompt)

            self.stream_markdown(response.ai_response)

            if response.search_query:
                with st.expander("Search In Repo with...", expanded=True):

                    self.stream_markdown(response.search_query)

                    with st.spinner("Searching In VecDB", show_time=True):
                        rag_results, response = self.agent.rag_on(
                            response.search_query
                        )

                    with st.container(border=True):
                        self.stream_markdown(rag_results, delay=.00001)

                self.stream_markdown(response.ai_response)

            if response.context_sources:
                self.render_sources(response.context_sources)

    def track_hist(self) -> None:
        self.chat_hist = self.agent.get_chat_hist()

        cln_chat_hist = [

            self.agent.sys_prompt
        ]
        for msg in self.chat_hist:

            if isinstance(msg, Content):
                cln_chat_hist.append(
                    dict(
                        role='user',
                        content=msg.parts[0].text  # type: ignore
                    )
                )

            elif isinstance(msg, Part):
                cln_chat_hist.append(
                    dict(
                        role='rag',
                        content=msg.text
                    )  # type: ignore
                )

            elif isinstance(msg, GenerateContentResponse):
                cln_chat_hist.append(
                    dict(
                        role='ai',
                        content=msg.parsed.model_dump()  # type: ignore
                    )
                )

        st.sidebar.write(cln_chat_hist)
