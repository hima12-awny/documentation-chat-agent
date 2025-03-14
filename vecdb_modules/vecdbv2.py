from typing import List
from llama_index.core import Document
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.indices.vector_store.retrievers import (
    VectorIndexRetriever,
)
from llama_index.core.schema import NodeWithScore
import nest_asyncio
from llama_index.core import SimpleDirectoryReader
import json
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
import os
from llama_index.embeddings.cohere import CohereEmbedding
from repo_cloner import RepoCloner
import streamlit as st


class VecDB:
    def __init__(
        self,
        repo_name: str | None = None,
        persist_directory="vec_db",
        cohere_api_key: str = 'cohere_api_key'

    ) -> None:

        self.repo_name = repo_name
        self.cohere_api_key = cohere_api_key

        self.persist_directory = persist_directory

        self.retriever: None | VectorIndexRetriever = None

        self.index: VectorStoreIndex | None = None

    def split_docs(self, docs: list[Document]) -> list[Document]:

        splitted_docs: list[Document] = []
        for doc in docs:
            file_name = doc.metadata['file_name']
            file_ex = '.' + doc.metadata['file_name'].split('.')[-1]

            file_url = doc.metadata['file_url']
            last_updated = doc.metadata['last_updated']

            if file_ex == '.txt':
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1024, chunk_overlap=50)

            else:
                code_lang = self.supported_files_types_names[file_ex]
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language(code_lang),
                    chunk_size=1500, chunk_overlap=100
                )

            code_text = doc.text

            file_docs = splitter.create_documents([code_text])

            splitted_docs.extend(
                Document(
                    text=f'// file name: {file_name}\n{doc.page_content}',
                    metadata=dict(
                        source=file_name,
                        source_url=file_url,
                        source_last_updated=last_updated
                    )
                )
                for doc in file_docs
            )
        return splitted_docs

    def load_docs(self, repo_name) -> list[Document]:

        with open("settings/supported_files.json", 'r') as sf:
            self.supported_files_types = json.loads(sf.read())

        with open("settings/supported_files_names.json", 'r') as sf:
            self.supported_files_types_names = json.loads(sf.read())

        repo_path = os.path.join(".", "repos", repo_name)

        reader = SimpleDirectoryReader(
            input_dir=repo_path,
            recursive=True,
            required_exts=self.supported_files_types
        )

        docs = reader.load_data(num_workers=4)

        repo_info = RepoCloner.get_repo_info(repo_name=repo_name)
        repo_url = repo_info['repo_url']
        last_commit_hash = repo_info['commit_hash']
        last_updated = repo_info['last_updated']

        for i in range(len(docs)):
            doc = docs[i]

            doc_last_path = doc.metadata['file_path'].replace(
                '\\', '/').split(repo_name)[-1]

            doc.metadata['file_url'] = f'{repo_url}/blob/{last_commit_hash}{doc_last_path}'
            doc.metadata['last_updated'] = last_updated

            docs[i] = doc

        return docs

    def vectorize_db(
        self,
        repo_name: str | None = None,
    ) -> None:

        if self.repo_name is None and repo_name is None:
            raise Exception("Must Specify repo_name!")

        repo_name = repo_name or self.repo_name or ''

        documents = self.load_docs(repo_name)

        splitted_docs = self.split_docs(docs=documents)

        nest_asyncio.apply()

        embed_model = CohereEmbedding(
            cohere_api_key=self.cohere_api_key,
            input_type="search_document"
        )

        self.index = VectorStoreIndex.from_documents(
            documents=splitted_docs,
            embed_model=embed_model,
            insert_batch=100,
            use_async=True,
            show_progress=True,
        )

        persist_dir_name = os.path.join(
            ".",
            self.persist_directory,
            repo_name
        )

        self.index.storage_context.persist(
            persist_dir=persist_dir_name)

        print("VecDB Storing Done.")

    def load_vecdb(
        self,
        repo_name: str | None = None,
    ) -> None:

        if self.repo_name is None and repo_name is None:
            raise Exception("Must Specify repo_name!")

        from llama_index.postprocessor.cohere_rerank import CohereRerank

        repo_name = repo_name or self.repo_name or ''

        persist_dir_name = os.path.join(
            ".",
            self.persist_directory,
            repo_name
        )

        storage_context = StorageContext.from_defaults(
            persist_dir=persist_dir_name)

        embed_model = CohereEmbedding(
            cohere_api_key=self.cohere_api_key,
            input_type="search_query"
        )

        index = load_index_from_storage(
            storage_context=storage_context,
            embed_model=embed_model
        )  # type: ignore

        self.postprocessor = CohereRerank(
            top_n=2,
            model="rerank-english-v3.0",
            api_key=self.cohere_api_key
        )

        self.retriever = index.as_retriever(  # type: ignore
            similarity_top_k=15,
        )

        print("VecDB Loading Done.")

    def query(self, text: str) -> List[NodeWithScore]:
        if self.retriever is None:
            self.load_vecdb()

        nodes = self.retriever.retrieve(text)  # type: ignore
        nodes = self.postprocessor.postprocess_nodes(
            nodes=nodes,
            query_str=text
        )
        return nodes


class VecdbChatRAG(VecDB):
    def __init__(
            self,
            repo_name: str,
            persist_directory="./vec_db") -> None:

        cohere_api_key = st.session_state.get("coher_api_key")
        if cohere_api_key is None:
            st.warning("You Should Set Coher API key.")
            st.stop()

        else:
            super().__init__(
                repo_name=repo_name,
                persist_directory=persist_directory,
                cohere_api_key=cohere_api_key)

        self.retrieved_node_ids = set()

    def query(self, text: str):  # type: ignore

        nodes = super().query(text)

        i = 0
        ret_docs = ''
        for node in nodes:
            node_id = node.node.node_id

            if node_id in self.retrieved_node_ids:
                continue

            self.retrieved_node_ids.add(node_id)

            doc = dict(
                metadata=node.metadata,
                context=node.text
            )
            ret_docs += f'{(i:=i+1)}. {doc}\n'

        rag_str_result = f'Use This as Code Context that may answer the user Query: {text[:(min(len(text)-1, 100))]}...\n'

        if ret_docs:
            rag_str_result += ret_docs

        else:
            rag_str_result += " - All Retrieved Docs, In Chat History."

        return rag_str_result
