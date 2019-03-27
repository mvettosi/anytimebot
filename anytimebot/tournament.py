import asyncio
import challonge

from anytimebot import config


async def create_tournament(tournament_id, players):
    my_user = await challonge.get_user(config.CHALLONGE_USERNAME, config.CHALLONGE_API_KEY)
    new_tournament = await my_user.create_tournament(
        name=f'Anytime Tournament #{tournament_id}',
        url=f'anytime_{tournament_id}',
        # open_signup=True,
        # signup_cap=len(players),
        check_in_duration=10
    )

    # for player in players:
    #     await new_tournament.add_participant(player['name'])
    john = await new_tournament.add_participant('john')
    bob = await new_tournament.add_participant('bob')
    steve = await new_tournament.add_participant('steve')
    franck = await new_tournament.add_participant('franck')

    await new_tournament.start()

    print(f'DEBUG: {new_tournament.full_challonge_url}')
