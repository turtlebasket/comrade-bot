import random
import discord
from discord.ext import commands
import asyncio

async def take_vote(ctx, question:str, vote_time, min_voters):

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

    # TODO: Short-circuit eval loop, old stuff temp commented
    # await asyncio.sleep(vote_time)


    passed = False
    curr_time = 0
    while curr_time < vote_time:
        await asyncio.sleep(5)
        all_in_favor = 0
        not_in_favor = 0
        finished_votey = await votey_message.channel.fetch_message(votey_message.id)
        for reaction in finished_votey.reactions:
            if str(reaction.emoji) == '✅':
                all_in_favor += reaction.count-1 # don't include bot's reaction
            elif str(reaction.emoji) == '❌':
                not_in_favor += reaction.count-1

        print("check ({0} ✅, {1} ❌)".format(all_in_favor, not_in_favor))
        if all_in_favor > not_in_favor and all_in_favor >= min_voters:
            passed = True
            break

        await asyncio.sleep(5)
        curr_time += 5

    question += "\nVERDICT: **Vote passed!**" if passed else "\nVERDICT: **Vote failed!**"

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