import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from google import genai

from ..config import settings


@dataclass
class GeneratedAsset:
    caption: str
    file_bytes: bytes
    file_ext: str
    mime_type: str


class AIProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        content_type: str,
        style: str,
        color_theme: str,
    ) -> GeneratedAsset:
        ...


class GeminiAIProvider(AIProvider):

    MODEL = "gemini-3.5-flash-lite"

    MAX_RETRIES = 3
    RETRY_DELAYS = [2, 4, 8]

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured"
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate(
        self,
        prompt: str,
        content_type: str,
        style: str,
        color_theme: str,
    ) -> GeneratedAsset:

        request = f"""
Create professional social-media content for JZD Technologies.

Content type: {content_type}
Style: {style}
Color theme: {color_theme}

User's request:
{prompt}

Write polished, professional content suitable for the requested
content type.

Return only the final content.
Do not explain your answer.
"""

        for attempt in range(self.MAX_RETRIES + 1):

            print(
                f"[Gemini] Content generation attempt "
                f"{attempt + 1}/{self.MAX_RETRIES + 1}"
            )

            try:

                response = self.client.models.generate_content(
                    model=self.MODEL,
                    contents=request,
                )

                text = (response.text or "").strip()

                if not text:
                    raise RuntimeError(
                        "Gemini returned empty content."
                    )

                print("[Gemini] Content generation successful")

                return GeneratedAsset(
                    caption=text,
                    file_bytes=b"",
                    file_ext="txt",
                    mime_type="text/plain",
                )

            except Exception as exc:

                if attempt < self.MAX_RETRIES:

                    delay = self.RETRY_DELAYS[attempt]

                    print(
                        f"[Gemini] Generation error: {exc}"
                    )

                    print(
                        f"[Gemini] Retrying in {delay} seconds..."
                    )

                    time.sleep(delay)

                    continue

                raise RuntimeError(
                    f"Gemini content generation failed: {exc}"
                ) from exc


def get_ai_provider() -> AIProvider:

    if settings.AI_PROVIDER == "mock":
        raise RuntimeError(
            "Mock AI provider is disabled. "
            "Use AI_PROVIDER=gemini."
        )

    return GeminiAIProvider()