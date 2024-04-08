import aiobungie
import asyncio
import datetime
from structlog import get_logger


logger = get_logger()


class Guardian:
    """Represents a player Guardian."""

    def __init__(self, name, code, membership_type, api_client):
        self.client = api_client
        self.name = name
        self.code = code
        self.membership_type = Guardian.get_membership_type_from_str(membership_type)

        logger.debug(
            "Building clients",
            name=self.name,
            code=self.code,
            membership=self.membership_type,
        )

        self.player = asyncio.run(self._get_player())
        self.player_profile = asyncio.run(self._get_player_profile())

    def __repr__(self):
        return "Guardian({})".format(
            ",".join(
                [
                    f"{k}={v}"
                    for k, v in {
                        "Name": self.name,
                        "Code": self.code,
                        "Membership": self.membership_type,
                    }.items()
                ]
            )
        )

    @staticmethod
    def get_class_from_str(guardian_class):
        """Map guardian class plain text to aiobungie class object."""
        match guardian_class:
            case "hunter":
                return aiobungie.Class.HUNTER
            case "titan":
                return aiobungie.Class.TITAN
            case "warlock":
                return aiobungie.Class.WARLOCK

    @staticmethod
    def get_membership_type_from_str(membership_type):
        match membership_type:
            case "psn":
                return aiobungie.MembershipType.PSN
            case "steam":
                return aiobungie.MembershipType.STEAM
            case "xbox":
                return aiobungie.MembershipType.XBOX

    async def _get_player(self):
        """Fetch a player."""
        logger.debug(
            "Fetching membership",
            name=self.name,
            code=self.code,
            membership_type=self.membership_type,
        )

        async with self.client.rest:
            player = await self.client.fetch_membership(
                self.name, self.code, self.membership_type
            )

        return player[0]

    async def _get_player_profile(self):
        """Fetch a player profile."""
        async with self.client.rest:
            logger.debug(
                "Fetching player profile",
                name=self.name,
                code=self.code,
                membership_type=self.membership_type,
            )

            player_profile = await self.client.fetch_profile(
                self.player.id,
                self.membership_type,
                components=[
                    aiobungie.ComponentType.CHARACTERS,
                    aiobungie.ComponentType.PROFILE_INVENTORIES,
                ],
            )

        return player_profile


class Chronicle:
    """Main Bungie API manager."""

    def __init__(self, api_key):
        self.client = aiobungie.Client(api_key)
        self.rest_client = aiobungie.RESTClient(api_key)

    def init_player(self, player_name, player_code, player_membership_type):
        """Configures a player Guardian to make requests for."""
        self.player = Guardian(
            player_name, player_code, player_membership_type, self.client
        )

        logger.debug("Player character initialized", player=self.player)

    @staticmethod
    def player_history_activity_mode_to_list(history, activity_mode):
        """Converts the "fetch_historical_stats" output to a list."""

        def _map_history(i):
            """Munge history output into something displayable."""
            return {
                "basic": i["basic"]["displayValue"],
                "pga": i["pga"]["displayValue"] if "pga" in i else "n/a",
                "statId": i["statId"],
            }

        return list(map(_map_history, list(history[activity_mode]["allTime"].values())))

    async def get_player_history(self, guardian_class):
        """Fetch historical data for a player."""
        character = next(
            filter(
                lambda character: character.class_type
                == Guardian.get_class_from_str(guardian_class),
                self.player.player_profile.characters.values(),
            )
        )

        async with self.rest_client:
            history = await self.rest_client.fetch_historical_stats(
                character.id,
                self.player.player.id,
                self.player.membership_type,
                day_start=datetime.datetime.min,
                day_end=datetime.datetime.max,
                groups=[aiobungie.internal.enums.GroupType.GENERAL],
                modes=[aiobungie.internal.enums.GameMode.ALLPVE],
            )

        return history

    async def get_unique_weapon_history(self, guardian_class):
        """Fetch weapon data for a specific player class."""
        character = next(
            filter(
                lambda character: character.class_type
                == Guardian.get_class_from_str(guardian_class),
                self.player.player_profile.characters.values(),
            )
        )

        # Look-up unique weapon stats.
        async with self.client.rest:
            weapons = await self.client.fetch_unique_weapon_history(
                self.player.player.id, character.id, self.player.membership_type
            )

        return weapons

    async def get_weapons_from_reference_ids(self, reference_ids):
        """Fetches weapon names from a list of weapon reference ids."""
        weapons = []

        async with self.rest_client:
            for r in reference_ids:
                weapon_r = await self.rest_client.fetch_inventory_item(r)
                weapons.append(weapon_r["displayProperties"]["name"])

        return weapons
