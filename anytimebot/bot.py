#!/usr/bin/env python3.7
import pprint

from discord import ChannelType
from discord.ext.commands import Bot
from anytimebot import config, tournament
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
        request_id = persistence.add_to_waiting_list(server.id, user.id, size)
        await dm.send(config.get_server_config(server, 'wait_for_decks_message'))

        def he_replied(reply):
            return reply.author == user and reply.channel == dm

        while True:
            reply = await client.wait_for('message', check=he_replied)
            if not persistence.is_join_request_still_valid(request_id):
                # While waiting, the user performed the command again and subscribed to a new tournament format:
                # We'll let that coroutine to handle it, and this will terminate here
                print('submission invalidated: terminating')
                break
            if reply.content == '!submit':
                print('Submitting!')
                anytime_data = persistence.submit(request_id)
                if anytime_data is None:
                    await dm.send('I\'m sorry, there was a problem with your registration.'
                                  'Please try again by typing `!enterticket`')
                else:
                    if len(anytime_data['players']) == anytime_data['size']:
                        players = anytime_data['players']
                        for player in players:
                            player['name'] = server.get_member(player['user_id']).name
                        await tournament.create_tournament(anytime_data.doc_id, players)
                break
            else:
                urls = [attachment.url for attachment in reply.attachments]
                persistence.add_deck(request_id, reply.content, urls)


@client.command(pass_context=True)
async def mytest(context, size=4):
    await tournament.create_tournament(53, [])


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
