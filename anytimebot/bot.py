#!/usr/bin/env python3.7

from discord.ext.commands import Bot
from anytimebot import config
from anytimebot import persistence


client = Bot(command_prefix='!')


@client.command(pass_context=True)
async def enterticket(context, size=4):
    # Read and delete message
    message = context.message
    await message.delete()

    # Extract user, server, create direct message channel with the user
    user = message.author
    server = message.channel.guild
    dm = await user.create_dm()

    # Check user's ticker
    if config.misses_role(server, user):
        await dm.send(config.get_server_config(server, 'role_missing_message'))
    else:
        persistence.add_to_waiting_list(server.id, user.id, size)
        await dm.send(config.get_server_config(server, 'wait_for_decks_message'))


# async def finalize_round():
#     while True:
#         await asyncio.sleep(300)
# TODO fetch all running tournaments
# TODO for each one
# TODO if enough time has passed since last_update
# TODO finalize tournament


# Start
@client.event
async def on_ready():
    # client.loop.create_task(finalize_round())
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def run_bot():
    client.run(config.TOKEN)
