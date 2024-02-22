import aiobungie
import logging
import os
from chronicle.chronicle import Chronicle
from chronicle.cli import init_cli
from chronicle.web import init_web
from flask import Flask
from rich.logging import RichHandler


# Global variables. 😬
BUNGIE_API_KEY = os.getenv("BUNGIE_API_KEY")
PLAYER_CODE = os.getenv("PLAYER_CODE")
PLAYER_MEMBERSHIP_TYPE = aiobungie.MembershipType.PSN
PLAYER_NAME = os.getenv("PLAYER_NAME")


chronicle = Chronicle(BUNGIE_API_KEY, PLAYER_NAME, PLAYER_CODE, PLAYER_MEMBERSHIP_TYPE)


# Set-up logging.
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)


app = Flask("chronicle")
init_web(app, chronicle)


if __name__ == "__main__":
    init_cli(chronicle)
