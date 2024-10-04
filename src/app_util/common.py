"""Utilities common to all pages."""

import streamlit as st

# "🏠ホーム"ページに表示する機能説明
HOME_MARKDOWN = """
データの可視化機能、AIとのチャット機能、およびシステムデータの分析機能を利用できます。

- 可視化機能を利用するためには、

    1. サイドバーを開いて、
    2. 「📊可視化」メニューを選択し、
    3. システムデータをJSON形式でアップロードしてください。

- チャット機能を利用するためには、

    1. サイドバーを開いて、
    2. 「💬チャット」メニューを選択し、
    3. Azure OpenAI (もしくはOpenAI) のAPIキー等を入力してください。

- 分析機能を利用するためには、

    1. サイドバーを開いて、
    2. 「📈分析」メニューを選択し、
    3. システムデータをJSON形式でアップロードして、
    4. Azure OpenAI (もしくはOpenAI) のAPIキー等を入力してください。

システムデータとAPIキー等は、3つの機能で共通して利用されます。
"""

ANALYSIS_PROMPT = (
    "1. 現在のデータと過去のデータに含まれる指標を比較し、優れている点や改善が必要な点を具体的に指摘してください。"
    "    その際、はじめに注目すべき指標について述べ、その後Markdown形式で表を用いて視覚的にわかりやすく示してください。可能な限り、様々な指標についての比較を行ってください。\n\n"
    "2. IPA参照項目に記載されている統計量と現在のデータを比較し、プロジェクトの位置付けを評価してください。根拠となる計算結果を明示してください。\n\n"
    "3. 現在のデータの解釈や改善案の提示を行ってください。"
    "    その際、プロジェクトの背景情報（システムの特性や制約条件など）を具体的に考慮し、それらを踏まえた改善案を提示してください。\n\n"
    "4. レビューを通じて発見した課題や問題点について、優先度を考慮しながら具体的な改善策を提案してください。改善案には優先順位を付けてください。\n\n"
    "5. レビュー結果を総括し、プロジェクトの現状と今後の方向性についてまとめてください。その際、具体的なアクションプランや目標設定を含めてください。"
)

# 全てのページに共通する設定
COMMON_PAGE_CONFIG = {
    "layout": "centered",
    "initial_sidebar_state": "auto",
    "menu_items": {
        "Get Help": None,
        "Report a bug": "mailto:otoba@araya.org",
        "About": (
            "オージス総研様のシステムデータを可視化して、"
            "チャット形式で分析するためのWebアプリケーションです。\n\n"
            "開発元：（株）アラヤ https://www.araya.org \n\n"
            "開発期間：2024年1月〜3月"
        ),
    },
}


def init_session_state():
    """Initialize session state variables common to all pages."""
    if "json_obj" not in st.session_state:
        st.session_state["json_obj"] = None
    if "data_data_file_name" not in st.session_state:
        st.session_state["data_data_file_name"] = None
    if "data_file_size" not in st.session_state:
        st.session_state["data_file_size"] = None
    if "api" not in st.session_state:
        st.session_state["api"] = None
