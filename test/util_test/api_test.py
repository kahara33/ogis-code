import pytest

from util.api import (
    API,
    MAX_TOKENS,
    TEMPERAURE,
    APIType,
    AzureOpenAIAPIConfig,
    InvalidAPIError,
    OpenAIAPIConfig,
    has_valid_openai_api_from_env,
)


def test_APIType():
    assert len(APIType) == 2
    assert APIType.AZURE_OPENAI.index == 0
    assert APIType.AZURE_OPENAI.name == "Azure OpenAI"
    assert APIType.OPENAI.index == 1
    assert APIType.OPENAI.name == "OpenAI"
    for index, api in enumerate(APIType):
        assert api.index == index
        assert api.name == api.value.name


def test_invalid_openai_api_config():
    with pytest.raises(InvalidAPIError):
        OpenAIAPIConfig(openai_api_key="obviously_invalid_key")


@pytest.mark.skipif(
    not has_valid_openai_api_from_env(), reason="OpenAI API credentials not found"
)
def test_valid_openai_api_config():
    api_config = OpenAIAPIConfig.from_env()
    assert api_config.openai_api_key is not None
    assert api_config.openai_base_url is not None
    # NOTE: api.openai_org_id can be None
    assert api_config.chat_model_name == "gpt-4o"
    assert api_config.temperature == TEMPERAURE
    assert api_config.max_tokens == MAX_TOKENS
    assert api_config.embd_model_name == "text-embedding-ada-002"


@pytest.mark.skipif(
    not has_valid_openai_api_from_env(), reason="OpenAI API credentials not found"
)
def test_valid_openai_api():
    api = API.from_env(APIType.OPENAI)
    assert api.type is APIType.OPENAI
    assert api.config.openai_api_key is not None
    assert api.config.openai_base_url is not None
    # NOTE: api.config.openai_org_id can be None
    assert api.config.chat_model_name == "gpt-4o"
    assert api.config.temperature == TEMPERAURE
    assert api.config.max_tokens == MAX_TOKENS
    assert api.config.embd_model_name == "text-embedding-ada-002"


@pytest.mark.skip(reason="Araya TODO: Azure OpenAI API verification is incomplete.")
def test_valid_azure_openai_api():
    with pytest.raises(InvalidAPIError):
        AzureOpenAIAPIConfig(azure_openai_api_key="obviously_valid_key")


# TODO: Add equivalent test functions for Azure OpenAI
