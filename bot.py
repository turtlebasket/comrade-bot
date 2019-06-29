"""
Karl Marx 2
A bot by turtlebasket
"""

import asyncio
import json
import discord
from discord.ext import commands

# I know, config parsing is ugly and bad, I'll get around to refactoring later TwT

with open('config.json', 'r') as json_file:
    config = json.load(json_file)

MUTE_VOTE_TIME = config["MUTE_VOTE_TIME"]
MIN_MUTE_VOTERS = config["MIN_MUTE_VOTERS"] # should be 3
MUTE_TIME = config["MUTE_TIME"] # 10 mins

KICK_VOTE_TIME = config["KICK_VOTE_TIME"]
MIN_KICK_VOTERS = config["MIN_KICK_VOTERS"]

BAN_VOTE_TIME = config["BAN_VOTE_TIME"]
MIN_BAN_VOTERS = config["MIN_BAN_VOTERS"]

bot = commands.Bot(command_prefix='>>')

# To store users who are currently being voted on
muted_users = []
muting_users = []
kicking_users = []
banning_users = []

@bot.event
async def on_ready():
    print("Bot started.")
    print("--------------------------")


@bot.command()
async def manual(ctx):
    embed = discord.Embed(title="How 2 Comrade")
    embed.add_field(
        name=">>mute",
        value="Hold a {0}-second vote to mute a user for {1} minutes (minimum voters: {2}, over 50% majority required). You can set different requirements in `config.json`.".format(MUTE_VOTE_TIME, int(MUTE_TIME/60), MIN_MUTE_VOTERS)
    )

    embed.add_field(
        name=">>kick",
        value="Kick user. The vote is up for {0} minutes, and requires that a minimum of {1} users and >50% approve.".format(int(KICK_VOTE_TIME/60), MIN_KICK_VOTERS)
    )

    embed.add_field(
        name=">>exile",
        value="Ban user. By default, the vote lasts {0} minutes, and requires that there be at least {1} votes and a 50% majority. Like the `>>mute`/`>>kick` commands, you can also tweak settings in `config.json`.".format(int(BAN_VOTE_TIME/60), MIN_BAN_VOTERS)
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    """ 
    command: ping
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

# not commands, just some functionality that's used across commands
async def take_vote(ctx, question:str, wait_time):

    """
    take_vote(ctx, question:str) - Collects votes
    ctx: pass from command function
    question: what to ask

    returns [<all who want>, <all who don't want>]. 
    It's up to the context/use case to decide how these should be used.
    """

    votey_message = await ctx.send(
        embed=discord.Embed(
            type="rich",
            title="NEW VOTE",
            description="{}\n\n✅ - Yes\n\n❌ - No".format(question)
        )
    )

    await votey_message.add_reaction('✅')
    await votey_message.add_reaction('❌')

    await asyncio.sleep(wait_time)

    finished_votey = await votey_message.channel.fetch_message(votey_message.id)
    all_in_favor = 0
    not_in_favor = 0
    for reaction in finished_votey.reactions:
        if str(reaction.emoji) == '✅':
            all_in_favor += reaction.count-1 # don't include bot's reaction
        if str(reaction.emoji) == '❌':
            not_in_favor += reaction.count-1

    await ctx.send(embed=discord.Embed(type='rich', title="VOTE RESULTS", description="✅ - {0}\n\n❌ - {1}\n".format(all_in_favor, not_in_favor)))
    return [all_in_favor, not_in_favor]

@bot.command()
async def mute(ctx, target_user:discord.User):

    if target_user in muting_users:
        await ctx.send("There is already a mute vote on `{}`!".format(target_user))
        return
    elif target_user in muted_users:
        await ctx.send("`{}` is already muted!".format(target_user))
        return

    muting_users.append(target_user)

    results = await take_vote(ctx, "Mute `{}`?".format(target_user), MUTE_VOTE_TIME)
    all_in_favor = results[0]
    not_in_favor = results[1]

    muting_users.remove(target_user)

    if all_in_favor >= MIN_MUTE_VOTERS and all_in_favor - not_in_favor > 0:
        # Add to muted_users
        muted_users.append(target_user)

        # add temp. role for mute
        muted_role = await ctx.guild.create_role(name="Muted")

        # edit role position to take precedence over other roles
        await muted_role.edit(position=ctx.guild.get_member(target_user.id).top_role.position+1)

        # change channel permissions for new role
        for channel in ctx.guild.channels:
            if channel is discord.TextChannel and target_user in channel.members:
                await channel.set_permissions(muted_role, read_messages=True, send_messages=False, add_reactions=False)

            elif channel is discord.VoiceChannel:
                await channel.set_permissions(muted_role, connect=False)

        # Give role to member
        await ctx.guild.get_member(target_user.id).add_roles(muted_role)

        endmessage = "**{0}, the majority has ruled that you should be muted.** See ya in {1} minutes!".format(target_user, int(MUTE_TIME/60))

        await ctx.send(
            embed=discord.Embed(
                type='rich',
                title="MUTE VOTE VERDICT",
                description=endmessage
            )
        )

        await asyncio.sleep(MUTE_TIME)

        await muted_role.delete()

        # Remove from muted_users
        muted_users.remove(target_user)

        return

    elif all_in_favor <= not_in_favor:
        endmessage = "A >50% vote was not reached."

    elif all_in_favor < MIN_MUTE_VOTERS:
        endmessage = "Not enough users voted to mute `{0}` (min: {1})".format(target_user, MIN_MUTE_VOTERS)

    else:
        endmessage = "**`{}` has not been muted.**".format(target_user)

    await ctx.send(
        embed=discord.Embed(
            type='rich',
            title="MUTE VOTE VERDICT",
            description=endmessage
        )
    )

@bot.command()
async def kick(ctx, target_user:discord.User):

    if target_user in kicking_users:
        await ctx.send("There is already a kick vote on `{}`!".format(target_user))
        return 

    # add to kicking_users
    kicking_users.append(target_user)

    results = await take_vote(ctx, "Kick `{}`?".format(target_user), KICK_VOTE_TIME)
    all_in_favor = results[0]
    not_in_favor = results[1]

    if all_in_favor > not_in_favor and all_in_favor >= MIN_KICK_VOTERS: # change to 10 later
        await ctx.guild.ban(target_user)
        endmessage = "`{}` was kicked.".format(target_user.name)

    elif all_in_favor <= not_in_favor:
        endmessage = "The majority (>50%) did not decide on kicking `{}`.".format(target_user.name)

    elif all_in_favor < MIN_KICK_VOTERS:
        endmessage = "Not enough users voted to kick `{0}` (min: {1}).".format(target_user.name, MIN_KICK_VOTERS)

    else:
        endmessage = "`{}` was not kicked.".format(target_user.name)

    kicking_users.remove(target_user)

    await ctx.send(
        embed=discord.Embed(
            type="rich",
            title="KICK VOTE VERDICT",
            description=endmessage
        )
    )


@bot.command()
async def exile(ctx, target_user:discord.User):

    if target_user in banning_users:
        await ctx.send("There is already a ban vote on `{}`!".format(target_user))
        return 

    # add to banning_users
    banning_users.append(target_user)

    results = await take_vote(ctx, "Ban `{}`?".format(target_user), BAN_VOTE_TIME)
    all_in_favor = results[0]
    not_in_favor = results[1]

    if all_in_favor > not_in_favor and all_in_favor >= MIN_BAN_VOTERS: # change to 10 later
        await ctx.guild.ban(target_user)
        endmessage = ":crab: :crab: `{}` IS GONE :crab: :crab:".format(target_user.name)
    elif all_in_favor <= not_in_favor:
        endmessage = "The majority (>50%) did not decide on banning `{}`.".format(target_user.name)
    elif all_in_favor < MIN_BAN_VOTERS:
        endmessage = "Not enough users voted to ban `{0}` (min: {1}.".format(target_user.name, MIN_BAN_VOTERS)
    else:
        endmessage = "`{}` was not banned.".format(target_user.name)

    banning_users.remove(target_user)

    await ctx.send(
        embed=discord.Embed(
            type="rich",
            title="BAN VOTE VERDICT",
            description=endmessage
        )
    )

bot.run(open("token.txt").read().strip())
