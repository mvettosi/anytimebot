#!/usr/bin/env python3.7

from discord.ext.commands import Bot
import discord

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
    dm = await get_dm(user)

    # Check user's ticker
    if not config.has_ticket(server.name, user):
        await dm.send(config.get_server_config(server.name, 'role_missing_message'))
    elif not is_power_of_two(size):
        await dm.send(f'I\'sorry, but the size "{size}"" is not a power of two! Try with one of these: 2, 4, 8, 16, 32,'
                      f' 64, 128....')
    elif persistence.is_username_used(user.name, server.id, size):
        await dm.send(f'I\'sorry, but the user name "{user.name}" is already being used in the currently open Anytime '
                      f'Tournament of size {size}. Change it and try again!')
    else:
        await add_player(user, server, size)


@client.command(pass_context=True)
async def test(context):
    message = context.message
    user = message.author
    ticket_to_remove = None
    for role in user.roles:
        if 'Ticket' in role.name and (
                ticket_to_remove is None or ticket_val(ticket_to_remove) < ticket_val(role)
        ):
            ticket_to_remove = role
    await user.remove_roles(ticket_to_remove)


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


def is_power_of_two(number):
    return ((number & (number - 1)) == 0) and number > 0


async def add_player(user, server, size):
    # Register user and ask for decks
    request_id = persistence.add_to_waiting_list(server.id, user, size)
    dm = await get_dm(user)
    await dm.send(config.get_server_config(server.name, 'wait_for_decks_message'))

    def he_replied(message):
        return message.author == user and message.channel == dm

    request = None
    while True:
        reply = await client.wait_for('message', check=he_replied)

        if not persistence.is_join_request_still_valid(request_id):
            # While waiting, the user performed the command again and subscribed to a new tournament format:
            # We'll let that coroutine to handle it, and this will terminate here
            print('submission invalidated: terminating')
            break

        if reply.content != '!submit':
            # Add deck
            urls = [attachment.url for attachment in reply.attachments]
            request = persistence.add_deck(request_id, reply.content, urls)
        elif request is None:
            # !submit used, but no decks submitted yet
            await dm.send('At least one deck is needed to complete registration, please send at least one and try '
                          'again with `!submit`')
        else:
            # He's finished
            print(f'Submitting player: {user.name}')
            await confirm_player(request_id, server, user)
            break


async def confirm_player(request_id, server, user):
    dm = await get_dm(user)

    # Transition user's request to accepted registration
    anytime_data = persistence.submit(request_id)

    if anytime_data is None:
        await dm.send('I\'m sorry, there was a problem with your registration.'
                      'Please try again by typing `!enterticket`')
        return
    elif len(anytime_data['players']) == 1:
        # First submitted player: create channel
        anytime_channel = await create_anytime_channel(server, anytime_data.doc_id)
        await anytime_channel.send(f'Hi everyone! This is the channel we\'ll use for the '
                             f'Anytime Tournament #{anytime_data.doc_id}')
        anytime_data = persistence.add_channel_id(anytime_channel.id, anytime_data.doc_id)
    else:
        # Retrieve anytime channel
        anytime_channel = server.get_channel(anytime_data['channel_id'])

    # Notify user in the anytime channel
    participant_role = await get_participant_role(server, anytime_data.doc_id)
    await user.add_roles(participant_role)
    await anytime_channel.send(f'{user.mention} joins the battle!')

    # Check that everyone still has a ticket, exit the ones that does not
    for player in anytime_data['players']:
        discord_player = server.get_member(player['user_id'])
        if not config.has_ticket(server.name, discord_player):
            await discord_player.remove_roles(participant_role)
            persistence.remove_player(anytime_data.doc_id, player['user_id'])
            await get_dm(discord_player).send(f'Hey, you don\'t seem to have a ticket anymore, so you were removed from'
                                              f' the Anytime #{anytime_data.doc_id}. If you think this is an error,'
                                              f'please contact an Anytime Mod!')

    # Did the anytime just got full?
    if len(anytime_data['players']) == anytime_data['size']:
        await start_tournament(server, anytime_data)


async def start_tournament(server, anytime_data):
    anytime_channel = server.get_channel(anytime_data['channel_id'])
    participant_role = await get_participant_role(server, anytime_data.doc_id)
    players = anytime_data['players']

    # Create tournament on challonge
    challonge_tournament = await tournament.create_tournament(anytime_data.doc_id, players)
    anytime_data = persistence.tournament_started(anytime_data.doc_id, challonge_tournament.id)

    # Notify that tournament started
    await anytime_channel.send(f'{participant_role.mention} the tournament has begun!\n'
                               f'The challonge url is: {challonge_tournament.full_challonge_url}\n\n'
                               f'You can submit your score on the website directly, or simply type:\n'
                               f'`!win <games you won> <games you lost>\n'
                               f'For example, to submit a 2-1 victory: `!win 2 1`\n\n'
                               f'Good luck everyone, and have fun!')

    # Remove tickets
    for player in anytime_data['players']:
        participant = server.get_member(player['user_id'])
        ticket_to_remove = None
        for role in participant.roles:
            if 'Ticket' in role.name and (
                    ticket_to_remove is None or ticket_val(ticket_to_remove) < ticket_val(role)
            ):
                ticket_to_remove = role
        await participant.remove_roles(ticket_to_remove)


async def create_anytime_channel(server, anytime_id):
    category = get_anytime_category_channel(server)
    participant_role = await get_participant_role(server, anytime_id)
    anytime_mod_role = get_anytime_mod_role(server)
    overwrites = {
        server.default_role: discord.PermissionOverwrite(read_messages=False),
        server.me: discord.PermissionOverwrite(read_messages=True),
        participant_role: discord.PermissionOverwrite(read_messages=True),
        anytime_mod_role: discord.PermissionOverwrite(read_messages=True)
    }
    channel = await server.create_text_channel(
        f'anytime-{anytime_id}',
        overwrites=overwrites,
        category=category
    )
    return channel


async def get_dm(user):
    result = user.dm_channel
    if result is None:
        result = await user.create_dm()
    return result


def get_anytime_category_channel(guild):
    for cat in guild.categories:
        if cat.name == 'anytimes':
            return cat


async def get_participant_role(guild, anytime_id):
    anytime_role_name = f'Anytime-{anytime_id}'
    anytime_role = None
    for role in guild.roles:
        if role.name == anytime_role_name:
            anytime_role = role
    if anytime_role is None:
        anytime_role = await guild.create_role(name=anytime_role_name, mentionable=True)
    return anytime_role


def get_anytime_mod_role(guild):
    for role in guild.roles:
        if role.name == 'Anytime Mod':
            return role


def ticket_val(role):
    return int(role.name.replace('Ticket ', ''))
