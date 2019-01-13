from anytimebot import persistence
from anytimebot import tournament


class AnytimeException(Exception):
    pass


async def add_to_awaiting_deck(server, user, size):
    await persistence.add_to_waiting_list(server, user, size)


async def add_to_anytime(server, user, size):
    raise AnytimeException(f'I\'m sorry, but you are already listed in another anytime tournament. '
                           f'If you wish to change tournament, drop from the previous one first!')
