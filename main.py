import aiobungie
import asyncio
import click
import datetime
import logging
import os
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.pretty import pprint


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

    chronicle = Chronicle(PLAYER_NAME, PLAYER_CODE, PLAYER_MEMBERSHIP_TYPE)
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
    chronicle = Chronicle(PLAYER_NAME, PLAYER_CODE, PLAYER_MEMBERSHIP_TYPE)
    weapons = asyncio.run(chronicle.get_weapons_by_class(guardian_class))
    create_table(weapons, "Weapons")


class Chronicle:
    def __init__(self, name, code, membership_type):
        self.code = code
        self.membership_type = membership_type
        self.name = name

        self.client = aiobungie.Client(BUNGIE_API_KEY)
        self.rest_client = aiobungie.RESTClient(BUNGIE_API_KEY)
        self.player = asyncio.run(self._get_player())
        self.player_profile = asyncio.run(self._get_player_profile())

    @staticmethod
    def get_class_from_str(guardian_class):
        """Map guardian class plain text to aiobungie class object."""
        match guardian_class:
            case "hunter":
                return aiobungie.Class.HUNTER
            case "titan":
                return aiobungie.Class.TITAN
            case "warlock":
                return aiobungie.Class.WARLOCK

    async def _get_player(self):
        """Fetch a player."""
        async with self.client.rest:
            player = (
                await self.client.fetch_player(
                    self.name, self.code, self.membership_type
                )
            )[0]

        return player

    async def _get_player_profile(self):
        """Fetch a player profile."""
        async with self.client.rest:
            player_profile = await self.client.fetch_profile(
                self.player.id,
                self.membership_type,
                components=[aiobungie.ComponentType.CHARACTERS],
            )

        return player_profile

    async def get_player_history(self, guardian_class):
        """Fetch historical data for a player."""
        character = next(
            filter(
                lambda character: character.class_type
                == Chronicle.get_class_from_str(guardian_class),
                self.player_profile.characters.values(),
            )
        )

        async with self.rest_client:
            history = await self.rest_client.fetch_historical_stats(
                character.id,
                self.player.id,
                self.membership_type,
                day_start=datetime.datetime.min,
                day_end=datetime.datetime.max,
                groups=[aiobungie.internal.enums.GroupType.GENERAL],
                modes=[aiobungie.internal.enums.GameMode.ALLPVE],
            )

        return history

    async def get_weapons_by_class(self, guardian_class):
        """Fetch weapon data for a specific player class."""
        character = next(
            filter(
                lambda character: character.class_type
                == Chronicle.get_class_from_str(guardian_class),
                self.player_profile.characters.values(),
            )
        )

        async with self.client.rest:
            weapons = await self.client.fetch_unique_weapon_history(
                self.player.id, character.id, self.membership_type
            )

        return weapons


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
