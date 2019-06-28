"""
Karl Marx 2
A bot by turtlebasket
"""

import asyncio
import json
import discord
from discord.ext import commands

MUTE_VOTE_TIME = 10
MUTE_VOTER_MIN = 2
MUTE_TIME = 600 # 10 mins
BAN_VOTE_TIME = 8
BAN_VOTER_MIN = 4
bot = commands.Bot(command_prefix='>>')

@bot.event
async def on_ready():
    print("Bot started.")
    print("--------------------------")

@bot.command()
async def ping(ctx):
    """ command: ping
    Use with caution, you might stir up a revolution.
    """
    await ctx.send("What do you think I am, some sort of toy? I refuse to bend to the will of the bourgeoisie!")

@bot.command()
async def anthem(ctx):
    """
    command: anthem
    some people just need a reference, ya know?
    """
    await ctx.send("Soyuz nyerushimyiy ryespublik svobodnyikh\n"
                   "Splotila navyeki Vyelikaya Rus’.\n"
                   "Da zdravstvuyet sozdannyiy volyey narodov\n"
                   "Yedinyiy, moguchiy Sovyetskiy Soyuz!\n")

# not a command, just some functionality that's used across commands
async def take_vote(ctx, question:str, wait_time):
    """
    take_vote(ctx, question:str) - Collects votes
    ctx: pass from command function
    question: what to ask

    returns [<all who want>, <all who don't want>]. 
    It's up to the context/use case to decide how these should be used.
    """

    votey_message = await ctx.send("**=== NEW VOTE ===**\n{}".format(question))

    await votey_message.add_reaction('✅')
    await votey_message.add_reaction('❌')

    await asyncio.sleep(wait_time)

    finished_votey = await votey_message.channel.fetch_message(votey_message.id)
    all_in_favor = 0
    not_in_favor = 0

    for reaction in finished_votey.reactions:
        if str(reaction.emoji) == '✅':
            all_in_favor += reaction.count-1 # don't include bot's reaction
        elif str(reaction.emoji) == '✅':
            not_in_favor += reaction.count-1
        else:
            pass

    await ctx.send(
        "**=== VOTE RESULTS ===**\n"
        "✅ - {0}\n"
        "❌ - {1}\n".format(all_in_favor, not_in_favor))
    return [all_in_favor, not_in_favor]

@bot.command()
async def mute(ctx, target_user:discord.User):

    results = await take_vote(ctx, "Mute `{}`?".format(target_user), MUTE_VOTE_TIME)
    all_in_favor = results[0]
    not_in_favor = results[1]

    if all_in_favor > 0 and all_in_favor - not_in_favor > 0:
        # Take action to mute user

        # add temp. role for mute
        muted_role = await ctx.guild.create_role(name="Muted")
        # edit role position to take precedence over other roles
        await muted_role.edit(position=ctx.guild.get_member(target_user.id).top_role.position+1)

        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, read_messages=True, send_messages=False, add_reactions=False, connect=False)

        await ctx.guild.get_member(target_user.id).add_roles(muted_role)
        await ctx.send("**{0}, the majority has ruled that you should be muted.** See ya in {1} minutes!".format(target_user, int(MUTE_TIME/60)))
        await asyncio.sleep(MUTE_TIME)
        await muted_role.delete()

    else:
        await ctx.send("**{} has not been muted.**".format(target_user))

@bot.command()
async def roletest(ctx):
    await ctx.send("`{}`".format(ctx.guild.roles))

@bot.command()
async def exile(ctx, target_user:discord.User):
    results = await take_vote(ctx, "Ban `{}`?".format(target_user), BAN_VOTE_TIME)
    all_in_favor = results[0]
    not_in_favor = results[1]

    if all_in_favor > not_in_favor and all_in_favor >= BAN_VOTER_MIN: # change to 10 later
        await ctx.guild.ban(target_user)
        await ctx.send(":crab: :crab: `{}` IS GONE :crab: :crab:".format(target_user.name))
    elif all_in_favor <= all_in_favor:
        await ctx.send("The majority (>50%) did not decide on banning `{}`.".format(target_user.name))
    elif all_in_favor < 1:
        await ctx.send("Not enough users voted to ban `{}`.".format(target_user.name))

bot.run(open("token.txt").read().strip())
