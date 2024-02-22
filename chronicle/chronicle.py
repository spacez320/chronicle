import aiobungie
import asyncio
import datetime


class Chronicle:
    def __init__(self, api_key, name, code, membership_type):
        self.api_key = api_key
        self.code = code
        self.membership_type = membership_type
        self.name = name

        self.client = aiobungie.Client(api_key)
        self.rest_client = aiobungie.RESTClient(api_key)
        self.player = asyncio.run(self._get_player())
        self.player_profile = asyncio.run(self._get_player_profile())

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

    async def _get_player(self):
        """Fetch a player."""
        async with self.client.rest:
            player = (
                await self.client.fetch_player(
                    self.name, self.code, self.membership_type
                )
            )[0]

        return player

    async def _get_player_profile(self):
        """Fetch a player profile."""
        async with self.client.rest:
            player_profile = await self.client.fetch_profile(
                self.player.id,
                self.membership_type,
                components=[aiobungie.ComponentType.CHARACTERS],
            )

        return player_profile

    async def get_player_history(self, guardian_class):
        """Fetch historical data for a player."""
        character = next(
            filter(
                lambda character: character.class_type
                == Chronicle.get_class_from_str(guardian_class),
                self.player_profile.characters.values(),
            )
        )

        async with self.rest_client:
            history = await self.rest_client.fetch_historical_stats(
                character.id,
                self.player.id,
                self.membership_type,
                day_start=datetime.datetime.min,
                day_end=datetime.datetime.max,
                groups=[aiobungie.internal.enums.GroupType.GENERAL],
                modes=[aiobungie.internal.enums.GameMode.ALLPVE],
            )

        return history

    async def get_weapons_by_class(self, guardian_class):
        """Fetch weapon data for a specific player class."""
        character = next(
            filter(
                lambda character: character.class_type
                == Chronicle.get_class_from_str(guardian_class),
                self.player_profile.characters.values(),
            )
        )

        async with self.client.rest:
            weapons = await self.client.fetch_unique_weapon_history(
                self.player.id, character.id, self.membership_type
            )

        return weapons
