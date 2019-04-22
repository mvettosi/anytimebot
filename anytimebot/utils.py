import re

from anytimebot import persistence


def is_power_of_two(number):
    return ((number & (number - 1)) == 0) and number > 0


async def get_anytime(context):
    channel = context.message.channel
    if re.match(r'^anytime-\d+$', channel.name):
        id_string = channel.name.replace('anytime-', '')
        id = int(id_string)
        anytime_data = persistence.get_anytime(id)
        if anytime_data is None:
            # await context.message.delete()
            await context.message.send('This doesn\'t seem to be an anytime channel!')
        else:
            return anytime_data


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


async def send_decks(destination, decks):
    pass
