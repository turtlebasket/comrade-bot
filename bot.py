r"""
  _____                       __   
 / ___/__  __ _  _______ ____/ /__ 
/ /__/ _ \/  ' \/ __/ _ `/ _  / -_)
\___/\___/_/_/_/_/  \_,_/\_,_/\__/ 

A bot by turtlebasket
"""

import asyncio
import json
from urllib.request import urlopen, Request
import random
import discord
from discord.ext import commands
from discord.ext import tasks
from os import environ
import dbl
from bot_utils import *

from dotenv import load_dotenv
from os import path, getenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv()

with open('config.json', 'r') as json_file:
    config = json.load(json_file)

BOT_TOKEN = getenv('BOT_TOKEN')
DBL_TOKEN = getenv('DBL_TOKEN')

# Feeling cute, might refactor later
MUTE_VOTE_TIME = config["MUTE_VOTE_TIME"]
MIN_MUTE_VOTERS = config["MIN_MUTE_VOTERS"] # should be 3
MUTE_TIME = config["MUTE_TIME"] # 10 mins

KICK_VOTE_TIME = config["KICK_VOTE_TIME"]
MIN_KICK_VOTERS = config["MIN_KICK_VOTERS"]

BAN_VOTE_TIME = config["BAN_VOTE_TIME"]
MIN_BAN_VOTERS = config["MIN_BAN_VOTERS"]

EMOTE_VOTE_TIME = config["EMOTE_VOTE_TIME"]
MIN_EMOTE_VOTERS = config["MIN_EMOTE_VOTERS"]

STATUS_LOOP = config["STATUS_LOOP"]

bot = commands.Bot(command_prefix='>>')
bot.remove_command('help')

# To store users who are currently being voted on
muted_users = []
muting_users = []
kicking_users = []
banning_users = []

async def status_loop():
    while True:
        await bot.change_presence(activity=discord.Game(name="Serving {0} glorious servers".format(len(bot.guilds))))
        await asyncio.sleep(STATUS_LOOP)

        await bot.change_presence(activity=discord.Game(name=">>help"))
        await asyncio.sleep(STATUS_LOOP)

        await bot.change_presence(activity=discord.Game(name="Proletarian Uprising 2: Electric Boogaloo"))
        await asyncio.sleep(STATUS_LOOP)


# top.gg API interaction handling (boilerplate)
class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = DBL_TOKEN
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True) # refresh guild count every 30 mins 

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        """Automatically update server count"""
        try:
            await self.dblpy.post_guild_count()
        except Exception as e:
            print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

        # await asyncio.sleep(1800)

@bot.event
async def on_ready():
    # await bot.change_presence(activity=discord.Game(name='{} servers | >>help'.format(len(bot.guilds))))
    bot.add_cog(TopGG(bot))
    print("Bot started.")
    print("--------------------------")

    await asyncio.sleep(300)
    bot.loop.create_task(status_loop())

@bot.command(aliases=['manual', 'commands', 'info'])
async def help(ctx):
    embed = discord.Embed(title="Comrade: Usage & Other Info")
    embed.add_field(inline=False,
        name="`>>addEmote` <emoji name> [ATTACHED IMAGE]",
        value=
            """Vote to add a new emoji, attached as JPEG, PNG or GIF image.
            Vote time: {0} minutes
            Minimum Voters: {1}
            """.format(int(EMOTE_VOTE_TIME/60), MIN_EMOTE_VOTERS)
    )

    embed.add_field(inline=False,
        name="`>>mute` <user>",
        value=
            """Vote to mute user for {0} minutes.
            Vote time: {1} minutes
            Minimum Voters: {2}
            """.format(int(MUTE_TIME/60), int(MUTE_VOTE_TIME/60), MIN_MUTE_VOTERS)
    )

    embed.add_field(inline=False,
        name="`>>kick` <user>",
        value=
            """Vote to kick user.
            Vote Time: {0} minutes
            Minimum Voters: {1}
            """.format(int(KICK_VOTE_TIME/60), MIN_KICK_VOTERS)
    )

    embed.add_field(inline=False,
        name="`>>ban` <user>",
        value=
            """Vote to ban user.
            Vote Time: {0} minutes
            Minimum Voters: {1}
            """.format(int(BAN_VOTE_TIME/60), MIN_BAN_VOTERS)
    )

    embed.add_field(inline=False,
        name="`>>shibe`",
        value="Random shibe :dog: :eyes:"
    )

    embed.add_field(inline=False,
        name="`>>cat`",
        value="Random cat :cat: :cat2:"
    )

    embed.add_field(inline=False,
        name="`>>birb`",
        value="Random birb :bird: :hatching_chick:"
    )
    
    embed.add_field(inline=False,
        name="`>>ping`",
        value="Get bot latency."
    )

    embed.add_field(inline=False,
        name="Enjoying Comrade?",
        value="[Upvote Comrade on Discord Bot List!](https://top.gg/bot/592852914553487370/vote)"
    )

    embed.add_field(inline=False,
        name="Need help?",
        value="[Report an issue](https://github.com/turtlebasket/comrade-bot/issues)"
    )

    await ctx.send(embed=embed)


@bot.command(aliases=['addemote', 'addemoji', 'addEmoji'])
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

    if vote_passed:
        try:
            file_bytes = await ctx.message.attachments[0].read()
            await ctx.guild.create_custom_emoji(name=emote_name, image=file_bytes)
            await ctx.send("`Emote {0} added!` :{0}:".format(emote_name))
        except:
            await ctx.send(":warning: `There was an error adding emote {}.`".format(emote_name))


