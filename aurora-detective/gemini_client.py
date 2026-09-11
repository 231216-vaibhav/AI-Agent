"""Google Gemini Client Service using the official google-genai SDK.
Supports structured outputs via Pydantic, automatic single-retry error handling,
and offline mock execution without API key leakage.
"""

import os
import time
import logging
from typing import Type, TypeVar, Optional, Callable, Any
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

from google import genai
from google.genai import types

# Load environment variables
env_file = Path(__file__).resolve().parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

logger = logging.getLogger("aurora.gemini")

T = TypeVar("T", bound=BaseModel)


class GeminiClientError(Exception):
    """Raised when Gemini API request fails or cannot be parsed."""
    pass


class GeminiService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self._client: Optional[genai.Client] = None
        self._mock_handler: Optional[Callable[[str, str, Type[BaseModel]], BaseModel]] = None

        # Check for mock flag
        if os.getenv("MOCK_GEMINI", "false").lower() in ("true", "1", "yes"):
            self._setup_default_mock()

    def _setup_default_mock(self):
        try:
            from tests.mock_gemini import default_mock_gemini_handler
            self._mock_handler = default_mock_gemini_handler
        except ImportError:
            pass

    @property
    def is_api_key_configured(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    @property
    def client(self) -> genai.Client:
        if self._mock_handler is not None:
            return self._client or genai.Client(api_key="mock-key")
        if self._client is None:
            if not self.is_api_key_configured:
                raise GeminiClientError(
                    "GEMINI_API_KEY is not configured. Please add GEMINI_API_KEY to your .env file."
                )
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def set_mock_handler(self, handler: Optional[Callable[[str, str, Type[BaseModel]], BaseModel]]) -> None:
        """Configures a mock handler for testing without making real API calls."""
        self._mock_handler = handler

    def _execute_api_call(self, system_instruction: str, prompt: str, response_model: Type[T]) -> T:
        """Executes a structured content generation call with Gemini Flash."""
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_model,
            temperature=0.2
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )

        if not response or not response.text:
            raise GeminiClientError("Gemini API returned an empty response.")

        return response_model.model_validate_json(response.text)

    def generate_structured(self, system_instruction: str, prompt: str, response_model: Type[T]) -> T:
        """Generates structured Pydantic response with automatic single retry on failure."""
        if self._mock_handler is not None:
            try:
                result = self._mock_handler(system_instruction, prompt, response_model)
                if isinstance(result, response_model):
                    return result
                if isinstance(result, dict):
                    return response_model.model_validate(result)
                raise GeminiClientError(f"Mock handler returned invalid type: {type(result)}")
            except GeminiClientError:
                raise
            except Exception as exc:
                raise GeminiClientError(f"Gemini API generation failed: {str(exc)}")

        attempts = 0
        last_error: Optional[Exception] = None

        while attempts < 3:
            try:
                attempts += 1
                return self._execute_api_call(system_instruction, prompt, response_model)
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Gemini API attempt %d failed for model %s: %s",
                    attempts,
                    self.model,
                    str(exc)
                )
                if attempts < 3:
                    time.sleep(2.0 * attempts)  # Exponential backoff before retry

        error_message = f"Gemini API generation failed after 3 attempts: {str(last_error)}"
        logger.error(error_message)
        raise GeminiClientError(error_message)


# Global reusable service
gemini_service = GeminiService()
