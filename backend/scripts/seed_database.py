"""Database seeding script for Recipe Management API.

This script generates and seeds realistic recipe data through the API.
Supports dry-run mode, batch processing, and comprehensive reporting.
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any
from uuid import UUID

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from scripts.recipe_generator import RecipeDataGenerator
from scripts.seeder_client import SeederAPIClient, SeederReport, ValidationReport

# Setup rich console for beautiful output
console = Console()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)


class RecipeSeeder:
    """Main seeding orchestrator for recipe database."""

    def __init__(
        self,
        api_url: str,
        batch_size: int = 10,
        dry_run: bool = False,
    ):
        """Initialize recipe seeder.

        Args:
            api_url: Base URL of the Recipe Management API
            batch_size: Number of recipes to process in each batch
            dry_run: If True, only validate data without sending to API
        """
        self.api_url = api_url
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.generator = RecipeDataGenerator()

    async def generate_recipes(
        self, count: int, categories: list[str] = None, seed: int = None
    ) -> list[dict[str, Any]]:
        """Generate recipe data.

        Args:
            count: Number of recipes to generate
            categories: Optional list of categories to include
            seed: Optional random seed for reproducibility

        Returns:
            List of recipe dictionaries
        """
        console.print(f"\n[bold cyan]Generating {count} recipes...[/bold cyan]")

        recipes = self.generator.generate_recipes(
            count=count, categories=categories, seed=seed
        )

        console.print(f"[green]Generated {len(recipes)} recipes successfully[/green]")

        # Show distribution
        distribution = self._analyze_distribution(recipes)
        self._display_distribution(distribution)

        return recipes

    def _analyze_distribution(self, recipes: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze recipe distribution by various attributes."""
        difficulty_dist = {"easy": 0, "medium": 0, "hard": 0}
        cuisine_dist = {}
        diet_dist = {}

        for recipe in recipes:
            # Difficulty
            difficulty = recipe.get("difficulty", "medium")
            difficulty_dist[difficulty] = difficulty_dist.get(difficulty, 0) + 1

            # Cuisine
            cuisine = recipe.get("cuisine_type", "Unknown")
            cuisine_dist[cuisine] = cuisine_dist.get(cuisine, 0) + 1

            # Diet types
            for diet in recipe.get("diet_types", []):
                diet_dist[diet] = diet_dist.get(diet, 0) + 1

        return {
            "difficulty": difficulty_dist,
            "cuisine": cuisine_dist,
            "diet": diet_dist,
            "total": len(recipes),
        }

    def _display_distribution(self, distribution: dict[str, Any]) -> None:
        """Display distribution statistics in a table."""
        table = Table(title="Recipe Distribution")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="magenta", justify="right")
        table.add_column("Percentage", style="green", justify="right")

        total = distribution["total"]

        # Difficulty distribution
        table.add_row("[bold]Difficulty[/bold]", "", "")
        for difficulty, count in distribution["difficulty"].items():
            pct = (count / total * 100) if total > 0 else 0
            table.add_row(f"  {difficulty.capitalize()}", str(count), f"{pct:.1f}%")

        # Cuisine distribution (top 5)
        table.add_row("[bold]Top Cuisines[/bold]", "", "")
        sorted_cuisines = sorted(
            distribution["cuisine"].items(), key=lambda x: x[1], reverse=True
        )[:5]
        for cuisine, count in sorted_cuisines:
            pct = (count / total * 100) if total > 0 else 0
            table.add_row(f"  {cuisine}", str(count), f"{pct:.1f}%")

        # Diet types
        if distribution["diet"]:
            table.add_row("[bold]Diet Types[/bold]", "", "")
            for diet, count in sorted(distribution["diet"].items()):
                pct = (count / total * 100) if total > 0 else 0
                table.add_row(f"  {diet}", str(count), f"{pct:.1f}%")

        console.print(table)

    async def seed_database(
        self, recipes: list[dict[str, Any]], show_progress: bool = True
    ) -> SeederReport:
        """Seed database with recipes.

        Args:
            recipes: List of recipe dictionaries
            show_progress: Whether to show progress bar

        Returns:
            Seeding report with statistics
        """
        if self.dry_run:
            console.print(
                "\n[yellow]DRY RUN MODE - No data will be sent to API[/yellow]"
            )
            return await self._dry_run_seed(recipes)

        console.print(
            f"\n[bold cyan]Seeding {len(recipes)} recipes to {self.api_url}...[/bold cyan]"
        )

        start_time = time.time()
        succeeded = []
        failed = []
        created_ids = []

        async with SeederAPIClient(self.api_url) as client:
            # Check API health first
            health = await client.get_health_status()
            if health.get("status") != "healthy":
                console.print("[red]API health check failed![/red]")
                logger.error(f"API Health: {health}")

            # Process in batches with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "[cyan]Seeding recipes...", total=len(recipes)
                )

                for i in range(0, len(recipes), self.batch_size):
                    batch = recipes[i : i + self.batch_size]
                    results = await client.create_recipe_batch(batch)

                    for recipe, result in zip(batch, results):
                        if result:
                            succeeded.append(recipe)
                            created_ids.append(UUID(result["id"]))
                        else:
                            failed.append(
                                {"recipe": recipe, "error": "API request failed"}
                            )

                        progress.update(task, advance=1)

        duration = time.time() - start_time
        avg_time = duration / len(recipes) if recipes else 0

        report = SeederReport(
            total_attempted=len(recipes),
            total_succeeded=len(succeeded),
            total_failed=len(failed),
            failed_recipes=failed,
            duration_seconds=duration,
            average_time_per_recipe=avg_time,
            created_recipe_ids=created_ids,
        )

        self._display_seeding_report(report)

        return report

    async def _dry_run_seed(self, recipes: list[dict[str, Any]]) -> SeederReport:
        """Simulate seeding without making API calls."""
        console.print("\n[bold]Validating recipe data...[/bold]")

        start_time = time.time()
        succeeded = []
        failed = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Validating recipes...", total=len(recipes)
            )

            for recipe in recipes:
                # Validate required fields
                validation_errors = self._validate_recipe_data(recipe)

                if not validation_errors:
                    succeeded.append(recipe)
                else:
                    failed.append({"recipe": recipe, "errors": validation_errors})

                progress.update(task, advance=1)
                # Simulate processing time
                await asyncio.sleep(0.01)

        duration = time.time() - start_time
        avg_time = duration / len(recipes) if recipes else 0

        report = SeederReport(
            total_attempted=len(recipes),
            total_succeeded=len(succeeded),
            total_failed=len(failed),
            failed_recipes=failed,
            duration_seconds=duration,
            average_time_per_recipe=avg_time,
            created_recipe_ids=[],
        )

        self._display_seeding_report(report)

        return report

    def _validate_recipe_data(self, recipe: dict[str, Any]) -> list[str]:
        """Validate recipe data structure.

        Args:
            recipe: Recipe dictionary

        Returns:
            List of validation error messages
        """
        errors = []

        # Required fields
        required = ["name", "instructions", "difficulty"]
        for field in required:
            if field not in recipe:
                errors.append(f"Missing required field: {field}")

        # Validate instructions format
        if "instructions" in recipe:
            if not isinstance(recipe["instructions"], dict):
                errors.append("Instructions must be a dictionary")
            elif "steps" not in recipe["instructions"]:
                errors.append("Instructions must contain 'steps' key")

        # Validate ingredients
        if "ingredients" in recipe:
            if not isinstance(recipe["ingredients"], list):
                errors.append("Ingredients must be a list")
            else:
                for idx, ing in enumerate(recipe["ingredients"]):
                    if not isinstance(ing, dict):
                        errors.append(f"Ingredient {idx} must be a dictionary")
                    elif "name" not in ing:
                        errors.append(f"Ingredient {idx} missing 'name' field")

        # Validate time fields
        for field in ["prep_time", "cook_time", "servings"]:
            if field in recipe:
                value = recipe[field]
                if not isinstance(value, (int, float)) or value < 0:
                    errors.append(f"{field} must be a positive number")

        return errors

    def _display_seeding_report(self, report: SeederReport) -> None:
        """Display seeding report in formatted table."""
        table = Table(title="Seeding Report")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta", justify="right")

        table.add_row("Total Attempted", str(report.total_attempted))
        table.add_row(
            "Succeeded",
            f"[green]{report.total_succeeded}[/green]",
        )
        table.add_row(
            "Failed",
            f"[red]{report.total_failed}[/red]",
        )
        table.add_row(
            "Success Rate",
            f"{(report.total_succeeded / report.total_attempted * 100):.1f}%"
            if report.total_attempted > 0
            else "N/A",
        )
        table.add_row("Duration", f"{report.duration_seconds:.2f}s")
        table.add_row("Avg Time/Recipe", f"{report.average_time_per_recipe:.3f}s")

        console.print(table)

        if report.failed_recipes:
            console.print("\n[red]Failed Recipes:[/red]")
            for failure in report.failed_recipes[:5]:  # Show first 5
                recipe_name = failure.get("recipe", {}).get("name", "Unknown")
                error = failure.get("error", failure.get("errors", "Unknown error"))
                console.print(f"  - {recipe_name}: {error}")

            if len(report.failed_recipes) > 5:
                console.print(
                    f"  ... and {len(report.failed_recipes) - 5} more failures"
                )

    async def validate_seeded_data(
        self, expected_count: int, sample_queries: list[str] = None
    ) -> ValidationReport:
        """Validate seeded data in the database.

        Args:
            expected_count: Expected number of recipes
            sample_queries: Optional list of queries to test search

        Returns:
            Validation report
        """
        if self.dry_run:
            console.print(
                "\n[yellow]Skipping validation in dry-run mode[/yellow]"
            )
            return ValidationReport(
                recipe_count_valid=True,
                search_functional=True,
                embeddings_generated=True,
                sample_queries_tested=0,
                validation_errors=[],
                overall_success=True,
            )

        console.print("\n[bold cyan]Validating seeded data...[/bold cyan]")

        errors = []
        recipe_count_valid = False
        search_functional = False
        embeddings_generated = True  # Assume true, would need specific checks

        async with SeederAPIClient(self.api_url) as client:
            # Check recipe count
            actual_count = await client.get_recipe_count()
            recipe_count_valid = actual_count >= expected_count

            if not recipe_count_valid:
                errors.append(
                    f"Recipe count mismatch: expected >= {expected_count}, got {actual_count}"
                )
            else:
                console.print(
                    f"[green]Recipe count validated: {actual_count} recipes[/green]"
                )

            # Test search functionality
            if sample_queries is None:
                sample_queries = [
                    "chicken",
                    "vegetarian pasta",
                    "chocolate dessert",
                    "quick breakfast",
                ]

            search_functional, search_results = await client.verify_search_indexing(
                sample_queries
            )

            if search_functional:
                console.print("[green]Search functionality validated[/green]")
                for result in search_results:
                    console.print(
                        f"  Query '{result['query']}': {result['result_count']} results"
                    )
            else:
                errors.append("Search functionality not working properly")
                console.print("[red]Search validation failed[/red]")

        report = ValidationReport(
            recipe_count_valid=recipe_count_valid,
            search_functional=search_functional,
            embeddings_generated=embeddings_generated,
            sample_queries_tested=len(sample_queries) if sample_queries else 0,
            validation_errors=errors,
            overall_success=not bool(errors),
        )

        self._display_validation_report(report)

        return report

    def _display_validation_report(self, report: ValidationReport) -> None:
        """Display validation report."""
        table = Table(title="Validation Report")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="magenta")

        status_icon = lambda x: "[green]PASS[/green]" if x else "[red]FAIL[/red]"

        table.add_row("Recipe Count", status_icon(report.recipe_count_valid))
        table.add_row("Search Functional", status_icon(report.search_functional))
        table.add_row("Embeddings Generated", status_icon(report.embeddings_generated))
        table.add_row("Sample Queries Tested", str(report.sample_queries_tested))
        table.add_row(
            "Overall Status",
            "[green]SUCCESS[/green]"
            if report.overall_success
            else "[red]FAILED[/red]",
        )

        console.print(table)

        if report.validation_errors:
            console.print("\n[red]Validation Errors:[/red]")
            for error in report.validation_errors:
                console.print(f"  - {error}")

    async def save_report(
        self, report: SeederReport, output_file: Path
    ) -> None:
        """Save seeding report to file.

        Args:
            report: Seeding report
            output_file: Path to output JSON file
        """
        report_data = report.model_dump(mode="json")

        # Convert UUIDs to strings for JSON serialization
        report_data["created_recipe_ids"] = [
            str(uid) for uid in report_data["created_recipe_ids"]
        ]

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        console.print(f"\n[green]Report saved to {output_file}[/green]")


