import discord,random,json
from discord.ext import commands
from discord import Embed

class Fun(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.last_member =None

    @commands.command(brief='Pulls up random pokemon name')
    async def pokeran(self,ctx):
        random.seed()
        ranint = random.randint(1,898)
        
        apibase = 'https://pokeapi.co/api/v2/'
        pokeem = Embed(title=str(p1.name).capitalize())
        pokeem.set_image(url = str(p1.sprites.front_default))
        await ctx.send(embed=pokeem)

def setup(bot):
    bot.add_cog(Fun(bot))
