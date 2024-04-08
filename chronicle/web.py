"""
Web functions.
"""

import asyncio
from flask import render_template, request

from chronicle.chronicle import Chronicle
from chronicle.data import Data
from chronicle.util import create_html_error, create_html_table


def init_web(app, chronicle):
    @app.route("/")
    def hello():
        return render_template("index.html")

    @app.route("/history", methods=["POST"])
    def history():
        """Gets various historical stats."""
        template = ""

        try:
            player_name, player_code = request.form["id"].split("#")
            player_class = request.form["class"]
            player_membership_type = request.form["membership"]

            chronicle.init_player(player_name, player_code, player_membership_type)
            history = asyncio.run(chronicle.get_player_history(player_class))

            for activity_mode in history:
                template += create_html_table(
                    activity_mode.title(),
                    Data(
                        activity_mode,
                        Chronicle.player_history_activity_mode_to_list(
                            history, activity_mode
                        ),
                    ),
                )
        except Exception as e:
            template = create_html_error(e)

        return template

    @app.route("/weapons", methods=["POST"])
    def weapons():
        """Gets weapon usage."""
        template = ""

        try:
            player_name, player_code = request.form["id"].split("#")
            player_class = request.form["class"]
            player_membership_type = request.form["membership"]

            chronicle.init_player(player_name, player_code, player_membership_type)

            weapons = asyncio.run(chronicle.get_unique_weapon_history(player_class))
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

            template = create_html_table("Weapons", data)
        except Exception as e:
            template = create_html_error(e)

        return template
