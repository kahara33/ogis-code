"""Tests for the txt_to_db module."""

from typing import List

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from rag_textual.txt_to_db import TextProcessor, get_ipa_db_path, get_rag_txt_path


def test_txt_to_db():
    rag_txt_path = get_rag_txt_path()
    ipa_db_path = get_ipa_db_path()
    processor = TextProcessor(
        embedding_model="text-embedding-3-small", knowledge_path=ipa_db_path
    )
    with open(rag_txt_path, "r", encoding="utf-8") as file:
        text = file.read()

    specific_strings = ["ソフトウェア開発データ白書", "● ソフトウェア開発データ白書"]
    processed_text = processor.insert_newlines(text, specific_strings)
    assert "\n\n" in processed_text, "テキストが正しく区切られていません"

    cleaned_text = processor.clean_text(processed_text)
    assert "�" not in cleaned_text, "テキストのクリーニングが正しく行われていません"

    docs = processor.split_text_into_chunks(cleaned_text)
    assert isinstance(docs, List), "チャンキングの結果がリストではありません"
    assert all(
        isinstance(doc, Document) for doc in docs
    ), "チャンキングの結果にDocumentオブジェクト以外が含まれています"

    embeddings = processor.initialize_embeddings()
    assert isinstance(
        embeddings, OpenAIEmbeddings
    ), "embeddingsがOpenAIEmbeddingsのインスタンスではありません"
