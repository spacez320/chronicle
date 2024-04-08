"""
Utility functions.
"""

import traceback

from dominate.tags import code, p, table, td, th, tr
from rich.console import Console
from rich.table import Table


def create_html_error(error):
    """Prints a Python Error or Exception."""
    return str(p("Sorry, there was an error. 😞")) + str(
        code(
            "".join(traceback.format_tb(error.__traceback__)) + str(error), cls="error"
        )
    )


def create_html_table(title, data):
    """Prints an HTML table from arbitrary objects or dictionaries."""
    t = table()

    t += tr(th(title, cls="dataTblTitle", colspan=len(data.columns)))

    t_header = tr()
    for column in data.columns:
        t_header += th(column)
    t += t_header

    for dat in data:
        t_row = tr()
        t_row += [td(str(d)) for d in dat]
        t += t_row

    return str(t)


def create_rich_table(title, data):
    """Prints a rich table from arbitrary objects or dictionaries."""
    console = Console()
    table = Table(title=title)

    for column in data.columns:
        table.add_column(column)

    for dat in data:
        table.add_row(*[str(d) for d in dat])

    console.print(table)
