import pytest
from streamlit.testing.v1 import AppTest

from util.api import API, APIType, has_valid_openai_api_from_env

# Relative to the present test module
APP_PATH = "../../app/pages/2_💬_チャット.py"


def test_initial_state():
    at = AppTest.from_file(APP_PATH).run()
    assert at.session_state["api"] is None
    assert len(at.title) == 1
    assert at.title[0].body == "AIとのチャット💬"
    assert len(at.error) == 1
    assert at.error[0].body == "サイドバーを開き、APIキーを入力してください。"
    assert len(at.chat_input) == 0
    assert len(at.chat_message) == 0
    # TODO: Check the status for sidebar


@pytest.mark.skipif(
    not has_valid_openai_api_from_env(), reason="OpenAI API credentials not found"
)
def test_chat_openai():
    at = AppTest.from_file(APP_PATH).run()
    api = API.from_env(APIType.OPENAI)
    api.config.temperature = 0.0  # For test reproducibility
    # Simulates the user entering OpenAI API credentials
    at.session_state["api"] = api
    at.run()
    assert len(at.title) == 1
    assert at.title[0].body == "AIとのチャット💬"
    assert len(at.error) == 0  # Error message should be gone
    assert at.sidebar.success[0].body == "OpenAI のAPIを使用します。"
    assert len(at.chat_input) == 1
    assert len(at.chat_message) == 0

    first_prompt = (
        "私が「おはようございます！」と言うので、"
        "「おはようございます！」とだけ返してください。"
        "おはようございます！"
    )
    first_response = "おはようございます！"
    second_prompt = (
        "私が「こんにちは！」と言うので、"
        "「こんにちは！」とだけ返してください。"
        "こんにちは！"
    )
    second_response = "こんにちは！"
    third_prompt = "あなたの最初の応答は何ですか？そっくりそのまま返してください。"
    third_response = "おはようございます！"

    # Simulates the user entering a first chat message
    at.chat_input[0].set_value(first_prompt).run()
    assert len(at.title) == 1
    assert at.title[0].body == "AIとのチャット💬"
    assert len(at.error) == 0  # Error message should be gone
    assert at.sidebar.success[0].body == "OpenAI のAPIを使用します。"
    assert len(at.chat_input) == 1
    assert len(at.chat_message) == 2
    assert at.chat_message[0].avatar == "user"
    assert at.chat_message[0].markdown[0].value == first_prompt
    assert at.chat_message[1].avatar == "assistant"
    assert at.chat_message[1].markdown[0].value == first_response

    # Simulates the user entering a second chat message
    at.chat_input[0].set_value(second_prompt).run()
    assert len(at.title) == 1
    assert at.title[0].body == "AIとのチャット💬"
    assert len(at.error) == 0  # Error message should be gone
    assert at.sidebar.success[0].body == "OpenAI のAPIを使用します。"
    assert len(at.chat_input) == 1
    assert len(at.chat_message) == 2 * 2
    assert at.chat_message[0].avatar == "user"
    assert at.chat_message[0].markdown[0].value == first_prompt
    assert at.chat_message[1].avatar == "assistant"
    assert at.chat_message[1].markdown[0].value == first_response
    assert at.chat_message[2].avatar == "user"
    assert at.chat_message[2].markdown[0].value == second_prompt
    assert at.chat_message[3].avatar == "assistant"
    assert at.chat_message[3].markdown[0].value == second_response

    # Simulates the user entering a third chat message
    at.chat_input[0].set_value(third_prompt).run()
    assert len(at.title) == 1
    assert at.title[0].body == "AIとのチャット💬"
    assert len(at.error) == 0  # Error message should be gone
    assert at.sidebar.success[0].body == "OpenAI のAPIを使用します。"
    assert len(at.chat_input) == 1
    assert len(at.chat_message) == 3 * 2
    assert at.chat_message[0].avatar == "user"
    assert at.chat_message[0].markdown[0].value == first_prompt
    assert at.chat_message[1].avatar == "assistant"
    assert at.chat_message[1].markdown[0].value == first_response
    assert at.chat_message[2].avatar == "user"
    assert at.chat_message[2].markdown[0].value == second_prompt
    assert at.chat_message[3].avatar == "assistant"
    assert at.chat_message[3].markdown[0].value == second_response
    assert at.chat_message[4].avatar == "user"
    assert at.chat_message[4].markdown[0].value == third_prompt
    assert at.chat_message[5].avatar == "assistant"
    assert at.chat_message[5].markdown[0].value == third_response


