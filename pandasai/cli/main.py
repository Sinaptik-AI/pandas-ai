import os
import re

import click

from pandasai import DatasetLoader
from pandasai.data_loader.semantic_layer_schema import (
    SemanticLayerSchema,
    Source,
    SQLConnectionConfig,
)
from pandasai.helpers.path import find_project_root


def get_validated_dataset_path(path: str) -> tuple[str, str]:
    """Validate and split a dataset path into organization and dataset names."""
    if not path or "/" not in path:
        raise ValueError("Path must be in format: organization/dataset")

    org_name, dataset_name = path.split("/", 1)

    # Validate names (lowercase with hyphens)
    pattern = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    if not pattern.match(org_name):
        raise ValueError("Organization name must be lowercase with hyphens")
    if not pattern.match(dataset_name):
        raise ValueError("Dataset name must be lowercase with hyphens")

    return org_name, dataset_name


@click.group()
def cli():
    """🐼 PandaAI CLI - Manage your datasets with ease"""
    pass


@cli.group()
def dataset():
    """📊 Dataset management commands"""
    pass


@dataset.command()
def create():
    """🎨 Create a new dataset through a guided process"""
    click.echo("🚀 Let's create a new dataset!\n")

    # Get organization and dataset name
    while True:
        path = click.prompt("📁 Enter the dataset path (format: organization/dataset)")
        try:
            org_name, dataset_name = get_validated_dataset_path(path)
            break
        except ValueError as e:
            click.echo(f"❌ Error: {str(e)}")

    dataset_directory = os.path.join(
        find_project_root(), "datasets", org_name, dataset_name
    )

    # Check if dataset already exists
    if os.path.exists(dataset_directory):
        schema_path = os.path.join(dataset_directory, "schema.yaml")
        if os.path.exists(schema_path):
            click.echo(f"❌ Error: Dataset already exists at path: {path}")
            return

    # Get dataset metadata
    name = click.prompt("📝 Enter dataset name", default=dataset_name)
    description = click.prompt("📋 Enter dataset description", default="")

    # Get source configuration
    source_type = click.prompt(
        "🔌 Enter source type",
        type=click.Choice(["mysql", "postgres"]),
        default="mysql",
    )

    table_name = click.prompt("📦 Enter table name")

    # Build connection configuration
    connection_config = {
        "host": click.prompt("🌐 Enter host", default="localhost"),
        "port": click.prompt("🔍 Enter port", type=int),
        "database": click.prompt("💾 Enter database name"),
        "user": click.prompt("👤 Enter username"),
        "password": click.prompt("🔑 Enter password", hide_input=True),
    }

    # Create source configuration
    source = {
        "type": source_type,
        "table": table_name,
        "connection": SQLConnectionConfig(**connection_config),
    }

    # Create schema
    schema = SemanticLayerSchema(
        name=name, description=description, source=Source(**source)
    )

    # Create directory and save schema
    os.makedirs(dataset_directory, exist_ok=True)
    schema_path = os.path.join(dataset_directory, "schema.yaml")

    with open(schema_path, "w") as yml_file:
        yml_file.write(schema.to_yaml())

    click.echo(f"\n✨ Dataset created successfully at: {dataset_directory}")


@cli.command()
@click.argument("dataset_path")
def pull(dataset_path):
    """📥 Pull a dataset from a remote source"""
    try:
        click.echo(f"🔄 Pulling dataset from: {dataset_path}")
        dataset_loader = DatasetLoader()
        df = dataset_loader.load(dataset_path)
        df.pull()
        click.echo(f"\n✨ Dataset successfully pulled from path: {dataset_path}")
    except Exception as e:
        click.echo(f"❌ Error pulling dataset: {str(e)}")


@cli.command()
@click.argument("dataset_path")
def push(dataset_path):
    """📤 Push a dataset to a remote source"""
    try:
        click.echo(f"🔄 Pushing dataset to: {dataset_path}")
        dataset_loader = DatasetLoader()
        df = dataset_loader.load(dataset_path)
        df.push()
        click.echo(f"\n✨ Dataset successfully pushed to path: {dataset_path}")
    except Exception as e:
        click.echo(f"❌ Error pushing dataset: {str(e)}")


if __name__ == "__main__":
    cli()
