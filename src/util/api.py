"""Implementation of api-related utilities."""

import os
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum

import openai
from langchain_openai import (
    AzureChatOpenAI,
    AzureOpenAIEmbeddings,
    ChatOpenAI,
    OpenAIEmbeddings,
)

_APITypeInfo = namedtuple("_APITypeInfo", ["index", "name"])


MAX_TOKENS = 4000
TEMPERAURE = 0.7


class InvalidAPIError(Exception):
    pass


class APIType(Enum):
    AZURE_OPENAI = _APITypeInfo(0, "Azure OpenAI")
    OPENAI = _APITypeInfo(1, "OpenAI")

    @property
    def index(self):
        return self.value.index

    @property
    def name(self):
        return self.value.name


@dataclass(kw_only=True)
class OpenAIAPIConfig:
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_org_id: str | None = None

    chat_model_name: str = "gpt-4"
    temperature: float = TEMPERAURE
    max_tokens: int = MAX_TOKENS
    embd_model_name: str = "text-embedding-3-small"

    def __post_init__(self):
        if self.openai_api_key is None:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_base_url is None:
            self.openai_base_url = (
                os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
            )
        if self.openai_org_id is None:
            self.openai_org_id = os.getenv("OPENAI_ORG_ID")
        self.validate()

    @classmethod
    def from_env(cls) -> "OpenAIAPIConfig":
        return cls()

    def validate(self) -> None:
        """Validates an OpenAI API key."""
        try:
            client = self.init_openai_client()
        except Exception:
            raise InvalidAPIError("OpenAIクライアントの初期化に失敗しました。")
        try:
            self.init_chat_model()
        except Exception:
            raise InvalidAPIError("チャットモデルの初期化に失敗しました。")
        try:
            self.init_embd_model()
        except Exception:
            raise InvalidAPIError("埋め込みモデルの初期化に失敗しました。")
        try:
            client.models.retrieve(self.chat_model_name)
        except Exception:
            raise InvalidAPIError("チャットモデルの取得に失敗しました。")
        try:
            client.models.retrieve(self.embd_model_name)
        except Exception:
            raise InvalidAPIError("埋め込みモデルの取得に失敗しました。")

    def init_openai_client(self) -> openai.OpenAI:
        return openai.OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_base_url,
            organization=self.openai_org_id,
        )

    def init_chat_model(self) -> ChatOpenAI:
        return ChatOpenAI(
            client=self.init_openai_client().chat.completions,
            api_key=self.openai_api_key,  # type: ignore[arg-type]
            model=self.chat_model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def init_embd_model(self) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            client=self.init_openai_client().embeddings,
            api_key=self.openai_api_key,  # type: ignore[arg-type]
            model=self.embd_model_name,
        )


