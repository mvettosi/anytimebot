#!/usr/bin/env python3.7

from discord.ext.commands import Bot

TOKEN = 'NTIyMTA3MzcyODMxODk5NjQ5.DvGKPg.VdNfFHyTm76G6XgFaT9dl8rmxKc'
client = Bot(command_prefix='!')
servers = {}


class Anytime:
    partecipants = []

    def __init__(self, size):
        # TODO check size is power of 2
        self.size = size

    async def addParticipant(self, user, context):
        self.partecipants.append(user)
        if len(self.partecipants) == self.size:
            await self.startTournament(context)

    async def startTournament(self, context):
        await context.message.guild.create_text_channel('cool-channel')
        print(f'Starting a tournament with users: {self.partecipants}')


# Commands
@client.command(pass_context=True)
async def joinanytime(context, size = 4):
    await context.message.delete()
    user = context.message.author
    dm = await user.create_dm()
    if 'Ticket1' in [role.name for role in user.roles]:
        # TODO add to awaiting submission
        await dm.send(f'Hello {user}! Please provide your deck link using !submit <deckurl>')
    else:
        await dm.send(f'Hello {user}! I\'m sorry but you don\'t seem to have DLM tickets in the DLM Discord, '
                      f'please purchase some and try again')


@client.command(pass_context=True)
async def submit(context, deck):
    # TODO check if there is a server id
    # TODO check if he's awaiting submission
    # TODO validate deck
    # TODO move user to await others
    # TODO if full then start tournament
    print(f'DEBUG deck submitted: {deck}')



@client.command(pass_context=True)
async def winner(context, deck):
    # TODO check if there is a server id
    # TODO check user has running anytime
    # TODO check has running match
    # TODO if match was finals, set it on awaiting loser confirmation
    pass


# Start
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
