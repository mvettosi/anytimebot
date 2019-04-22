from discord.ext import commands
from anytimebot import tournament
from anytimebot.utils import get_anytime, get_anytime_mod_role


# Setup
def setup(bot):
    bot.add_command(finalize)


# Command definition
@commands.command()
async def finalize(context):
    anytime = await get_anytime(context)
    if anytime is not None:
        mod_role = get_anytime_mod_role(context.message.guild)
        if mod_role not in context.message.author.roles:
            await context.message.channel.send(f'Sorry, only anytime mods can finalize a tournament!')
        else:
            try:
                await tournament.finalize(anytime.tournament_id)
            except Exception:
                await context.message.channel.send('Sorry, something went wrong. Please try again and if it\'s not '
                                                   'getting better, finalize the tournament directly on the brackets'
                                                   'url.')
                raise
            #TODO post decklist and other info in the 1-st-place-decks channel
