"""Small OpenAI-compatible HTTP provider with no SDK dependency."""
from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


class ProviderError(RuntimeError):
    pass


class OpenAICompatibleProvider:
    """Call a chat-completions-compatible endpoint and return a JSON object.

    `auth_mode` may be `bearer` or `api-key`. The endpoint and credentials are
    supplied by the caller so secrets never belong in prompts or source files.
    """

    def __init__(self, endpoint: str, model: str, api_key: str | None = None,
                 auth_mode: str = "bearer", api_version: str | None = None,
                 timeout_seconds: int = 90):
        self.endpoint = endpoint
        self.model = model
        self.api_key = api_key
        self.auth_mode = auth_mode
        self.api_version = api_version
        self.timeout_seconds = timeout_seconds
        self.last_metadata: dict[str, Any] = {}

    def complete(self, *, system_prompt: str,
                 user_context: dict[str, Any]) -> dict[str, Any]:
        url = self.endpoint
        if self.api_version:
            parts = urlsplit(url)
            query = urlencode({"api-version": self.api_version})
            url = urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))
        headers = {"Content-Type": "application/json"}
        if self.auth_mode == "api-key":
            if not self.api_key:
                raise ProviderError("api_key is required when auth_mode is 'api-key'")
            headers["api-key"] = self.api_key
        elif self.auth_mode == "bearer":
            headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            raise ProviderError("auth_mode must be 'bearer' or 'api-key'")
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_context, ensure_ascii=False)},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        request = Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            raise ProviderError(f"LLM endpoint returned HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderError(f"LLM endpoint request failed: {exc}") from exc

        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("LLM response did not contain choices[0].message.content") from exc
        if isinstance(content, dict):
            result = content
        else:
            try:
                result = json.loads(content)
            except (TypeError, json.JSONDecodeError) as exc:
                raise ProviderError("LLM response content was not valid JSON") from exc
        if not isinstance(result, dict):
            raise ProviderError("LLM response JSON must be an object")
        self.last_metadata = {
            "provider": "openai-compatible-http",
            "model": self.model,
            "usage": payload.get("usage", {}),
            "response_id": payload.get("id"),
        }
        return result


class EntraOpenAICompatibleProvider(OpenAICompatibleProvider):
    """OpenAI-compatible provider using Microsoft Entra ID tokens.

    Local development can use an Azure CLI login. A deployed application can
    use managed identity through the same DefaultAzureCredential chain.
    """

    def __init__(self, endpoint: str, model: str,
                 scope: str = "https://cognitiveservices.azure.com/.default",
                 timeout_seconds: int = 90):
        try:
            from azure.identity import DefaultAzureCredential
        except ImportError as exc:
            raise ProviderError("Entra authentication requires the optional azure-identity dependency") from exc
        super().__init__(endpoint, model, api_key=None, auth_mode="entra",
                         timeout_seconds=timeout_seconds)
        self.credential = DefaultAzureCredential()
        self.scope = scope

    def complete(self, *, system_prompt: str,
                 user_context: dict[str, Any]) -> dict[str, Any]:
        try:
            self.api_key = self.credential.get_token(self.scope).token
        except Exception as exc:
            raise ProviderError(f"Unable to acquire Entra ID token: {exc}") from exc
        self.auth_mode = "bearer"
        result = super().complete(system_prompt=system_prompt, user_context=user_context)
        self.last_metadata["authentication"] = "entra-id"
        return result


def provider_from_environment(timeout_seconds: int = 90) -> OpenAICompatibleProvider:
    """Create either API-key or Entra provider from environment configuration."""
    endpoint = os.environ.get("AGENT_LLM_ENDPOINT")
    model = os.environ.get("AGENT_LLM_MODEL")
    mode = os.environ.get("AGENT_LLM_AUTH_MODE", "entra").lower()
    if not endpoint or not model:
        raise ProviderError("AGENT_LLM_ENDPOINT and AGENT_LLM_MODEL are required")
    if mode == "entra":
        return EntraOpenAICompatibleProvider(
            endpoint, model,
            scope=os.environ.get("AGENT_LLM_SCOPE", "https://cognitiveservices.azure.com/.default"),
            timeout_seconds=timeout_seconds,
        )
    if mode == "api-key":
        return OpenAICompatibleProvider(
            endpoint, model, os.environ.get("AGENT_LLM_API_KEY"),
            auth_mode="api-key", api_version=os.environ.get("AGENT_LLM_API_VERSION"),
            timeout_seconds=timeout_seconds,
        )
    raise ProviderError("AGENT_LLM_AUTH_MODE must be 'entra' or 'api-key'")
