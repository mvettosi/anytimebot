import discord
from discord.ext import commands
from anytimebot import config, persistence, tournament
from anytimebot.utils import is_power_of_two, get_participant_role, ticket_val, get_anytime_category_channel, \
    get_anytime_mod_role


# Setup
def setup(bot):
    bot.add_command(enterticket)


# Command definition
@commands.command()
async def enterticket(context, size=4):
    # Read and delete message
    message = context.message
    await message.delete()

    # Extract user, server, create direct message channel with the user
    user = message.author
    server = message.channel.guild

    # Check user's ticker
    if not config.has_ticket(server.name, user):
        await user.send(config.get_server_config(server.name, 'role_missing_message'))
    elif not is_power_of_two(size):
        await user.send(
            f'I\'sorry, but the size "{size}"" is not a power of two! Try with one of these: 2, 4, 8, 16, 32,'
            f' 64, 128....')
    elif persistence.is_username_used(user.name, server.id, size):
        await user.send(
            f'I\'sorry, but the user name "{user.name}" is already being used in the currently open Anytime '
            f'Tournament of size {size}. Change it and try again!')
    else:
        try:
            await add_player(context.bot, user, server, size)
        except Exception:
            await user.send('Sorry, something went wrong. Please try again and if it\'s not getting better, contact'
                            'a mod.')
            raise


# Helpers
async def add_player(client, user, server, size):
    # Register user and ask for decks
    request_id = persistence.add_to_waiting_list(server.id, user, size)
    await user.send(config.get_server_config(server.name, 'wait_for_decks_message'))

    def he_replied(message):
        return message.author == user and isinstance(message.channel, discord.abc.PrivateChannel)

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
            await user.send('At least one deck is needed to complete registration, please send at least one and try '
                            'again with `!submit`')
        else:
            # He's finished
            print(f'Submitting player: {user.name}')
            await confirm_player(request_id, server, user)
            break


async def confirm_player(request_id, server, user):
    # Transition user's request to accepted registration
    anytime_data = persistence.submit(request_id)

    if anytime_data is None:
        await user.send('I\'m sorry, there was a problem with your registration.'
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
            await discord_player.send(f'Hey, you don\'t seem to have a ticket anymore, so you were removed from'
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
    tournament_data = await tournament.create_tournament(anytime_data.doc_id, players)
    anytime_data = persistence.tournament_started(anytime_data.doc_id, tournament_data['id'])

    # Notify that tournament started
    msg = f'{participant_role.mention} the tournament has begun!' \
        f'\nThe tournament url is: {tournament_data["url"]}\n'
    for pairing in tournament_data['pairings']:
        discord_player = server.get_member(pairing['player'])
        discord_opponent = server.get_member(pairing['opponent'])
        msg += f'\n{discord_player.mention} you are up against {discord_opponent.mention}'
    msg += f'\n\nYou can submit your score on the website directly, or simply by typing:' \
        f'\n`!win <games you won>-<games you lost>' \
        f'\nFor example, to submit a 2-1 victory: `!win 2-1`' \
        f'\n\nGood luck everyone, and have fun!'
    await anytime_channel.send(msg)

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
