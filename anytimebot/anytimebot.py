#!/usr/bin/env python3.7

from discord.ext.commands import Bot
import asyncio

config = {
    'TOKEN': 'NTIyMTA3MzcyODMxODk5NjQ5.DvGKPg.VdNfFHyTm76G6XgFaT9dl8rmxKc',
    'servers': {
        'Testing': {
            'role': 'Ticket1',
            'error_message': 'You need the Ticket1 role in order to subscribe to a tournament. Ask a mod, it\'s free!'
        },
        'Duel Links Meta': {
            'role': 'Ticket1',
            'error_message': 'Hello! Thanks for your interest in DLM anytime tournaments! Unfortunately you don\'t seem'
                             'to have any meta ticket left, please purchase some in #ticket-channel and try again.'
        }
    }
}
client = Bot(command_prefix='!')


@client.command(pass_context=True)
async def enterticket(context, size = 4):
    message = context.message
    await message.delete()
    user = message.author
    dm = await user.create_dm()
    guild = message.channel.guild
    server_config = config['servers'][guild.name]
    if server_config and server_config['role'] not in [role.name for role in user.roles]:
        await dm.send(server_config['error_message'])
    else:
        # TODO add to awaiting submission
        await dm.send(f'Hello {user}! Please provide your deck link using !submit <deckurl>')


@client.command(pass_context=True)
async def submit(context, deck):
    # TODO check if there is a server id
    # TODO check if he's awaiting submission
    # TODO validate deck
    # TODO move user to await others
    # TODO if full then start tournament
    print(f'DEBUG deck submitted: {deck}')


@client.command(pass_context=True)
async def decklist(context, username):
    # TODO check source channel
    # TODO check if sender is anytime mod or username
    # TODO retrieve decklist and send
    pass


@client.command(pass_context=True)
async def finalize(context):
    # TODO check source channel
    # TODO check if tournament is finished
    # TODO check if user is anytime mod
    # TODO finalize tournament
    pass


@client.command(pass_context=True)
async def mod(context):
    # TODO check channel
    # TODO update last_updated for the tournament
    # TODO retrieve list of online mods
    # TODO select one at random
    # TODO ping him
    pass


async def finalize_round():
    while True:
        await asyncio.sleep(300)
        # TODO fetch all running tournaments
        # TODO for each one
            # TODO if enough time has passed since last_update
                # TODO finalize tournament


# Start
@client.event
async def on_ready():
    client.loop.create_task(finalize_round())
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(config['TOKEN'])
