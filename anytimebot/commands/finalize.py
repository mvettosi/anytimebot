from discord.ext import commands
from anytimebot import tournament
from anytimebot.utils import get_anytime, get_anytime_mod_role, get_decklists_channel


# Setup
def setup(bot):
    bot.add_command(finalize)


# Command definition
@commands.command()
async def finalize(context):
    anytime = await get_anytime(context)

    if anytime is None:
        # Handled by get_anytime
        return

    # Check mod status
    mod_role = get_anytime_mod_role(context.message.guild)
    if mod_role not in context.message.author.roles:
        await context.message.channel.send(f'Sorry, only anytime mods can visualize decklists!')
        return

    try:
        await tournament.finalize(anytime['tournament_id'])
    except Exception:
        await context.message.channel.send('Sorry, something went wrong. Check that the tournament is actually finished'
                                           ' and try again!')
        raise

    decklists_channel = get_decklists_channel(context.message.channel.guild)
    await decklists_channel.send(f'Anytime Tournament #{anytime.doc_id} winner:\n')
