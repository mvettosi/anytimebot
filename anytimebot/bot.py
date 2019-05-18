#!/usr/bin/env python3.7
from pprint import pprint

from discord.ext.commands import Bot, MemberConverter
from anytimebot import config


# Instantiate bot and load extensions
client = Bot(command_prefix='!')
client.load_extension('anytimebot.commands.enterticket')
client.load_extension('anytimebot.commands.exit')
client.load_extension('anytimebot.commands.decklist')


@client.command()
async def test(ctx):
    for extention in client.extensions:
        print(extention)


@client.command()
async def reload(ctx):
    for extention in client.extensions:
        print(f'Reloading extension: {extention}')
        client.reload_extension(extention)


# Start
@client.event
async def on_ready():
    # client.loop.create_task(finalize_round())
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


# Functions
def run_bot():
    client.run(config.TOKEN)
