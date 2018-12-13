#!/usr/bin/env python3

from discord.ext.commands import Bot
from random import randint

TOKEN = 'NTIyMTA3MzcyODMxODk5NjQ5.DvGKPg.VdNfFHyTm76G6XgFaT9dl8rmxKc'

client = Bot(command_prefix='!')


class Anytime:
    partecipants = []

    def __init__(self, size):
        self.size = size

    def addPartecipant(self, user):
        self.partecipants.append(user)
        if len(self.partecipants) == self.size:
            self.startTournament()

    def startTournament(self):
        print(f'Starting a tournament with users: {self.partecipants}')


openTournament = Anytime(2)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command(pass_context=True)
async def register(context):
    """
    - Get params
    - Delete message
    - PM user asking for deck link
    """
    await context.message.delete()
    user = context.message.author
    dm = await user.create_dm()
    await dm.send('Hello! Thanks for registering to an Anytime Tournament')


@client.command(pass_context=True)
async def submit(context, deck):
    print(f'deck submitted: {deck}')


@client.command(pass_context=True)
async def later(context):
    await context.message.guild.create_text_channel('cool-channel')


client.run(TOKEN)
