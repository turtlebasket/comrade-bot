import random
import discord
from discord.ext import commands
import asyncio

async def take_vote(ctx, question:str, wait_time, min_voters):

    """
    take_vote(ctx, question:str) - Collects votes
    ctx: pass from command function
    question: what to ask

    returns [<all who want>, <all who don't want>]. 
    It's up to the context/use case to decide how these should be used.
    """
    embed_title="NEW VOTE"
    votey_message = await ctx.send(
        embed=discord.Embed(
            type="rich",
            title=embed_title,
            # description="{}\n\n✅ - Yes\n\n❌ - No".format(question)
            description="{0}\n\n✅ - Yes\n❌ - No\nMinimum {1} votes required.".format(question, min_voters)
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

    # await ctx.send(embed=discord.Embed(type='rich', title="VOTE RESULTS", description="✅ - {0}\n\n❌ - {1}\n".format(all_in_favor, not_in_favor)))
    passed = False
    if all_in_favor > not_in_favor and all_in_favor >= min_voters:
        question += "\nVERDICT: **Vote passed!**"
        passed = True
    else:
        question += "\nVERDICT: **Vote failed!**"

    await votey_message.edit(embed=discord.Embed(
        type="rich",
        title=embed_title,
        description=question
    ))
    return passed

async def improper_usage(ctx):
    await ctx.send("Improper command usage! See `>>help` for more.")

def imgfun(msg:str, img_url:str):
    return discord.Embed(
        title=msg, color=random.randint(0, 16777215)
    ).set_image(url=img_url)