@bot.command()
async def shibe(ctx):
    # with urllib.request.urlopen("http://shibe.online/api/shibes?count=1&urls=true&httpsUrls=true") as json_return:
    with urlopen(Request(url="http://shibe.online/api/shibes?count=1&urls=true&httpsUrls=true", headers={'User-Agent': 'Mozilla/5.0'})) as json_return:
        shibe_contents = json_return.read()
        msg="{0}, here is your random shibe:".format(ctx.message.author.name)
        url=json.loads(shibe_contents)[0]
    await ctx.send(embed=imgfun(msg, url))

@bot.command(aliases=['bird'])
async def birb(ctx):
    with urlopen(Request(url="http://random.birb.pw/tweet.json", headers={'User-Agent': 'Mozilla/5.0'})) as json_return:
        # get image filename
        birb_contents = json_return.read()
        msg="{0}, here is your random birb:".format(ctx.message.author.name)
        # insert image filename into URL
        url="http://random.birb.pw/img/{}".format(json.loads(birb_contents)["file"])
    await ctx.send(embed=imgfun(msg, url))

@bot.command(aliases=['kitty', 'kitti'])
async def cat(ctx):
    with urlopen(Request(url="http://aws.random.cat/meow", headers={'User-Agent': 'Mozilla/5.0'})) as json_return:
        # get image filename
        cat_contents = json_return.read()
        msg="{0}, here is your random cat:".format(ctx.message.author.name)
        # insert image filename into URL
        url=json.loads(cat_contents)["file"]
    await ctx.send(embed=imgfun(msg, url))
    
@bot.command(aliases=['latency'])
async def ping(ctx):
    await ctx.send("`Bot latency: {}s`".format(round(bot.latency, 2)))

@bot.command()
async def mute(ctx, target_user:discord.User):

    # await require_lower_permissions(ctx, target_user, bot)

    if target_user in muting_users:
        await ctx.send("There is already a mute vote on `{}`!".format(target_user))
        return
    elif target_user in muted_users:
        await ctx.send("`{}` is already muted!".format(target_user))
        return

    muting_users.append(target_user)
    vote_passed = await take_vote(ctx, "Mute `{}`?\n⚠ NOTE: Can't mute users with an equal or higher role.".format(target_user), MUTE_VOTE_TIME, MIN_MUTE_VOTERS)
    muting_users.remove(target_user)

    if vote_passed:
        try:
            # Add to muted_users
            muted_users.append(target_user)
            # add temp. role for mute, edit role position to take precedence over other roles
            muted_role = await ctx.guild.create_role(name="Muted")
            await muted_role.edit(position=ctx.guild.get_member(target_user.id).top_role.position+1)

            # change channel permissions for new role
            for channel in ctx.guild.channels:
                if type(channel) is discord.TextChannel and target_user in channel.members:
                    await channel.set_permissions(muted_role, read_messages=True, send_messages=False, add_reactions=False)

                elif type(channel) is discord.VoiceChannel:
                    await channel.set_permissions(muted_role, connect=False)

            # Give role to member
            await ctx.guild.get_member(target_user.id).add_roles(muted_role)
            await ctx.send("**{0}, the majority has ruled that you should be muted.** See ya in {1} minutes!".format(target_user, int(MUTE_TIME/60)))
            await asyncio.sleep(MUTE_TIME)
            await muted_role.delete()

            # Remove from muted_users
            muted_users.remove(target_user)
        except discord.ext.commands.errors.CommandInvokeError:
            await error_admin_targeted(ctx)
            muted_users.remove(target_user)

@bot.command()
async def kick(ctx, target_user:discord.User):

    # await require_lower_permissions(ctx, target_user, bot)

    if target_user in kicking_users:
        await ctx.send("There is already a kick vote on `{}`!".format(target_user))
        return 

    # add to kicking_users
    kicking_users.append(target_user)

    vote_passed = await take_vote(ctx, "Kick `{}`?\n⚠ NOTE: Can't kick users with an equal or higher role.".format(target_user), KICK_VOTE_TIME, MIN_KICK_VOTERS)

    if vote_passed:
        try:
            await ctx.guild.kick(target_user)
            await ctx.send("👢 Kicked `{}`.".format(target_user))
        except discord.ext.commands.errors.CommandInvokeError:
            await error_admin_targeted(ctx)

    kicking_users.remove(target_user)


@bot.command(aliases=['exile'])
async def ban(ctx, target_user:discord.User):

    # await require_lower_permissions(ctx, target_user, bot)

    if target_user in banning_users:
        await ctx.send("There is already a ban vote on `{}`!".format(target_user))
        return 

    # add to banning_users
    banning_users.append(target_user)

    vote_passed = await take_vote(ctx, "Ban `{}`?\n⚠ NOTE: Can't ban users with an equal or higher role.".format(target_user), BAN_VOTE_TIME, MIN_BAN_VOTERS)

    if vote_passed:
        try:
            await ctx.guild.ban(target_user)
            await ctx.send("🦀🦀 `{}` IS GONE 🦀🦀".format(target_user.name))
        except discord.ext.commands.errors.CommandInvokeError:
            await error_admin_targeted(ctx)


    banning_users.remove(target_user)

@bot.command()
async def test(ctx, target_user:discord.User):
    await require_lower_permissions(ctx, target_user, bot)
    await ctx.send("success")

bot.run(BOT_TOKEN)
