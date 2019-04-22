from discord.ext import commands
from discord.ext.commands import MemberConverter
from anytimebot.utils import get_anytime, get_anytime_mod_role, send_decks


# Setup
def setup(bot):
    bot.add_command(decklist)


# Command definition
@commands.command()
async def decklist(context, mention):
    anytime = await get_anytime(context)

    if anytime is None:
        # Handled by get_anytime
        return

    # Check mod status
    mod_role = get_anytime_mod_role(context.message.guild)
    if mod_role not in context.message.author.roles:
        await context.message.channel.send(f'Sorry, only anytime mods can visualize decklists!')
        return

    # Check argument
    if mention is None:
        await context.message.channel.send(f'Please mention the player you want to see the decklists of')
        return

    # Retrieve target player
    discord_player = await MemberConverter().convert(context, mention)
    anytime_player = next((player for player in anytime['players'] if player['user_id'] == discord_player.id), None)

    # Check player participates in tournament
    if anytime_player is None:
        await context.message.channel.send(f'User {mention} does not seem to be playing in this tournament!')
        return

    await send_decks(context.message.author, anytime_player['decks'])
