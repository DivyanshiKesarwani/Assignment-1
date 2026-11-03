from types import SimpleNamespace

import pytest

from src.reminder_agent import model


def test_reads_env_file_and_process_environment_overrides(
    tmp_path, monkeypatch
) -> None:
    (tmp_path / ".env").write_text(
        "MODEL_API_KEY='file-secret'\nMODEL_NAME=file-model\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)

    assert model.load_model_config() == ("file-secret", "file-model")

    monkeypatch.setenv("MODEL_API_KEY", "environment-secret")
    assert model.load_model_config() == ("environment-secret", "file-model")


def test_missing_model_configuration_has_no_secret_in_error(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)

    with pytest.raises(model.ModelConfigurationError) as error:
        model.load_model_config()

    assert "secret" not in str(error.value).lower()
    assert "key" in str(error.value).lower()


def test_model_call_extracts_text_with_mock_sdk(monkeypatch) -> None:
    class FakeModels:
        @staticmethod
        def generate_content(**kwargs):
            assert kwargs["model"] == "test-model"
            assert kwargs["contents"] == "user"
            assert kwargs["config"].system_instruction == "system"
            return SimpleNamespace(text='{"intent":"clarify"}')

    class FakeGemini:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.models = FakeModels()

    monkeypatch.setenv("MODEL_API_KEY", "test-key")
    monkeypatch.setenv("MODEL_NAME", "test-model")
    monkeypatch.setattr(
        model, "_gemini_client", lambda api_key: (FakeGemini(api_key), RuntimeError)
    )

    assert model.generate_response("system", "user") == '{"intent":"clarify"}'


def test_provider_error_is_sanitized(monkeypatch) -> None:
    class FakeProviderError(RuntimeError):
        code = 400
        message = "request failed with test-secret"

    class FakeModels:
        @staticmethod
        def generate_content(**kwargs):
            raise FakeProviderError("request failed with test-secret")

    class FakeGemini:
        def __init__(self, api_key):
            self.models = FakeModels()

    monkeypatch.setenv("MODEL_API_KEY", "test-secret")
    monkeypatch.setenv("MODEL_NAME", "test-model")
    monkeypatch.setattr(
        model, "_gemini_client", lambda api_key: (FakeGemini(api_key), RuntimeError)
    )

    with pytest.raises(model.ModelServiceError) as error:
        model.generate_response("system", "user")

    assert "test-secret" not in str(error.value)
    assert "[REDACTED]" in str(error.value)
    assert "400" in str(error.value)


def test_accepts_gemini_specific_key_setting(tmp_path, monkeypatch) -> None:
    (tmp_path / ".env").write_text(
        "GEMINI_API_KEY=gemini-secret\nMODEL_NAME=gemini-model\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)

    assert model.load_model_config() == ("gemini-secret", "gemini-model")