@pytest.mark.skip("Testing with Azure OpenAI API is very unstable and slow")
def test_chat_azure_openai():
    at = AppTest.from_file(APP_PATH, default_timeout=60).run()
    api = API.from_env(APIType.AZURE_OPENAI)
    api.config.temperature = 0.0  # For test reproducibility
    # Simulates the user entering OpenAI API credentials
    at.session_state["api"] = api
    at.run()
    assert len(at.title) == 1
    assert at.title[0].body == "AIとのチャット💬"
    assert len(at.error) == 0  # Error message should be gone
    assert at.sidebar.success[0].body == "Azure OpenAI のAPIを使用します。"
    assert len(at.chat_input) == 1
    assert len(at.chat_message) == 0

    first_prompt = (
        "私が「おはようございます！」と言うので、"
        "「おはようございます！」とだけ返してください。"
        "おはようございます！"
    )
    first_response = "おはようございます！"
    second_prompt = (
        "私が「こんにちは！」と言うので、"
        "「こんにちは！」とだけ返してください。"
        "こんにちは！"
    )
    second_response = "こんにちは！"
    third_prompt = "あなたの最初の応答は何ですか？そっくりそのまま返してください。"
    third_response = "おはようございます！"

    # Simulates the user entering a first chat message
    at.chat_input[0].set_value(first_prompt).run()
    assert len(at.title) == 1
    assert at.title[0].body == "AIとのチャット💬"
    assert len(at.error) == 0  # Error message should be gone
    assert at.sidebar.success[0].body == "Azure OpenAI のAPIを使用します。"
    assert len(at.chat_input) == 1
    assert len(at.chat_message) == 2
    assert at.chat_message[0].avatar == "user"
    assert at.chat_message[0].markdown[0].value == first_prompt
    assert at.chat_message[1].avatar == "assistant"
    assert at.chat_message[1].markdown[0].value == first_response

    # Simulates the user entering a second chat message
    at.chat_input[0].set_value(second_prompt).run()
    assert len(at.title) == 1
    assert at.title[0].body == "AIとのチャット💬"
    assert len(at.error) == 0  # Error message should be gone
    assert at.sidebar.success[0].body == "Azure OpenAI のAPIを使用します。"
    assert len(at.chat_input) == 1
    assert len(at.chat_message) == 2 * 2
    assert at.chat_message[0].avatar == "user"
    assert at.chat_message[0].markdown[0].value == first_prompt
    assert at.chat_message[1].avatar == "assistant"
    assert at.chat_message[1].markdown[0].value == first_response
    assert at.chat_message[2].avatar == "user"
    assert at.chat_message[2].markdown[0].value == second_prompt
    assert at.chat_message[3].avatar == "assistant"
    assert at.chat_message[3].markdown[0].value == second_response

    # Simulates the user entering a third chat message
    at.chat_input[0].set_value(third_prompt).run()
    assert len(at.title) == 1
    assert at.title[0].body == "AIとのチャット💬"
    assert len(at.error) == 0  # Error message should be gone
    assert at.sidebar.success[0].body == "Azure OpenAI のAPIを使用します。"
    assert len(at.chat_input) == 1
    assert len(at.chat_message) == 3 * 2
    assert at.chat_message[0].avatar == "user"
    assert at.chat_message[0].markdown[0].value == first_prompt
    assert at.chat_message[1].avatar == "assistant"
    assert at.chat_message[1].markdown[0].value == first_response
    assert at.chat_message[2].avatar == "user"
    assert at.chat_message[2].markdown[0].value == second_prompt
    assert at.chat_message[3].avatar == "assistant"
    assert at.chat_message[3].markdown[0].value == second_response
    assert at.chat_message[4].avatar == "user"
    assert at.chat_message[4].markdown[0].value == third_prompt
    assert at.chat_message[5].avatar == "assistant"
    assert at.chat_message[5].markdown[0].value == third_response
