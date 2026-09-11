"""OpenAI Client Service.
Manages a single reusable OpenAI client for GPT-5, implementing the Responses API
and structured outputs with single-retry error handling and zero key leakage.
"""

import logging
import time
from typing import Type, TypeVar, Optional, Callable, Any
from pydantic import BaseModel
from openai import OpenAI

from app.config import settings

logger = logging.getLogger("investigation.openai")

T = TypeVar("T", bound=BaseModel)


class OpenAIClientError(Exception):
    """Raised when OpenAI API call fails after retry or fails to parse."""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


class OpenAIService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self._client: Optional[OpenAI] = None
        self._mock_handler: Optional[Callable[[str, str, Type[BaseModel]], BaseModel]] = None

        if settings.MOCK_OPENAI:
            from app.services.mock_agent_data import default_mock_handler
            self._mock_handler = default_mock_handler

        if self._api_key and self._api_key.strip():
            self._client = OpenAI(api_key=self._api_key)

    @property
    def client(self) -> OpenAI:
        if self._mock_handler is not None:
            return self._client or OpenAI(api_key="mock-key")
        if self._client is None:
            if not self._api_key or not self._api_key.strip():
                raise OpenAIClientError(
                    "OPENAI_API_KEY is not configured on the backend. Please check .env.",
                    status_code=502
                )
            self._client = OpenAI(api_key=self._api_key)
        return self._client

    def set_mock_handler(self, handler: Optional[Callable[[str, str, Type[BaseModel]], BaseModel]]) -> None:
        """Sets a mock handler for testing without making real OpenAI API calls."""
        self._mock_handler = handler

    def _execute_api_call(self, instructions: str, input_data: str, response_model: Type[T]) -> T:
        """Executes structured API call using Responses API or beta chat completions parse."""
        # 1. Try Responses API first
        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=instructions,
                input=input_data,
                text_format=response_model
            )
            if hasattr(response, "output_parsed") and response.output_parsed is not None:
                return response.output_parsed
            if hasattr(response, "output_text") and response.output_text:
                return response_model.model_validate_json(response.output_text)
        except Exception as responses_err:
            logger.debug("Responses API parse returned: %s. Falling back to chat completions parse.", str(responses_err))

        # 2. Fallback to beta chat completions parse
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": input_data}
        ]
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=response_model
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raw_content = completion.choices[0].message.content or ""
            return response_model.model_validate_json(raw_content)
        return parsed

    def generate_structured(self, instructions: str, input_data: str, response_model: Type[T]) -> T:
        """Generates structured output for an agent with one automatic retry on failure."""
        if self._mock_handler is not None:
            result = self._mock_handler(instructions, input_data, response_model)
            if isinstance(result, response_model):
                return result
            if isinstance(result, dict):
                return response_model.model_validate(result)
            raise OpenAIClientError("Mock handler returned incompatible data type.")

        attempts = 0
        last_error: Optional[Exception] = None

        while attempts < 2:
            try:
                attempts += 1
                return self._execute_api_call(instructions, input_data, response_model)
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "OpenAI API call attempt %d failed for model %s: %s",
                    attempts,
                    self.model,
                    str(exc)
                )
                if attempts < 2:
                    time.sleep(0.5)  # Brief backoff before retry

        # Both attempts failed
        error_msg = f"Failed to generate structured AI response after 2 attempts: {str(last_error)}"
        logger.error(error_msg)
        raise OpenAIClientError(error_msg, status_code=502)


# Reusable global instance
openai_service = OpenAIService()
