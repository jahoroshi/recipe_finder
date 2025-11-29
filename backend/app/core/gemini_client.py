"""Gemini API client for embeddings and text generation."""

import asyncio
from functools import lru_cache
from typing import List, Optional

import google.generativeai as genai
from google.generativeai import GenerativeModel

from app.config import get_settings


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, requests_per_minute: int):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.interval = 60.0 / requests_per_minute
        self.last_request_time = 0.0
        self._lock: Optional[asyncio.Lock] = None

    def _get_lock(self) -> asyncio.Lock:
        """Get or create lock for current event loop."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()

        if self._lock is None or self._lock._loop != loop:
            self._lock = asyncio.Lock()

        return self._lock

    async def acquire(self) -> None:
        """Acquire rate limit slot, waiting if necessary."""
        lock = self._get_lock()
        async with lock:
            now = asyncio.get_event_loop().time()
            time_since_last_request = now - self.last_request_time

            if time_since_last_request < self.interval:
                wait_time = self.interval - time_since_last_request
                await asyncio.sleep(wait_time)

            self.last_request_time = asyncio.get_event_loop().time()


class GeminiClient:
    """Client for Google Gemini API operations.

    Provides methods for generating embeddings and text using Gemini models,
    with built-in rate limiting, retry logic, and error handling.
    """

    def __init__(
        self,
        api_key: str,
        embedding_model: str,
        text_model: str,
        rate_limit_rpm: int,
        timeout: int,
        max_retries: int,
    ):
        """Initialize Gemini client.

        Args:
            api_key: Google Gemini API key
            embedding_model: Name of the embedding model
            text_model: Name of the text generation model
            rate_limit_rpm: Rate limit in requests per minute
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.text_model = text_model
        self.timeout = timeout
        self.max_retries = max_retries

        # Configure Gemini API
        genai.configure(api_key=api_key)

        # Initialize rate limiter
        self._rate_limiter = RateLimiter(rate_limit_rpm)

        # Initialize models
        self._generative_model: Optional[GenerativeModel] = None

    def _get_generative_model(self) -> GenerativeModel:
        """Get or create generative model instance.

        Returns:
            GenerativeModel instance
        """
        if self._generative_model is None:
            self._generative_model = GenerativeModel(self.text_model)
        return self._generative_model

    async def generate_embedding(
        self,
        text: str,
        task_type: str = "retrieval_document",
    ) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to generate embedding for
            task_type: Task type for embedding generation
                (retrieval_query, retrieval_document, semantic_similarity, etc.)

        Returns:
            Embedding vector as list of floats

        Raises:
            ValueError: If text is empty
            Exception: If API call fails after retries
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        await self._rate_limiter.acquire()

        for attempt in range(self.max_retries + 1):
            try:
                # Use asyncio.to_thread for blocking API call
                response = await asyncio.to_thread(
                    genai.embed_content,
                    model=self.embedding_model,
                    content=text,
                    task_type=task_type,
                )

                return response["embedding"]

            except Exception as e:
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    raise Exception(
                        f"Failed to generate embedding after {self.max_retries + 1} attempts: {e}"
                    ) from e

    async def generate_batch_embeddings(
        self,
        texts: List[str],
        task_type: str = "retrieval_document",
        batch_size: int = 100,
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to generate embeddings for
            task_type: Task type for embedding generation
            batch_size: Number of texts to process in each batch

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("All texts are empty")

        embeddings = []

        # Process in batches
        for i in range(0, len(valid_texts), batch_size):
            batch = valid_texts[i : i + batch_size]

            # Generate embeddings for batch concurrently
            batch_embeddings = await asyncio.gather(
                *[self.generate_embedding(text, task_type) for text in batch]
            )

            embeddings.extend(batch_embeddings)

        return embeddings

    async def generate_text(
        self,
        prompt: str,
        max_output_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using Gemini text model.

        Args:
            prompt: Input prompt for text generation
            max_output_tokens: Maximum tokens in generated response
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated text

        Raises:
            ValueError: If prompt is empty
            Exception: If API call fails after retries
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        await self._rate_limiter.acquire()

        for attempt in range(self.max_retries + 1):
            try:
                model = self._get_generative_model()

                # Use asyncio.to_thread for blocking API call
                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                    generation_config={
                        "max_output_tokens": max_output_tokens,
                        "temperature": temperature,
                    },
                )

                return response.text

            except Exception as e:
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    raise Exception(
                        f"Failed to generate text after {self.max_retries + 1} attempts: {e}"
                    ) from e

    async def ping(self) -> bool:
        """Check if Gemini API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Try generating a simple embedding
            await self.generate_embedding("test", task_type="semantic_similarity")
            return True
        except Exception:
            return False


@lru_cache()
def get_gemini_client() -> GeminiClient:
    """Get cached Gemini client instance.

    Returns:
        GeminiClient instance configured from settings
    """
    settings = get_settings()

    return GeminiClient(
        api_key=settings.gemini_api_key,
        embedding_model=settings.gemini_embedding_model,
        text_model=settings.gemini_text_model,
        rate_limit_rpm=settings.gemini_rate_limit_rpm,
        timeout=settings.gemini_timeout,
        max_retries=settings.gemini_max_retries,
    )
