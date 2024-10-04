import json

import streamlit as st

from util.api import (
    API,
    APIType,
    AzureOpenAIAPIConfig,
    InvalidAPIError,
    OpenAIAPIConfig,
)


def no_data_error():
    if st.session_state["json_obj"] is None:
        st.error("サイドバーを開き、システムデータをアップロードしてください。")


def no_api_error():
    if st.session_state["api"] is None:
        st.error("サイドバーを開き、APIキーを入力してください。")


def require_data():
    # initial status
    if st.session_state["json_obj"] is None:
        if (
            data_file := st.file_uploader(
                "データをアップロード",
                type=["json"],  # TODO: Add support for Excel files
                accept_multiple_files=False,
                key="_data_file",
                help=(
                    "データをJSON形式でアップロードすると、"
                    "関連する過去データと比較するための可視化機能と分析機能を利用できます。"
                ),
                disabled=False,
                label_visibility="visible",
            )
        ) is not None:
            st.session_state["data_file_name"] = data_file.name
            st.session_state["data_file_size"] = data_file.size
            try:
                json_obj = json.load(data_file)
            except json.JSONDecodeError:
                st.error("JSONデータの読み込みに失敗しました。")
            else:
                if "フェーズ" in json_obj:  # TODO: Do not hardcode the key name
                    # TODO: validate the JSON instance using a JSON schema
                    st.session_state["json_obj"] = json_obj
                    st.rerun()
                else:
                    st.error("JSONデータにはフェーズが含まれている必要があります。")
    # status after valid data is uploaded
    else:
        st.success(
            f"{st.session_state['data_file_name']} "
            f"({st.session_state['data_file_size']/1000:.1f}KB) "
            "がアップロードされました。"
        )

        def reset_session_state():
            st.session_state["json_obj"] = None
            st.session_state["data_file_name"] = None
            st.session_state["data_file_size"] = None
            if "review_messages" in st.session_state:
                st.session_state["review_messages"] = []
            if "started_analysis" in st.session_state:
                st.session_state["started_analysis"] = False

        st.button(
            "データを再アップロードする",
            key="_reset_data",
            help="可視化と分析のページはリセットされます。",
            on_click=reset_session_state,
            type="secondary",
            disabled=False,
            use_container_width=True,
        )


def require_api():
    # initial status
    if st.session_state["api"] is None:
        api_name = st.selectbox(
            "APIの種類を選択できます",
            (api_type.name for api_type in APIType),
            index=0,  # Defaults to Azure OpenAI
            key="_api_name",
            help=None,
            disabled=False,
            label_visibility="visible",
        )

        if api_name == APIType.OPENAI.name:
            openai_api_key = st.text_input(
                "APIキーを入力してください",
                value=None,
                max_chars=(3 + 48),
                key="_openai_api_key",
                type="password",
                help="チャット機能と分析機能を利用するためには、Open AIのAPIキーが必要です。",
                autocomplete="off",
                placeholder="sk-" + "." * 48,
                disabled=False,
                label_visibility="visible",
            )
            if openai_api_key is not None:
                try:
                    api_config = OpenAIAPIConfig(openai_api_key=openai_api_key)
                except InvalidAPIError as e:
                    st.error(e)
                else:
                    st.session_state["api"] = API(
                        type=APIType.OPENAI, config=api_config
                    )
                    st.rerun()
        elif api_name == APIType.AZURE_OPENAI.name:
            azure_openai_endpoint = st.text_input(
                "エンドポイントを入力してください",
                value=None,
                max_chars=None,
                key="_azure_openai_endpoint",
                type="default",
                help="チャット機能と分析機能を利用するためには、Azureのエンドポイントが必要です。",
                autocomplete="off",
                placeholder="https://your-endpoint.openai.azure.com/",
                disabled=False,
                label_visibility="visible",
            )
            azure_openai_api_key = st.text_input(
                "APIキーを入力してください",
                value=None,
                max_chars=32,
                key="_azure_openai_api_key",
                type="password",
                help="チャット機能と分析機能を利用するためには、Azure OpenAIのAPIキーが必要です。",
                autocomplete="off",
                placeholder="0123456789abcdef" + "." * 16,
                disabled=False,
                label_visibility="visible",
            )
            if azure_openai_api_key is not None and azure_openai_endpoint is not None:
                try:
                    api_config = AzureOpenAIAPIConfig(
                        azure_openai_endpoint=azure_openai_endpoint,
                        azure_openai_api_key=azure_openai_api_key,
                    )
                except InvalidAPIError as e:
                    st.error(e)
                else:
                    st.session_state["api"] = API(
                        type=APIType.AZURE_OPENAI, config=api_config
                    )
                    st.rerun()
    # status after valid API is entered
    else:
        st.success(f"{st.session_state['api'].type.name} のAPIを使用します。")


def sidebar0():
    with st.sidebar:
        st.success("メニューを選択してください。")


def error1():
    no_data_error()


def sidebar1():
    with st.sidebar:
        with st.container(border=True):
            require_data()


def error2():
    no_api_error()


def sidebar2():
    with st.sidebar:
        with st.container(border=True):
            require_api()


def error3():
    no_data_error()
    no_api_error()


def sidebar3():
    with st.sidebar:
        with st.container(border=True):
            require_data()
        with st.container(border=True):
            require_api()
