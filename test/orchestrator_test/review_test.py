"""Tests for the review module."""

import json

import pytest

from orchestrator.review import generate_review, review_agent
from rag_tabular.excel_to_csv import get_rag_tab_path
from util.api import API, APIType, has_valid_openai_api_from_env


@pytest.mark.skipif(
    not has_valid_openai_api_from_env(), reason="OpenAI API key not found"
)
def test_generate_review():
    api = API.from_env(APIType.OPENAI)
    json_path = get_rag_tab_path().parent.joinpath("json/基本設計/基本設計_00.json")
    with open(json_path, "r", encoding="utf-8") as f:
        json_obj = json.load(f)
    analysisPoint = "時間がないので、必ず50文字以内で簡潔にレビューを行なってください。"
    response, prompt_content = generate_review(json_obj, analysisPoint, api)
    response_text = ""
    for chunk in response:
        if chunk is not None:
            response_text += chunk
    assert isinstance(response_text, str)
    assert isinstance(prompt_content, str)


@pytest.mark.skipif(
    not has_valid_openai_api_from_env(), reason="OpenAI API key not found"
)
def test_review_agent():
    api = API.from_env(APIType.OPENAI)
    messages = []
    messages.append({"role": "user", "content": "こんにちは"})
    response = review_agent(
        messages,
        api,
    )
    response_text = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            response_text += chunk.choices[0].delta.content
    assert isinstance(response_text, str)


@pytest.mark.skipif(
    not has_valid_openai_api_from_env(), reason="OpenAI API key not found"
)
def test_from_main():
    """Formerly the `if __name__ == "__main__":` block in review.py."""
    json_path = get_rag_tab_path().parent.joinpath("json/基本設計/基本設計_00.json")
    with open(json_path, "r", encoding="utf-8") as f:
        json_obj = json.load(f)

    analysisPoint = ""
    api = API.from_env(APIType.OPENAI)
    response, _ = generate_review(
        json_obj,
        analysisPoint,
        api,
    )
    for chunk in response:
        print(chunk, end="", flush=True)

    messages = []
    messages.append({"role": "user", "content": "こんにちは"})

    response = review_agent(
        messages,
        api,
    )
    for chunk in response:
        print(chunk.choices[0].delta.content, end="", flush=True)
