"""
Set-up for Chronicle CLI.
"""

import asyncio
import click
import os

from chronicle.chronicle import Chronicle
from chronicle.data import Data
from chronicle.util import create_rich_table


# Retrieve configured player information from the environment.
PLAYER_CODE = os.getenv("PLAYER_CODE")
PLAYER_MEMBERSHIP_TYPE = os.getenv("PLAYER_MEMBERSHIP_TYPE")
PLAYER_NAME = os.getenv("PLAYER_NAME")


def init_cli(chronicle):
    """Sets-up the CLI."""

    @click.group()
    @click.pass_context
    def cli(ctx):
        # Initialize the player character.
        chronicle.init_player(PLAYER_NAME, PLAYER_CODE, PLAYER_MEMBERSHIP_TYPE)

    @click.command()
    @click.option(
        "--guardian-class",
        default="warlock",
        prompt="Guardian class",
        help="Guardian class to inspect.",
    )
    def history(guardian_class):
        """Gets various historical stats."""
        history = asyncio.run(chronicle.get_player_history(guardian_class))

        for activity_mode in history:
            create_rich_table(
                activity_mode.title(),
                Data(
                    activity_mode,
                    Chronicle.player_history_activity_mode_to_list(
                        history, activity_mode
                    ),
                ),
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
        weapons = asyncio.run(chronicle.get_unique_weapon_history(guardian_class))
        weapon_names = asyncio.run(
            chronicle.get_weapons_from_reference_ids(
                [weapon.reference_id for weapon in weapons]
            )
        )

        data = Data(
            "weapons",
            weapons,
            columns=["kills", "precision_kills"],
        )
        data.join([{"name": weapon_name} for weapon_name in weapon_names])
        data.join(
            [
                {"precision_kills_percentage": weapon.precision_kills_percentage[0]}
                for weapon in weapons
            ]
        )

        create_rich_table("Unique Weapons", data)

    cli.add_command(weapons)
    cli.add_command(history)
    cli()
