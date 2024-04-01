"""
Set-up for Chronicle CLI.
"""

import asyncio
import click

from chronicle.chronicle import Chronicle
from chronicle.util import create_rich_table


def init_cli(chronicle):
    """Sets-up the CLI."""

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
        history = asyncio.run(chronicle.get_player_history(guardian_class))

        for activity_mode in history:
            create_rich_table(
                Chronicle.player_history_activity_mode_to_list(history, activity_mode),
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
        weapons = asyncio.run(chronicle.get_weapons_by_class(guardian_class))
        create_rich_table(weapons, "Weapons")

    cli.add_command(weapons)
    cli.add_command(history)
    cli()
