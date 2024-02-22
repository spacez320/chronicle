"""
Set-up for Chronicle CLI.
"""

import asyncio
import click

from chronicle.util import create_table


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

        def _map_history(i):
            """Munge history output into something displayable."""
            return {
                "basic": i["basic"]["displayValue"],
                "pga": i["pga"]["displayValue"] if "pga" in i else "n/a",
                "statId": i["statId"],
            }

        history = asyncio.run(chronicle.get_player_history(guardian_class))

        for activity_mode in history:
            create_table(
                list(
                    map(_map_history, list(history[activity_mode]["allTime"].values()))
                ),
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
        create_table(weapons, "Weapons")

    cli.add_command(weapons)
    cli.add_command(history)
    cli()
