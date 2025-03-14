from google import genai
from google.genai.types import Content, Part, ContentListUnion
from typing import Optional, Union
from pydantic import Field
from agent.response_formatter import ResponseFormatter
from vecdb_modules.vecdbv2 import VecdbChatRAG
from repo_cloner import RepoCloner


class UserContent(Content):
    """Contains the multi-part content of a user message."""

    role: Optional[str] = Field(
        default="user",
        description="The producer of the content. Fixed as 'user' for user messages."
    )  # type: ignore

    def __init__(self, text: Union[str, list[str]], **kwargs):
        # Handle both single string and list of strings
        if isinstance(text, str):
            parts = [Part(text=text)]
        elif isinstance(text, list):
            parts = [Part(text=t) for t in text]
        else:
            raise ValueError("text must be either a string or list of strings")

        super().__init__(parts=parts, **kwargs)


class DocAgent:
    def __init__(
        self,
        repo_name: str,
        api_key: str = 'gemini_aki_key',
        model_name: str = 'gemini-2.0-flash-001',
    ):

        self.repo_name = repo_name

        self.client = genai.Client(api_key=api_key)
        self.model = self.client.models.generate_content

        self.vecdb = VecdbChatRAG(
            repo_name=repo_name
        )
        self.vecdb.load_vecdb()

        self.contents = []

        self.create_system_prompt()

        self.all_model_config = dict(
            model=model_name,
            config={
                'response_mime_type': 'application/json',
                'response_schema': ResponseFormatter,
                "system_instruction": self.sys_prompt,
                "temperature": 0
            })

    def create_system_prompt(self):

        with open('agent/sys_prompt2.md', 'r') as f:
            self.sys_prompt = f.read()

        repo = RepoCloner.get_repo_info(
            self.repo_name
        )
        repo_structure = repo['repo_structure']

        self.sys_prompt = self.sys_prompt.format(repo_structure=repo_structure)

    def generate_response(self, text: str) -> ResponseFormatter:

        self.contents.append(UserContent(text=text))  # type: ignore

        return self.invoke()

    def invoke(self) -> ResponseFormatter:

        response = self.model(
            contents=self.contents,
            **self.all_model_config  # type: ignore
        )

        self.contents.append(response)

        return response.parsed  # type: ignore

    def rag_on(self, user_search_query: str):

        rag_results_context = self.vecdb.query(
            text=user_search_query
        )

        self.contents.append(
            Part(text=rag_results_context)
        )
        return rag_results_context, self.invoke()

    def get_chat_hist(self):
        return self.contents

    def clear_chat_hist(self):
        self.contents = []
