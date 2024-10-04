import os
import re
import shutil
from pathlib import Path
from typing import List

import neologdn
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


def get_rag_txt_path() -> Path:
    """Returns the path to the text file representing the IPA whitepaper.

    Raises: `ValueError` if the environment variable `RAG_TXT_PATH` is not properly set.
    """
    _rag_txt_path: str | None = os.getenv("RAG_TXT_PATH")
    if _rag_txt_path is None:
        raise ValueError("環境変数RAG_TXT_PATHを設定してください。")
    rag_txt_path = Path(_rag_txt_path)
    if not rag_txt_path.is_file():
        raise ValueError(
            f"ファイル {rag_txt_path} が見つかりません。"
            "環境変数RAG_TXT_PATHを正しく設定してください。"
        )
    if rag_txt_path.suffix != ".txt":
        raise ValueError(
            f"ファイル {rag_txt_path} はテキスト (.txt) ファイルでなくてはなりません。"
            "環境変数RAG_TXT_PATHを正しく設定してください。"
        )
    return rag_txt_path


def get_ipa_db_path() -> Path:
    """Returns the path to the vector database of IPA whitepaper."""
    rag_txt_path = get_rag_txt_path()
    # if rag_txt_path is /foo/IPA_2018-2019.txt,
    # then ipa_db_path is /foo/IPA_2018-2019_chroma_db.
    return rag_txt_path.parent.joinpath(f"{rag_txt_path.stem}_chroma_db")


class TextProcessor:
    def __init__(self, embedding_model: str, knowledge_path: str):
        self.embedding_model = embedding_model
        self.knowledge_path = knowledge_path

    def clean_text(self, text: str) -> str:
        """テキストのクリーニング処理"""
        # 入力テキストを正規化（長音記号の統一、全角・半角の統一など）
        text = neologdn.normalize(text)
        for char in ["", "", "�"]:
            text = text.replace(char, " ")
        return text

    def insert_newlines(self, text: str, specific_strings: list) -> str:
        """テキストをページごとに区切る"""
        pattern = (
            r"(\d+)(\n?[^\d\n]*?)("
            + "|".join(re.escape(s) for s in specific_strings)
            + ")"
        )
        return re.sub(pattern, r"\n\n\1\3", text)

    def split_text_into_chunks(
        self, text: str, separator="\n\n", chunk_size=512, chunk_overlap=128
    ) -> List[Document]:
        """チャンキング処理"""
        text_splitter = CharacterTextSplitter(
            separator=separator, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        return text_splitter.create_documents([text])

    def initialize_embeddings(self) -> OpenAIEmbeddings:
        """OpenAIのEmbeddingモデルの初期化"""
        return OpenAIEmbeddings(model=self.embedding_model)

    def store_documents(self, docs: List[Document], embeddings: OpenAIEmbeddings):
        """ChromaDBの作成と保存。既存のDBがあれば削除。"""
        persist_dir = Path(self.knowledge_path)
        if persist_dir.exists():
            shutil.rmtree(persist_dir)
            print(f"既存のChromaDBを削除しました: {persist_dir.resolve()}")

        db = Chroma.from_documents(docs, embeddings, persist_directory=str(persist_dir))
        print(f"新しいChromaDBを作成しました: {persist_dir.resolve()}")
        return db.as_retriever()


def main():
    ipa_db_path = get_ipa_db_path()
    processor = TextProcessor(
        embedding_model="text-embedding-3-small",
        knowledge_path=ipa_db_path,
    )
    rag_txt_path = get_rag_txt_path()
    with open(rag_txt_path, "r", encoding="utf-8") as file:
        text = file.read()

    specific_strings = ["ソフトウェア開発データ白書", "● ソフトウェア開発データ白書"]
    text = processor.insert_newlines(text, specific_strings)
    text = processor.clean_text(text)
    docs = processor.split_text_into_chunks(text)
    embeddings = processor.initialize_embeddings()
    processor.store_documents(docs, embeddings)


if __name__ == "__main__":
    main()
