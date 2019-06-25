import discord
from discord.ext import commands
from time import sleep

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

    await ctx.send(
        "Soyuz nyerushimyiy ryespublik svobodnyikh\n"
        "Splotila navyeki Vyelikaya Rus’.\n"
        "Da zdravstvuyet sozdannyiy volyey narodov\n"
        "Yedinyiy, moguchiy Sovyetskiy Soyuz!\n"
    )

@bot.command()
async def mute(ctx, target_user:str):
    """
    command: soft_mute
    The actual good stuff.
    If someone's spamming or being annoying, just mute 'em. Requires 3 votes by default.
    """

    votey_message = await ctx.send(
        "=== NEW MUTE VOTE ===\n"
        "Mute {}?".format(str(target_user)))

    await votey_message.add_reaction('✅')
    await votey_message.add_reaction('❌')

    sleep(10)

    finished_votey = await votey_message.channel.fetch_message(votey_message.id)
    print(finished_votey.reactions)
    all_in_favor = 0
    not_in_favor = 0
    for reaction in finished_votey.reactions:
        if str(reaction.emoji) == '✅':
            all_in_favor += reaction.count-1
        elif str(reaction.emoji) == '✅':
            not_in_favor += reaction.count-1
        else:
            pass

    await ctx.send(
        "**=== VOTE RESULTS ===**\n"
        "✅ - {0}\n"
        "❌ - {1}\n".format(all_in_favor, not_in_favor))

    if all_in_favor > 2 and all_in_favor - not_in_favor > 0:
        await ctx.send("{} **has** been muted.".format(target_user))
    else:
        await ctx.send("{} **has not** been muted.".format(target_user))
    print("all in favor: {}".format(all_in_favor))

bot.run(open("token.txt").read().strip())
