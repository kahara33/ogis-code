"""作成したChromaDBから、クエリに基づいてベクトル検索を行う"""

from pathlib import Path

from langchain_community.vectorstores.chroma import Chroma

from rag_textual.txt_to_db import get_ipa_db_path
from util.api import API

# ChromaDBから取得する最大の数を指定
MAX_RETRIEVE = 5
QUERY = "IPA白書によると、基本設計レビュー実績工数の中央値はどのぐらいの値でしょうか?"


def load_db(
    api: API,
    persist_directory: Path | None = None,
) -> Chroma:
    """ChromaDBのロード"""
    embeddings = api.init_embd_model()
    if persist_directory is None:
        persist_directory = get_ipa_db_path()
    db = Chroma(persist_directory=str(persist_directory), embedding_function=embeddings)
    return db


def _documents_to_dicts(query: str, context_docs: list) -> list:
    """抽出したドキュメントのリストをjson形式のリストに変換"""
    docs_as_dicts = []
    for doc, score in context_docs:
        formatted_content = doc.page_content.replace(". ", ".\n")
        docs_as_dicts.append(
            {"query": query, "page_content": formatted_content, "score": score}
        )
    return docs_as_dicts


def retrieve_documents(
    retriever: Chroma, query: str, k: int = 5, doc_type: bool = True
) -> list:
    """ドキュメントの抽出"""
    context_docs = retriever.similarity_search_with_score(query, k=k)
    if doc_type:
        return _documents_to_dicts(query=query, context_docs=context_docs)
    else:
        return context_docs