@dataclass(kw_only=True)
class AzureOpenAIAPIConfig:
    azure_openai_ad_token: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    openai_api_version: str | None = None

    chat_model_name: str = "gpt-4"
    temperature: float = TEMPERAURE
    max_tokens: int = MAX_TOKENS
    embd_model_name: str = "text-embedding-3-small"

    def __post_init__(self):
        if self.azure_openai_ad_token is None:
            self.azure_openai_ad_token = os.getenv("AZURE_OPENAI_AD_TOKEN")
        if self.azure_openai_api_key is None:
            self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if self.azure_openai_endpoint is None:
            self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if self.openai_api_version is None:
            self.openai_api_version = (
                os.getenv("OPENAI_API_VERSION") or "2023-07-01-preview"
            )
        self.validate()

    @classmethod
    def from_env(cls) -> "AzureOpenAIAPIConfig":
        return cls()

    def validate(self) -> None:
        """Validates an OpenAI API key."""
        try:
            self.init_openai_client()
        except Exception:
            raise InvalidAPIError("OpenAIクライアントの初期化に失敗しました。")
        try:
            self.init_chat_model()
        except Exception:
            raise InvalidAPIError("チャットモデルの初期化に失敗しました。")
        try:
            self.init_embd_model()
        except Exception:
            raise InvalidAPIError("埋め込みモデルの初期化に失敗しました。")
        # NOTE: Unlike OpenAI, there seems to be no `models` API in Azure OpenAI.
        # FIXME: We have to validate the API info, cf.
        #   https://learn.microsoft.com/en-us/answers/questions/1472308/how-to-validate-azure-open-ai-configuration-triple
        #   The problem is, even if we succeeded in instantiating `AzureOpenAIAPIConfig`,
        #   we cannot be sure that the API info is valid.

    def init_openai_client(self) -> openai.AzureOpenAI:
        assert self.azure_openai_endpoint is not None  # for mypy
        return openai.AzureOpenAI(
            azure_ad_token=self.azure_openai_ad_token,
            api_key=self.azure_openai_api_key,
            azure_endpoint=self.azure_openai_endpoint,
            api_version=self.openai_api_version,
        )

    def init_chat_model(self) -> AzureChatOpenAI:
        assert self.openai_api_version is not None
        return AzureChatOpenAI(
            azure_ad_token=self.azure_openai_ad_token,  # type: ignore[arg-type]
            api_key=self.azure_openai_api_key,  # type: ignore[arg-type]
            azure_endpoint=self.azure_openai_endpoint,
            api_version=self.openai_api_version,
            azure_deployment=self.chat_model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        # NOTE: Due to a bug in langchain-openai, the following code does not work.
        #   More precisely, the `client` parameter is ignored.
        #   Since the bug is already fixed in the `master` branch, we should be
        #   able to replace it once a next version of langchain-openai is released.
        # return AzureChatOpenAI(
        #     client=self.init_openai_client().chat.completions,
        #     model=self.chat_model_name,
        #     temperature=self.temperature,
        #     max_tokens=self.max_tokens,
        # )

    def init_embd_model(self) -> AzureOpenAIEmbeddings:
        return AzureOpenAIEmbeddings(
            azure_ad_token=self.azure_openai_ad_token,  # type: ignore[arg-type]
            api_key=self.azure_openai_api_key,  # type: ignore[arg-type]
            azure_endpoint=self.azure_openai_endpoint,
            api_version=self.openai_api_version,
            azure_deployment=self.embd_model_name,
        )
        # NOTE: Due to a bug in langchain-openai, the following code does not work.
        #   More precisely, the `client` parameter is ignored.
        #   Since the bug is already fixed in the `master` branch, we should be
        #   able to replace it once a next version of langchain-openai is released.
        # return AzureOpenAIEmbeddings(
        #     client=self.init_openai_client().embeddings,
        #     model=self.embd_model_name,
        # )


@dataclass(kw_only=True)
class API:
    type: APIType
    config: OpenAIAPIConfig | AzureOpenAIAPIConfig

    def __post_init__(self):
        if self.type is APIType.OPENAI:
            assert isinstance(self.config, OpenAIAPIConfig)
        elif self.type is APIType.AZURE_OPENAI:
            assert isinstance(self.config, AzureOpenAIAPIConfig)
        else:
            raise ValueError("Invalid APIType")

    @classmethod
    def from_env(cls, api_type: APIType) -> "API":
        if api_type == APIType.OPENAI:
            return cls(type=api_type, config=OpenAIAPIConfig.from_env())
        elif api_type == APIType.AZURE_OPENAI:
            return cls(type=api_type, config=AzureOpenAIAPIConfig.from_env())
        else:
            raise ValueError("Invalid APIType")

    def init_openai_client(self) -> openai.OpenAI | openai.AzureOpenAI:
        return self.config.init_openai_client()

    def init_chat_model(self) -> ChatOpenAI | AzureChatOpenAI:
        return self.config.init_chat_model()

    def init_embd_model(self) -> OpenAIEmbeddings | AzureOpenAIEmbeddings:
        return self.config.init_embd_model()


def has_valid_openai_api_from_env():
    try:
        API.from_env(APIType.OPENAI)
    except InvalidAPIError:
        return False
    return True


# FIXME: The following function does not work as expected.
# def has_valid_azure_openai_api_from_env():
#     try:
#         API.from_env(APIType.AZURE_OPENAI)
#     except InvalidAPIError:
#         return False
#     return True
