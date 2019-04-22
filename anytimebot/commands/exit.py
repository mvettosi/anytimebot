from discord.ext import commands

from anytimebot import persistence, utils
from anytimebot.persistence import AnytimeStatus
from anytimebot.utils import get_anytime


# Setup
def setup(bot):
    bot.add_command(exit)


# Command definition
@commands.command()
async def exit(context):
    anytime = await get_anytime(context)

    if anytime is None:
        # Handled by get_anytime
        return

    # Check player status
    anytime_player = next(
        (player for player in anytime['players'] if player['user_id'] == context.message.author.id),
        None
    )
    if anytime_player is None:
        await context.message.channel.send(f'You don\'t seem to be playing in this tournament!')
        return

    if anytime['status'] == AnytimeStatus.RECRUITING:
        persistence.remove_player(anytime.doc_id, context.message.author.id)
        participant_role = await utils.get_participant_role(context.message.guild, anytime.doc_id)
        await context.message.author.remove_roles(participant_role)
    else:
        await context.message.channel.send(f'It\'s too late to exit this tournament!')
