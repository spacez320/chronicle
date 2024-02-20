"""
Web functions.
"""

from flask import render_template


def init_web(app, chronicle):
    @app.route("/")
    def hello():
        return render_template("index.html")
