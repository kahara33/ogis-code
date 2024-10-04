import json
from pathlib import Path

import langchain
import openai
import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from rag_tabular.json_to_db import query_sql_db
from rag_textual.retrieve_from_db import load_db, retrieve_documents
from util.api import API
from util.catvar import DevPhase

TOP_K = 3  # NOTE: ChromaDBからレトリーブする数

REFERENCE_DIR = Path(__file__).parent.joinpath("../../data/2024-02-29/参照項目/")

langchain.verbose = False  # type: ignore[attr-defined]
langchain.debug = False  # type: ignore[attr-defined]
langchain.llm_cache = None  # type: ignore[attr-defined]


def _load_reference_json_file(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def get_reference(series: pd.Series) -> dict:
    if series["フェーズ"] == DevPhase.RD.ja:
        return _load_reference_json_file(
            REFERENCE_DIR.joinpath("要件定義_参照項目.json")
        )
    elif series["フェーズ"] == DevPhase.DES1.ja:
        return _load_reference_json_file(
            REFERENCE_DIR.joinpath("基本設計_参照項目.json")
        )
    elif series["フェーズ"] == DevPhase.DES2.ja:
        return _load_reference_json_file(
            REFERENCE_DIR.joinpath("詳細設計_参照項目.json")
        )
    elif series["フェーズ"] == DevPhase.IMPL.ja:
        return _load_reference_json_file(
            REFERENCE_DIR.joinpath("実装・単テ_参照項目.json")
        )
    elif series["フェーズ"] == DevPhase.INT.ja:
        return _load_reference_json_file(REFERENCE_DIR.joinpath("結テ_参照項目.json"))
    elif series["フェーズ"] == DevPhase.ST.ja:
        return _load_reference_json_file(REFERENCE_DIR.joinpath("ST_参照項目.json"))
    else:
        raise ValueError(f"Unknown phase: {series['フェーズ']}")


def get_pre_info(json_obj: dict, bool_current_system: bool = True):
    series, df = query_sql_db(
        json_obj=json_obj, remove_phase_key=False
    )  # NOTE: 過去の関連データを取得
    current_system = series["システム"]
    if bool_current_system:
        df = df[
            df["システム"] != current_system
        ]  # NOTE: 過去の関連データのうち、現在のシステムに関連するものを除外
    reference_information = get_reference(series)  # NOTE: 参照項目の情報を取得
    return series, df, reference_information


def generate_review(
    json_obj: dict,
    analysisPoint: str,
    api: API,
):
    series, df, reference_information = get_pre_info(json_obj=json_obj)
    chat: ChatOpenAI | AzureChatOpenAI = api.init_chat_model()
    prompt = ChatPromptTemplate.from_template(
        "あなたは渡されたデータのレビューを行うAIアシスタントです。\n"
        "現在のデータは次のものです。\n"
        "<現在のデータ>{data}</現在のデータ>\n"
        "過去のデータは次のものです。\n"
        "<過去のデータ>{past_data}</過去のデータ>\n"
        "現在の開発フェーズ[{phase}]にて比較を行う上で"
        "参考可能なソフトウェア開発データ白書2018-2019に記載されている参照項目は下のものです。\n"
        "<参照項目>{reference_information}</参照項目>\n"
        "現在のデータと参照項目の比較と、現在のデータと過去のデータの比較を、以下の手順でレビューを行なってください。\n"
        "{analysisPoint}\n"
        "以上の点を踏まえ、現在のデータの表示、過去データや参照項目との比較を行い、回答を提示してください。\n"
        "あなたの全ての出力はMarkdown形式で整形してください。\n"
        "見出しには'##'などを使用し、内容に沿った絵文字を見出しの後ろに使用してください。\n"
        "見出しごとに'***'で水平線を使用して区切ってください。\n "
        "文章内においては、指標名を'`'を使用して出力して下さい。\n"
        "'多い、高い、長い、上回る'などの文章の直後には、矢印などの絵文字を使用して視覚的に分かりやすくしてください。\n"
        "'少ない、低い、短い、下回る'などの文章の直後には、矢印などの絵文字を使用して視覚的に分かりやすくしてください。\n"
        "数値に関しては、'**'を使用して出力してください。"
    )

    output_parser = StrOutputParser()
    chain = prompt | chat | output_parser
    response = chain.stream(
        {
            "data": series,  # NOTE: 現在のデータ
            "past_data": df.T,  # NOTE:　過去の関連データ
            "phase": series["フェーズ"],  # NOTE: 現在のフェーズ
            "reference_information": reference_information,  # NOTE: 参照項目の情報
            "analysisPoint": analysisPoint,  # NOTE: 分析の観点
        }
    )
    prompt_content = prompt.format(
        data=series,
        past_data=df.T,
        phase=series["フェーズ"],
        reference_information=reference_information,
        analysisPoint=analysisPoint,
    )
    return response, prompt_content


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "_retrieve_from_chromadb",
            "description": (
                "Use this function to answer user questions about IPA information "
                "from ソフトウェア開発データ白書2018-2019. "
                "Input should be a fully formed vector database query."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The query should be returned in plain text, not in JSON. "
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    }
]


def _retrieve_from_chromadb(query: str, api: API):
    """Function to query Chroma database with a provided query."""
    retriever = load_db(api)
    return retrieve_documents(
        retriever=retriever, query=query, k=TOP_K
    )  # NOTE: ChromaDBからレトリーブ


def _execute_function_call(function_info: dict, api: API):
    function_to_execute = function_info["name"]
    if function_to_execute == "_retrieve_from_chromadb":
        arguments = json.loads(function_info["arguments"])
        query = arguments["query"]
        results = _retrieve_from_chromadb(query, api)
    else:
        results = f"Error: function {function_to_execute} does not exist"
    return results


def _chat_completion_request(
    messages,
    api: API,
    tools=None,
    tool_choice="auto",
):

    client: openai.OpenAI | openai.AzureOpenAI = api.init_openai_client()
    response = client.chat.completions.create(
        model=api.config.chat_model_name,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        stream=True,
    )
    return response


def _chat_completion_response(
    messages,
    api: API,
):
    client: openai.OpenAI | openai.AzureOpenAI = api.init_openai_client()
    stream = client.chat.completions.create(
        model=api.config.chat_model_name,
        messages=messages,
        stream=True,
    )
    return stream


def review_agent(
    messages,
    api: API,
):
    function_info = {
        "name": None,
        "arguments": "",
    }
    function_stream = _chat_completion_request(
        messages,
        api,
        tools=TOOLS,
        tool_choice="auto",
    )
    for chunk in function_stream:
        if len(chunk.choices) == 0:
            continue
        if chunk.choices[0].delta.content is None:  # NOTE: function callingが選択された
            function_call = chunk.choices[0].delta.tool_calls
            if function_call:
                if (
                    function_call[0].function.name is not None
                    and function_call[0].function.name != ""
                ):
                    function_info["name"] = function_call[0].function.name
                if (
                    function_call[0].function.arguments is not None
                    and function_call[0].function.arguments != ""
                ):
                    function_info["arguments"] += function_call[0].function.arguments
            if chunk.choices[0].finish_reason == "tool_calls":
                results = _execute_function_call(function_info, api)
                messages.append(
                    {
                        "role": "function",
                        "name": function_info["name"],
                        "content": str(results),
                    }
                )
                chat_stream = _chat_completion_response(messages, api)
                yield from chat_stream
        else:  # NOTE: 通常のレスポンスが選択された場合
            yield chunk
            yield from function_stream
