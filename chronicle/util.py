"""
Utility functions.
"""

from rich.console import Console
from rich.table import Table


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
