import asyncio
import aiobungie
import os
import pprint


BUNGIE_API_KEY = os.getenv("BUNGIE_API_KEY")
PLAYER_NAME = "spacez320"
PLAYER_CODE = 3465
PLAYER_MEMBERSHIP_TYPE = aiobungie.MembershipType.PSN


async def main():
    client = aiobungie.Client(BUNGIE_API_KEY)

    async with client.rest:
        player = (
            await client.fetch_player(PLAYER_NAME, PLAYER_CODE, PLAYER_MEMBERSHIP_TYPE)
        )[0]
        player_profile = await client.fetch_profile(
            player.id,
            PLAYER_MEMBERSHIP_TYPE,
            components=[aiobungie.ComponentType.CHARACTERS],
        )
        pprint.pp(player_profile.characters.keys(), indent=1)

        for character_id in player_profile.characters.keys():
            character = await client.fetch_character(
                player.id,
                PLAYER_MEMBERSHIP_TYPE,
                character_id,
                components=[aiobungie.ComponentType.CHARACTERS],
                # player.type,
            )
            print(character)


asyncio.run(main())
