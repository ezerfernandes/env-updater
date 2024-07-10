"""Env updater."""

import os
import re
from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.table import Table

app = typer.Typer()


@app.command()
def findenvs(
    parent: Annotated[
        str,
        typer.Option(
            help="Parent directory to search for .env files",
        ),
    ] = ".",
    dirpattern: Annotated[
        str,
        typer.Option(
            help="Sub-directory pattern to search for .env files",
        ),
    ] = "*",
    suffix: Annotated[
        str,
        typer.Option(
            help="Filename pattern to search for .env files",
        ),
    ] = ".env",
) -> None:
    """Find .env files in sub-directories of the current directory."""
    for root, _, files in os.walk(parent):
        if dirpattern != "*" and not re.search(dirpattern, root):
            continue
        for file in files:
            if file.endswith(suffix):
                print(Path(root) / file)  # noqa: T201


@app.command()
def getvalues(
    variable: str,
    parent: Annotated[
        str,
        typer.Option(
            help="Parent directory to search for .env files",
        ),
    ] = ".",
    dirpattern: Annotated[
        str,
        typer.Option(
            help="Sub-directory pattern to search for .env files",
        ),
    ] = "*",
    suffix: Annotated[
        str,
        typer.Option(
            help="Filename pattern to search for .env files",
        ),
    ] = ".env",
) -> None:
    """Search for .env files and print the specified variable's values."""
    variable_values = {}
    varval_pattern = re.compile(rf"^{re.escape(variable)}\s*=\s*(.*)$")

    for root, _, files in os.walk(parent):
        if dirpattern != "*" and not re.search(dirpattern, root):
            continue
        root_path = Path(root)
        for file in files:
            if file.endswith(suffix):
                filepath = root_path / file
                with Path.open(filepath) as f:
                    for line in f:
                        match = varval_pattern.match(line)
                        if match:
                            value = match.group(1).split("#")[0].strip()
                            if value not in variable_values:
                                variable_values[value] = []
                            variable_values[value].append(str(filepath))

    if variable_values:
        table = Table(title=f"Values for variable: [bold cyan]{variable}[/bold cyan]")

        table.add_column("Value", style="green")
        table.add_column("Files", style="magenta")

        for value, filepaths in variable_values.items():
            table.add_row(value, "\n".join(filepaths))

        print(table)
    else:
        print(f"[bold red]No values found for variable: {variable}[/bold red]")


if __name__ == "__main__":
    app()
