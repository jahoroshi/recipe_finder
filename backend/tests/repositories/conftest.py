"""Pytest fixtures for repository tests."""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, TypeDecorator, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.pool import StaticPool

from app.db.models import DifficultyLevel


class JSONEncodedDict(TypeDecorator):
    """Represents a dict as JSON-encoded string in SQLite."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


# Create a separate base class for test models to avoid conflicts with app models
class TestBase(DeclarativeBase):
    """Separate base for test models."""
    pass


class TestBaseModel(TestBase):
    """Test base model with common fields."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )


# Simple test models - avoid naming conflicts with actual models
class Recipe(TestBaseModel):
    """Simplified Recipe model for testing."""

    __tablename__ = "test_recipes"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[dict] = mapped_column(JSONEncodedDict, nullable=False, default=dict)
    prep_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cook_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel), nullable=False, default=DifficultyLevel.MEDIUM
    )
    cuisine_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    diet_types: Mapped[str] = mapped_column(String, nullable=False, default="")
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Simple relationships
    ingredients: Mapped[list["Ingredient"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    recipe_categories: Mapped[list["RecipeCategory"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    nutritional_info: Mapped["NutritionalInfo | None"] = relationship(back_populates="recipe", cascade="all, delete-orphan", uselist=False)


class Ingredient(TestBaseModel):
    """Simplified Ingredient model for testing."""

    __tablename__ = "test_ingredients"

    recipe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("test_recipes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float | None] = mapped_column(Integer, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")


class Category(TestBaseModel):
    """Simplified Category model for testing."""

    __tablename__ = "test_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    recipe_categories: Mapped[list["RecipeCategory"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class RecipeCategory(TestBaseModel):
    """Simplified RecipeCategory junction table for testing."""

    __tablename__ = "test_recipe_categories"

    recipe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("test_recipes.id"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("test_categories.id"), nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_categories")
    category: Mapped["Category"] = relationship(back_populates="recipe_categories")


class NutritionalInfo(TestBaseModel):
    """Simplified NutritionalInfo model for testing."""

    __tablename__ = "test_nutritional_info"

    recipe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("test_recipes.id"), nullable=False, unique=True)
    calories: Mapped[float | None] = mapped_column(Integer, nullable=True)
    protein_g: Mapped[float | None] = mapped_column(Integer, nullable=True)
    carbohydrates_g: Mapped[float | None] = mapped_column(Integer, nullable=True)
    fat_g: Mapped[float | None] = mapped_column(Integer, nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="nutritional_info")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,  # Use StaticPool to share the same in-memory connection
        connect_args={"check_same_thread": False},  # Allow sharing connection
    )

    # Create all test tables from TestBase metadata
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with AsyncSession(db_engine, expire_on_commit=False) as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def sample_recipe(db_session: AsyncSession) -> Recipe:
    """Create a sample recipe for testing."""
    recipe = Recipe(
        id=uuid.uuid4(),
        name="Test Recipe",
        description="A delicious test recipe",
        instructions={"steps": ["Step 1", "Step 2"]},
        prep_time=15,
        cook_time=30,
        servings=4,
        difficulty=DifficultyLevel.MEDIUM,
        cuisine_type="Italian",
        diet_types="vegetarian",
    )

    db_session.add(recipe)
    await db_session.commit()
    await db_session.refresh(recipe)

    return recipe


@pytest_asyncio.fixture
async def sample_recipes(db_session: AsyncSession) -> list[Recipe]:
    """Create multiple sample recipes for testing."""
    recipes = [
        Recipe(
            id=uuid.uuid4(),
            name="Easy Pasta",
            description="Simple pasta dish",
            instructions={"steps": ["Boil pasta", "Add sauce"]},
            prep_time=5,
            cook_time=10,
            servings=2,
            difficulty=DifficultyLevel.EASY,
            cuisine_type="Italian",
            diet_types="vegetarian",
        ),
        Recipe(
            id=uuid.uuid4(),
            name="Complex Dish",
            description="Difficult recipe",
            instructions={"steps": ["Step 1", "Step 2", "Step 3"]},
            prep_time=30,
            cook_time=60,
            servings=6,
            difficulty=DifficultyLevel.HARD,
            cuisine_type="French",
            diet_types="gluten-free",
        ),
        Recipe(
            id=uuid.uuid4(),
            name="Quick Salad",
            description="Fast and healthy",
            instructions={"steps": ["Mix ingredients"]},
            prep_time=10,
            cook_time=0,
            servings=1,
            difficulty=DifficultyLevel.EASY,
            cuisine_type="Mediterranean",
            diet_types="vegan,gluten-free",
        ),
    ]

    for recipe in recipes:
        db_session.add(recipe)

    await db_session.commit()

    for recipe in recipes:
        await db_session.refresh(recipe)

    return recipes


@pytest_asyncio.fixture
async def recipe_with_ingredients(db_session: AsyncSession) -> Recipe:
    """Create a recipe with ingredients."""
    recipe = Recipe(
        id=uuid.uuid4(),
        name="Pasta Carbonara",
        description="Classic Italian pasta",
        instructions={"steps": ["Cook pasta", "Make sauce", "Combine"]},
        prep_time=10,
        cook_time=15,
        servings=4,
        difficulty=DifficultyLevel.MEDIUM,
        cuisine_type="Italian",
        diet_types="",
    )

    db_session.add(recipe)
    await db_session.flush()

    ingredients = [
        Ingredient(
            id=uuid.uuid4(),
            recipe_id=recipe.id,
            name="pasta",
            quantity=400,
            unit="g",
        ),
        Ingredient(
            id=uuid.uuid4(),
            recipe_id=recipe.id,
            name="eggs",
            quantity=4,
            unit="pieces",
        ),
        Ingredient(
            id=uuid.uuid4(),
            recipe_id=recipe.id,
            name="parmesan",
            quantity=100,
            unit="g",
        ),
    ]

    for ingredient in ingredients:
        db_session.add(ingredient)

    await db_session.commit()
    await db_session.refresh(recipe)

    return recipe


@pytest_asyncio.fixture
async def recipe_with_relations(db_session: AsyncSession) -> Recipe:
    """Create a recipe with all relations."""
    recipe = Recipe(
        id=uuid.uuid4(),
        name="Full Recipe",
        description="Recipe with all relations",
        instructions={"steps": ["Step 1"]},
        prep_time=20,
        cook_time=40,
        servings=4,
        difficulty=DifficultyLevel.MEDIUM,
        cuisine_type="Asian",
        diet_types="vegetarian",
    )

    db_session.add(recipe)
    await db_session.flush()

    ingredient = Ingredient(
        id=uuid.uuid4(),
        recipe_id=recipe.id,
        name="tofu",
        quantity=200,
        unit="g",
    )
    db_session.add(ingredient)

    category = Category(
        id=uuid.uuid4(),
        name="Main Dish",
        slug="main-dish",
        description="Main course recipes",
    )
    db_session.add(category)
    await db_session.flush()

    recipe_category = RecipeCategory(
        id=uuid.uuid4(),
        recipe_id=recipe.id,
        category_id=category.id,
    )
    db_session.add(recipe_category)

    nutritional_info = NutritionalInfo(
        id=uuid.uuid4(),
        recipe_id=recipe.id,
        calories=350,
        protein_g=20,
        carbohydrates_g=40,
        fat_g=10,
    )
    db_session.add(nutritional_info)

    await db_session.commit()
    await db_session.refresh(recipe)

    return recipe


@pytest_asyncio.fixture
async def recipes_with_embeddings(db_session: AsyncSession) -> list[Recipe]:
    """Create recipes with vector embeddings for similarity testing."""
    recipes = [
        Recipe(
            id=uuid.uuid4(),
            name="Recipe 1",
            description="Description 1",
            instructions={"steps": ["Step 1"]},
            prep_time=10,
            cook_time=20,
            servings=2,
            difficulty=DifficultyLevel.EASY,
            cuisine_type="Italian",
            diet_types="",
            embedding=None,
        ),
        Recipe(
            id=uuid.uuid4(),
            name="Recipe 2",
            description="Description 2",
            instructions={"steps": ["Step 1"]},
            prep_time=15,
            cook_time=25,
            servings=3,
            difficulty=DifficultyLevel.MEDIUM,
            cuisine_type="Chinese",
            diet_types="",
            embedding=None,
        ),
    ]

    for recipe in recipes:
        db_session.add(recipe)

    await db_session.commit()

    for recipe in recipes:
        await db_session.refresh(recipe)

    return recipes
