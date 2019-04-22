from discord.ext import commands


# Setup
from anytimebot import tournament
from anytimebot.utils import get_anytime


def setup(bot):
    bot.add_command(win)


# Command definition
@commands.command()
async def win(context, wins, losses):
    channel = context.message.channel
    if not isinstance(wins, int) or not isinstance(losses, int):
        await channel.send('Only numbers are allowed for how many wins and losses you had!'
                           ' Try something like `!win 2 0`')
    elif losses <= wins:
        await channel.send('You can\'t have won with more losses than wins! Try again with the right score please')
    else:
        anytime = await get_anytime(context)
        if anytime is not None:
            try:
                next_match_data = await tournament.win(
                    anytime.tournament_id,
                    context.message.author.id,
                    f'{wins}-{losses}'
                )
            except Exception:
                await channel.send('Sorry, something went wrong. Please try again and if it\'s not getting better, '
                                   'contact a mod.')
                raise
            if next_match_data is not None:
                opponent = await channel.guild.get_member(next_match_data['opponent'])
                await channel.send(
                    f'{context.message.author.mention} congratz! Your next opponent is {opponent.mention}')
            else:
                await channel.send('Something went wrong, please submit your score in the tournament website directly')
        else:
            await channel.send(
                f'{context.message.author.mention} congratulations! You just won this anytime tournament!'
                f'\nI\'ll make sure to post your decklist in the #1st-place-decks as soon as a mod comes to '
                f'finalize this one.')