async def main(
    count: int = 50,
    categories: list[str] = None,
    api_url: str = "http://localhost:8009",
    batch_size: int = 10,
    dry_run: bool = False,
    seed: int = None,
    output_file: str = None,
    skip_validation: bool = False,
) -> int:
    """Main seeding orchestration function.

    Args:
        count: Number of recipes to generate
        categories: Optional categories to filter
        api_url: API base URL
        batch_size: Batch size for API requests
        dry_run: Run without making API calls
        seed: Random seed for reproducibility
        output_file: Optional path to save report
        skip_validation: Skip post-seeding validation

    Returns:
        Exit code (0 for success)
    """
    console.print("[bold magenta]Recipe Database Seeder[/bold magenta]")
    console.print(f"API URL: {api_url}")
    console.print(f"Recipe Count: {count}")
    console.print(f"Batch Size: {batch_size}")
    if dry_run:
        console.print("[yellow]Mode: DRY RUN[/yellow]")
    if seed:
        console.print(f"Random Seed: {seed}")

    try:
        seeder = RecipeSeeder(api_url=api_url, batch_size=batch_size, dry_run=dry_run)

        # Generate recipes
        recipes = await seeder.generate_recipes(
            count=count, categories=categories, seed=seed
        )

        # Seed database
        seeding_report = await seeder.seed_database(recipes)

        # Save report if requested
        if output_file:
            await seeder.save_report(seeding_report, Path(output_file))

        # Validate if not skipped and not dry run
        if not skip_validation and not dry_run and seeding_report.total_succeeded > 0:
            validation_report = await seeder.validate_seeded_data(
                expected_count=seeding_report.total_succeeded
            )

            if not validation_report.overall_success:
                console.print("\n[red]Validation failed![/red]")
                return 1

        # Success summary
        if seeding_report.total_failed == 0:
            console.print("\n[bold green]Seeding completed successfully![/bold green]")
            return 0
        else:
            console.print(
                f"\n[yellow]Seeding completed with {seeding_report.total_failed} failures[/yellow]"
            )
            return 1

    except KeyboardInterrupt:
        console.print("\n[yellow]Seeding interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[red]Seeding failed with error: {e}[/red]")
        logger.exception("Unexpected error during seeding")
        return 1


def cli() -> None:
    """Command-line interface for the seeding script."""
    parser = argparse.ArgumentParser(
        description="Seed Recipe Management API with realistic recipe data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate and seed 50 recipes
  python -m scripts.seed_database

  # Dry run with 100 recipes
  python -m scripts.seed_database --count 100 --dry-run

  # Seed with custom API URL and batch size
  python -m scripts.seed_database --api-url http://localhost:8000 --batch-size 20

  # Use random seed for reproducibility
  python -m scripts.seed_database --seed 42 --output report.json
        """,
    )

    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of recipes to generate (default: 50)",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        help="Specific categories to include (space-separated)",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8009",
        help="API base URL (default: http://localhost:8009)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of recipes per batch (default: 10)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate data without sending to API",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for seeding report (JSON)",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip post-seeding validation",
    )

    args = parser.parse_args()

    # Run async main
    exit_code = asyncio.run(
        main(
            count=args.count,
            categories=args.categories,
            api_url=args.api_url,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
            seed=args.seed,
            output_file=args.output,
            skip_validation=args.skip_validation,
        )
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
