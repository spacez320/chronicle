import aiobungie
import asyncio
import click
import datetime
import logging
import os
from flask import Flask
from chronicle.chronicle import Chronicle
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table


# Global variables. 😬
BUNGIE_API_KEY = os.getenv("BUNGIE_API_KEY")
PLAYER_CODE = os.getenv("PLAYER_CODE")
PLAYER_MEMBERSHIP_TYPE = aiobungie.MembershipType.PSN
PLAYER_NAME = os.getenv("PLAYER_NAME")


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--guardian-class",
    default="warlock",
    prompt="Guardian class",
    help="Guardian class to inspect.",
)
def history(guardian_class):
    """Gets various historical stats."""

    def _map_history(i):
        """Munge history output into something displayable."""
        return {
            "basic": i["basic"]["displayValue"],
            "pga": i["pga"]["displayValue"] if "pga" in i else "n/a",
            "statId": i["statId"],
        }

    chronicle = Chronicle(
        BUNGIE_API_KEY, PLAYER_NAME, PLAYER_CODE, PLAYER_MEMBERSHIP_TYPE
    )
    history = asyncio.run(chronicle.get_player_history(guardian_class))

    for activity_mode in history:
        create_table(
            list(map(_map_history, list(history[activity_mode]["allTime"].values()))),
            activity_mode.title(),
        )


@click.command()
@click.option(
    "--guardian-class",
    default="warlock",
    prompt="Guardian class",
    help="Guardian class to inspect.",
)
def weapons(guardian_class):
    """Gets weapons usage."""
    chronicle = Chronicle(
        BUNGIE_API_KEY, PLAYER_NAME, PLAYER_CODE, PLAYER_MEMBERSHIP_TYPE
    )
    weapons = asyncio.run(chronicle.get_weapons_by_class(guardian_class))
    create_table(weapons, "Weapons")


app = Flask(__name__)


@app.route("/")
def hello():
    return "<p>Hello!</p>"


def create_table(data, title, columns=None):
    """Prints a rich table from an arbitrary object or dictionary."""
    console = Console()
    table = Table(title=title)

    columns = (
        (
            data[0].keys()
            if type(data[0]) is dict
            else [k for k in dir(data[0]) if not k.startswith("_")]
        )
        if columns is None
        else columns
    )

    for column in columns:
        table.add_column(column)

    for dat in data:
        row = (
            list(dat.values())
            if type(dat) is dict
            else [str(getattr(dat, column)) for column in columns]
        )

        table.add_row(*[str(v) for v in row])

    console.print(table)


if __name__ == "__main__":
    # Set-up logging.
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(markup=True)],
    )

    cli.add_command(weapons)
    cli.add_command(history)
    cli()
