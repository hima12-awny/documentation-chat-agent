from llama_index.core import Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.indices.vector_store.retrievers import (
    VectorIndexRetriever,
)
import nest_asyncio
from tqdm.notebook import tqdm
from concurrent.futures import ThreadPoolExecutor
from llama_index.core import SimpleDirectoryReader
import json
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
import os


class VecDB:
    def __init__(
        self,
        repo_name: str | None = None,
        embedding_model="all-MiniLM-L6-v2",
        persist_directory="vec_db",

    ) -> None:

        self.repo_name = repo_name

        self.embedding_model = embedding_model
        self.persist_directory = persist_directory

        self.embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")

        self.retriever: None | VectorIndexRetriever = None

        self.index: VectorStoreIndex | None = None

    def split_docs(self, docs) -> list[dict[str, str]]:

        splitted_docs: list[dict[str, str]] = []
        for doc in docs:
            file_name = doc.metadata['file_name']
            file_ex = '.' + doc.metadata['file_name'].split('.')[-1]

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
                dict(
                    file_name=file_name,
                    doc=doc.page_content
                )
                for doc in file_docs
            )
        return splitted_docs

    def split_into_chunks(self, data_recs, chunk_size):
        for i in range(0, len(data_recs), chunk_size):
            yield data_recs[i: i+chunk_size]

    def process_chunk(self, chunk) -> list[Document]:
        chunk_docs: list[Document] = []
        for doc in tqdm(chunk, desc="Embedding Chunk", position=1):
            chunk_docs.append(
                Document(
                    metadata=dict(file_name=doc['file_name']),
                    text=doc['doc'],
                    embedding=self.embed_model.get_text_embedding(
                        doc['doc']),
                )
            )

        return chunk_docs

    def vectorize_db(
        self,
        repo_name: str | None = None,
        chunk_size=50,
        max_workers=4
    ):

        if self.repo_name is None and repo_name is None:
            raise Exception("Must Specify repo_name!")

        repo_name = repo_name or self.repo_name or ''

        with open("supported_files.json", 'r') as sf:
            self.supported_files_types = json.loads(sf.read())

        with open("supported_files_names.json", 'r') as sf:
            self.supported_files_types_names = json.loads(sf.read())

        repo_path = os.path.join(".", "repos", repo_name)

        reader = SimpleDirectoryReader(
            input_dir=repo_path,
            recursive=True,
            required_exts=self.supported_files_types
        )
        documents = reader.load_data(num_workers=4)

        splitted_docs = self.split_docs(docs=documents)

        chunks = list(self.split_into_chunks(splitted_docs, chunk_size))

        ready_docs = []

        with ThreadPoolExecutor(
            max_workers=max_workers
        ) as executor:
            chunks_docs = list(
                tqdm(
                    executor.map(self.process_chunk, chunks),
                    position=0,
                    total=len(chunks),
                    desc="Embedding Texts"
                )
            )
        for chunk_docs in chunks_docs:
            ready_docs.extend(chunk_docs)

        nest_asyncio.apply()

        self.index = VectorStoreIndex.from_documents(
            documents=ready_docs,
            embed_model=self.embed_model,
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

        self.retriever = self.index.as_retriever(
            similarity_top_k=15)  # type: ignore

        print("VecDB Storing Done.")

    def load_vecdb(
        self,
        repo_name: str | None = None,
    ) -> None:

        if self.repo_name is None and repo_name is None:
            raise Exception("Must Specify repo_name!")

        repo_name = repo_name or self.repo_name or ''

        persist_dir_name = os.path.join(
            ".",
            self.persist_directory,
            repo_name
        )

        storage_context = StorageContext.from_defaults(
            persist_dir=persist_dir_name)

        self.index = load_index_from_storage(
            storage_context=storage_context,
            embed_model=self.embed_model
        )  # type: ignore

        self.retriever = self.index.as_retriever(  # type: ignore
            similarity_top_k=15,
        )  # type: ignore

        print("VecDB Loading Done.")

    def query(self, text: str):
        if self.retriever is None:
            self.load_vecdb()

        return self.retriever.retrieve(text)  # type: ignore
