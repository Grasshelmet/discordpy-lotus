import discord
from discord.ext import commands

class Voice(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.last_member = None

def setup(bot):
    bot.add_cog(Voice(bot))
