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


def create_html_table(data, title, columns=None):
    """Prints an HTML table from an arbitrary object or dictionary."""
    t = table()

    columns = (
        (
            data[0].keys()
            if type(data[0]) is dict
            else [k for k in dir(data[0]) if not k.startswith("_")]
        )
        if columns is None
        else columns
    )

    # Create the title row.
    t += tr(th(title, cls="dataTblTitle", colspan=len(columns)))

    # Create the header row.
    t_header = tr()
    for column in columns:
        t_header += th(column)
    t += t_header

    # Create the data rows.
    for dat in data:
        t_row = tr()
        if type(dat) is dict:
            t_row += [td(d) for d in dat.values()]
        else:
            t_row += [td(str(getattr(dat, column))) for column in columns]
        t += t_row

    return str(t)


def create_rich_table(data, title, columns=None):
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
