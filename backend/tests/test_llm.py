import pytest

from app.ai.llm import LLMClient


def test_default_provider_is_mock():
    client = LLMClient()

    assert client.provider == "mock"
    assert client.api_key == ""


def test_custom_provider_and_api_key():
    client = LLMClient(
        provider="openai",
        api_key="test-key",
    )

    assert client.provider == "openai"
    assert client.api_key == "test-key"


def test_generate_returns_demo_response():
    client = LLMClient()

    result = client.generate(
        "Analyze this failed payment."
    )

    assert result == (
        "Demo AI response. Connect an LLM provider "
        "for production reasoning."
    )


def test_empty_prompt_is_allowed():
    client = LLMClient()

    result = client.generate("")

    assert isinstance(result, str)
    assert result != ""


def test_non_string_prompt_rejected():
    client = LLMClient()

    with pytest.raises(TypeError):
        client.generate(None)