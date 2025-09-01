"""A tool that implements the knowledge base of agatha porblems."""

#import torch
from pathlib import Path

from langchain.tools import Tool
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

#__DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def agatha_knowledge(cache: str | Path = Path("./__knowledge")) -> Tool:
    """Return the knowledge source for the AGATHA website."""
    cache =  Path(cache)
    # create the embedding model to add and search to the vector db
    embedding_model = HuggingFaceEmbeddings(
        model = "intfloat/multilingual-e5-large",
        model_kwargs = {
            "model_kwargs": {"torch_dtype": "float16", "device_map": "auto"},
        }
    )
    # index the data if needed else just return the existing database
    if cache.exists():
        knowledge_source = Chroma(
            "agatha_website",
            embedding_model,
            persist_directory=str(cache),
        )
    else:
        loader = DoclingLoader(
            file_path = [
                "https://agatha.arch.be/help/States-Archives_user-guide-genealogical-sources.pdf",
                "https://agatha.arch.be/help/States-Archives_user-guide-analyses-records.pdf",
                "https://agatha.arch.be/help/",
                "https://agatha.arch.be/help/beginning/",
            ],
            export_type = ExportType.MARKDOWN,
        )
        splitter = MarkdownHeaderTextSplitter(
            strip_headers = False,
            headers_to_split_on = [
                ("##",  "h2"),
                ("###", "h3"),
            ],
        )
        documents = [ chunk for doc in loader.load() for chunk in splitter.split_text(doc.page_content) ]
        
        knowledge_source = Chroma.from_documents(
            documents, 
            embedding_model,
            collection_name="agatha_website",
            persist_directory=str(cache),
        )
    # finally, make it a tool that can be transparently used by an agent.
    knowledge_tool = create_retriever_tool(
        retriever   = knowledge_source.as_retriever(search_type="mmr"),
        name        = "agatha_help", 
        description = """
            Content of the help section from the AGATHA platform as well as
            that of the 'getting started' and 'genealogy' user manuals.
            """,
    )
    return knowledge_tool