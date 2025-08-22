from openai import AsyncOpenAI
from typing import Optional, Any
import httpx
import logfire


class OpenaiSTT:
    def __init__(
            self,
            api_key: str,
            base_url: str,
            default_model: str = "whisper-1",
            default_language: str = "auto",
            default_temperature: float = 0.1
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
        self.default_language = default_language
        self.default_temperature = default_temperature

    def _make_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            http_client=httpx.AsyncClient(),
            base_url=self.base_url,
            api_key=self.api_key,
        )

    async def transcribe(
            self,
            audio_data: bytes,
            model: Optional[str] = None,
            language: Optional[str] = None,
            temperature: Optional[float] = None
    ) -> Any:
        client = self._make_client()
        return await client.audio.transcriptions.create(
            model=model or self.default_model,
            file=audio_data,
            language=language or self.default_language,
            temperature=temperature or self.default_temperature
        )


class NexaraSTT(OpenaiSTT):

    API_URL = "https://api.nexara.ru/api/v1"

    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url=self.API_URL,
            default_model="whisper-1",
            default_language="auto"
        )

    async def audio_analyze(
            self,
            audio_data: bytes,
            model: Optional[str] = None,
            language: Optional[str] = None
    ) -> str:
        try:
            transcription = await self.transcribe(audio_data, model, language)
            return transcription.text
        except Exception as e:
            logfire.error("Nexara transcription failed", error=str(e))
            raise ValueError(f"Nexara transcription failed: {str(e)}") from e