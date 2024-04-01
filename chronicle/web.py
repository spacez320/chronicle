"""
Web functions.
"""

import asyncio
from flask import render_template, request

from chronicle.chronicle import Chronicle
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
                    Chronicle.player_history_activity_mode_to_list(
                        history, activity_mode
                    ),
                    activity_mode.title(),
                )
        except Exception as e:
            template = create_html_error(e)

        return template

    @app.route("/weapons", methods=["POST"])
    def weapons():
        """Gets weapon usage."""
        player_name, player_code = request.form["id"].split("#")
        player_class = request.form["class"]
        player_membership_type = request.form["membership"]

        chronicle.init_player(player_name, player_code, player_membership_type)

        return create_html_table(
            asyncio.run(chronicle.get_weapons_by_class(player_class)), "Weapons"
        )
