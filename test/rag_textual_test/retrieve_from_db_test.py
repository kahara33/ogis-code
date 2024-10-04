"""Tests for the retrieve_from_db module."""

import json

import pytest
from langchain_community.vectorstores.chroma import Chroma

from rag_textual.retrieve_from_db import load_db, retrieve_documents
from util.api import API, APIType, has_valid_openai_api_from_env

QUERY = "IPA白書によると、基本設計レビュー実績工数の中央値はどのぐらいの値でしょうか?"
K = 3


@pytest.mark.skipif(
    not has_valid_openai_api_from_env(), reason="OpenAI API key not found"
)
def test_load_db():
    api = API.from_env(APIType.OPENAI)
    retriever = load_db(api)
    assert isinstance(retriever, Chroma)


@pytest.mark.skipif(
    not has_valid_openai_api_from_env(), reason="OpenAI API key not found"
)
def test_simple_retrieve():
    api = API.from_env(APIType.OPENAI)
    retriever = load_db(api)
    retrieved_contents = retrieve_documents(retriever=retriever, query=QUERY, k=K)
    assert all(
        isinstance(doc_dict, dict)
        and "query" in doc_dict
        and isinstance(doc_dict["query"], str)
        and "page_content" in doc_dict
        and isinstance(doc_dict["page_content"], str)
        and "score" in doc_dict
        and isinstance(doc_dict["score"], float)
        for doc_dict in retrieved_contents
    )


@pytest.mark.skipif(
    not has_valid_openai_api_from_env(), reason="OpenAI API key not found"
)
def test_from_main():
    """Formerly the `if __name__ == "__main__"` block in retrieve_from_db.py."""
    api = API.from_env(APIType.OPENAI)
    api.init_embd_model()

    retriever = load_db(api)
    retrieved_contents = retrieve_documents(
        retriever=retriever,
        query=QUERY,
        k=5,
    )
    print(json.dumps(retrieved_contents, ensure_ascii=False, indent=2))
