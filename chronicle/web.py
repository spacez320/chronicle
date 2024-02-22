"""
Web functions.
"""

from flask import render_template


def init_web(app, chronicle):
    @app.route("/")
    def hello():
        return render_template("index.html")

    @app.route("/history")
    def history():
        return "<div>History called!</div>"

    @app.route("/weapons")
    def weapons():
        return "<div>Weapons called!</div>"
