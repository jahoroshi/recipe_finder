"""Embedding service for Gemini API integration with caching."""

import asyncio
from typing import Optional

from app.core.gemini_client import GeminiClient
from app.db.models import Recipe
from app.services.cache import CacheService


class EmbeddingService:
    """Service for generating embeddings using Gemini API.

    Provides embedding generation with caching, batch processing, and rate limiting.

    Features:
        - Rate limiting and retry logic (handled by GeminiClient)
        - Batch processing for efficiency
        - Embedding caching strategy (24-hour TTL)
        - Error handling for API failures

    Example:
        ```python
        service = EmbeddingService(gemini_client, cache_service)
        embedding = await service.generate_embedding("pasta carbonara")
        ```
    """

    def __init__(
        self,
        gemini_client: GeminiClient,
        cache_service: CacheService,
        batch_size: int = 100,
    ):
        """Initialize embedding service.

        Args:
            gemini_client: Gemini API client instance
            cache_service: Cache service for embedding caching
            batch_size: Number of texts to process in each batch (default: 100)
        """
        self.gemini = gemini_client
        self.cache = cache_service
        self.batch_size = batch_size
        self.model = gemini_client.embedding_model

    async def generate_embedding(
        self,
        text: str,
        task_type: str = "retrieval_document",
        use_cache: bool = True,
    ) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to generate embedding for
            task_type: Task type for embedding generation
                (retrieval_query, retrieval_document, semantic_similarity)
            use_cache: Whether to use cached embeddings (default: True)

        Returns:
            Embedding vector as list of floats (768 dimensions)

        Raises:
            ValueError: If text is empty
            Exception: If API call fails after retries
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Try to get from cache first
        if use_cache:
            cached_embedding = await self.cache.get_embedding(text)
            if cached_embedding is not None:
                return cached_embedding

        # Generate new embedding
        embedding = await self.gemini.generate_embedding(text, task_type=task_type)

        # Cache the result
        if use_cache:
            await self.cache.set_embedding(text, embedding)

        return embedding

    async def generate_batch_embeddings(
        self,
        texts: list[str],
        task_type: str = "retrieval_document",
        use_cache: bool = True,
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts in batches.

        Processes texts in batches to optimize API usage and respect rate limits.
        Checks cache for each text before generating.

        Args:
            texts: List of texts to generate embeddings for
            task_type: Task type for embedding generation
            use_cache: Whether to use cached embeddings (default: True)

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        # Filter out empty texts
        valid_texts = [t.strip() for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("All texts are empty")

        embeddings = []
        texts_to_generate = []
        text_indices = []

        # Check cache for each text
        for i, text in enumerate(valid_texts):
            if use_cache:
                cached_embedding = await self.cache.get_embedding(text)
                if cached_embedding is not None:
                    embeddings.append((i, cached_embedding))
                    continue

            # Track texts that need generation
            texts_to_generate.append(text)
            text_indices.append(i)

        # Generate embeddings for uncached texts in batches
        if texts_to_generate:
            generated_embeddings = []

            for i in range(0, len(texts_to_generate), self.batch_size):
                batch = texts_to_generate[i : i + self.batch_size]

                # Generate embeddings concurrently for the batch
                batch_embeddings = await asyncio.gather(
                    *[
                        self.gemini.generate_embedding(text, task_type=task_type)
                        for text in batch
                    ]
                )

                generated_embeddings.extend(batch_embeddings)

                # Cache generated embeddings
                if use_cache:
                    cache_tasks = [
                        self.cache.set_embedding(text, embedding)
                        for text, embedding in zip(batch, batch_embeddings)
                    ]
                    await asyncio.gather(*cache_tasks)

            # Add generated embeddings to result with indices
            for idx, embedding in zip(text_indices, generated_embeddings):
                embeddings.append((idx, embedding))

        # Sort by original index and extract embeddings
        embeddings.sort(key=lambda x: x[0])
        return [emb for _, emb in embeddings]

    async def create_recipe_embedding(
        self, recipe: Recipe, use_cache: bool = True
    ) -> list[float]:
        """Generate embedding for a recipe.

        Combines recipe name, description, cuisine type, and diet types into a
        single text representation for embedding generation.

        Args:
            recipe: Recipe model instance
            use_cache: Whether to use cached embeddings (default: True)

        Returns:
            Embedding vector for the recipe

        Example:
            ```python
            recipe = await recipe_repo.get(recipe_id)
            embedding = await service.create_recipe_embedding(recipe)
            ```
        """
        # Build comprehensive text representation
        text_parts = [recipe.name]

        if recipe.description:
            text_parts.append(recipe.description)

        if recipe.cuisine_type:
            text_parts.append(f"Cuisine: {recipe.cuisine_type}")

        if recipe.diet_types:
            text_parts.append(f"Diet: {', '.join(recipe.diet_types)}")

        # Add difficulty level (handle both enum and string)
        difficulty_value = (
            recipe.difficulty.value
            if hasattr(recipe.difficulty, "value")
            else recipe.difficulty
        )
        text_parts.append(f"Difficulty: {difficulty_value}")

        # Combine all parts
        recipe_text = " | ".join(text_parts)

        return await self.generate_embedding(
            recipe_text, task_type="retrieval_document", use_cache=use_cache
        )

    async def update_recipe_embeddings(
        self, recipes: list[Recipe], use_cache: bool = True
    ) -> list[tuple[Recipe, list[float]]]:
        """Generate embeddings for multiple recipes.

        Args:
            recipes: List of Recipe model instances
            use_cache: Whether to use cached embeddings (default: True)

        Returns:
            List of (recipe, embedding) tuples

        Example:
            ```python
            recipes = await recipe_repo.get_recipes_without_embeddings()
            results = await service.update_recipe_embeddings(recipes)
            ```
        """
        if not recipes:
            return []

        # Create text representations for all recipes
        recipe_texts = []
        for recipe in recipes:
            text_parts = [recipe.name]

            if recipe.description:
                text_parts.append(recipe.description)

            if recipe.cuisine_type:
                text_parts.append(f"Cuisine: {recipe.cuisine_type}")

            if recipe.diet_types:
                text_parts.append(f"Diet: {', '.join(recipe.diet_types)}")

            # Add difficulty level (handle both enum and string)
            difficulty_value = (
                recipe.difficulty.value
                if hasattr(recipe.difficulty, "value")
                else recipe.difficulty
            )
            text_parts.append(f"Difficulty: {difficulty_value}")

            recipe_texts.append(" | ".join(text_parts))

        # Generate embeddings in batches
        embeddings = await self.generate_batch_embeddings(
            recipe_texts, task_type="retrieval_document", use_cache=use_cache
        )

        return list(zip(recipes, embeddings))

    async def generate_query_embedding(
        self, query: str, use_cache: bool = True
    ) -> list[float]:
        """Generate embedding for a search query.

        Uses 'retrieval_query' task type which is optimized for search queries.

        Args:
            query: Search query text
            use_cache: Whether to use cached embeddings (default: True)

        Returns:
            Embedding vector for the query

        Example:
            ```python
            query_embedding = await service.generate_query_embedding("italian pasta")
            ```
        """
        return await self.generate_embedding(
            query, task_type="retrieval_query", use_cache=use_cache
        )

    async def ping(self) -> bool:
        """Check if Gemini API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        return await self.gemini.ping()
