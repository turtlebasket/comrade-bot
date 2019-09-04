"""
Karl Marx 2
A bot by turtlebasket
"""

import asyncio
import json
from urllib.request import urlopen, Request
import random
import discord
from discord.ext import commands
from bot_utils import *

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

EMOTE_VOTE_TIME = config["EMOTE_VOTE_TIME"]
MIN_EMOTE_VOTERS = config["MIN_EMOTE_VOTERS"]

bot = commands.Bot(command_prefix='>>')
bot.remove_command('help')

# To store users who are currently being voted on
muted_users = []
muting_users = []
kicking_users = []
banning_users = []

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='{} servers | >>help'.format(len(bot.guilds))))
    print("Bot started.")
    print("--------------------------")

@bot.command(aliases=['manual', 'commands'])
async def help(ctx):
    embed = discord.Embed(title="How 2 Comrade")
    embed.add_field(
        name=">>addEmote <emoji name>",
        value="hold a {0}-second vote on whether or not to add a given emote (provided as a message attachment.".format(EMOTE_VOTE_TIME)
    )

    embed.add_field(
        name=">>mute <user>",
        value="Hold a {0}-second vote to mute a user for {1} minutes (minimum voters: {2}, over 50% majority required). You can set different requirements in `config.json`.".format(MUTE_VOTE_TIME, int(MUTE_TIME/60), MIN_MUTE_VOTERS)
    )

    embed.add_field(
        name=">>kick <user>",
        value="Kick user. The vote is up for {0} minutes, and requires that a minimum of {1} users and >50% approve.".format(int(KICK_VOTE_TIME/60), MIN_KICK_VOTERS)
    )

    embed.add_field(
        name=">>ban <user>",
        value="Ban user. By default, the vote lasts {0} minutes, and requires that there be at least {1} votes and a 50% majority. Like the `>>mute`/`>>kick` commands, you can also tweak settings in `config.json`.".format(int(BAN_VOTE_TIME/60), MIN_BAN_VOTERS)
    )

    embed.add_field(
        name=">>ping",
        value="Get bot latency."
    )

    embed.add_field(
        name=">>shibe",
        value="shibe :dog: :eyes"
    )
    
    await ctx.send(embed=embed)


@bot.command(aliases=['addEmoji'])
async def addEmote(ctx, emote_name: str):
    """
    command: addEmote

    Hold a vote to add an emoji.
    """
    filename = str(ctx.message.attachments[0].filename)
    valid_exts = [".jpg", ".jpeg", ".png", ".gif"]
    valid = False
    for ext in valid_exts:
        # print(filename.endswith(ext))
        if filename.endswith(ext):
            valid = True
            break

    if not valid:
        await ctx.send("Invalid filetype!")
        return
        
    vote_passed = await take_vote(ctx, "Add emoji `{}`?".format(emote_name), EMOTE_VOTE_TIME, MIN_EMOTE_VOTERS)

    # if all_in_favor > not_in_favor and all_in_favor > MIN_EMOTE_VOTERS:
    if vote_passed:
        file_bytes = await ctx.message.attachments[0].read()
        await ctx.guild.create_custom_emoji(name=emote_name, image=file_bytes)

@bot.command()
async def shibe(ctx):
    # with urllib.request.urlopen("http://shibe.online/api/shibes?count=1&urls=true&httpsUrls=true") as json_return:
    with urlopen(Request(url="http://shibe.online/api/shibes?count=1&urls=true&httpsUrls=true", headers={'User-Agent': 'Mozilla/5.0'})) as json_return:
        shibe_contents = json_return.read()
        msg="{0}, here is your random shibe:".format(ctx.message.author.name)
        url=json.loads(shibe_contents)[0]
    await ctx.send(embed=imgfun(msg, url))
    
@bot.command(aliases=['latency'])
async def ping(ctx):
    await ctx.send("`Bot latency: {}s`".format(round(bot.latency, 2)))

@bot.command()
async def mute(ctx, target_user:discord.User):

    if target_user in muting_users:
        await ctx.send("There is already a mute vote on `{}`!".format(target_user))
        return
    elif target_user in muted_users:
        await ctx.send("`{}` is already muted!".format(target_user))
        return

    muting_users.append(target_user)
    vote_passed = await take_vote(ctx, "Mute `{}`?".format(target_user), MUTE_VOTE_TIME, MIN_MUTE_VOTERS)
    muting_users.remove(target_user)

    if vote_passed:
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
        await ctx.send("**{0}, the majority has ruled that you should be muted.** See ya in {1} minutes!".format(target_user, int(MUTE_TIME/60)))
        await asyncio.sleep(MUTE_TIME)
        await muted_role.delete()

        # Remove from muted_users
        muted_users.remove(target_user)

@bot.command()
async def kick(ctx, target_user:discord.User):

    if target_user in kicking_users:
        await ctx.send("There is already a kick vote on `{}`!".format(target_user))
        return 

    # add to kicking_users
    kicking_users.append(target_user)

    vote_passed = await take_vote(ctx, "Kick `{}`?".format(target_user), KICK_VOTE_TIME, MIN_KICK_VOTERS)

    if vote_passed:
        await ctx.guild.kick(target_user)

    kicking_users.remove(target_user)


@bot.command(aliases=['exile'])
async def ban(ctx, target_user:discord.User):

    if target_user in banning_users:
        await ctx.send("There is already a ban vote on `{}`!".format(target_user))
        return 

    # add to banning_users
    banning_users.append(target_user)

    vote_passed = await take_vote(ctx, "Ban `{}`?".format(target_user), BAN_VOTE_TIME, MIN_BAN_VOTERS)

    if vote_passed:
        await ctx.guild.ban(target_user)
        await ctx.send(":crab: :crab: `{}` IS GONE :crab: :crab:".format(target_user.name))

    banning_users.remove(target_user)

bot.run(open("token.txt").read().strip())
