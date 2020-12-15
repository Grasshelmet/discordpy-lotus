import discord


async def check_owner(ctx):
    inf = await ctx.bot.application_info()
    return ctx.author.id == inf.owner.id
