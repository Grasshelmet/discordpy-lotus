import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self._last_member = None
    
    @commands.command()
    async def perms(self,ctv,member : discord.Member):
        pers = member.guild_permissions
        prin = 'Permissions for {0} in Guild {1}:\n'.format(member,ctv.guild)
        for pe in pers:
            prin = prin + '\t{0[0]}: {0[1]}\n'.format(pe)
        await ctv.channel.send('```{0}```'.format(prin))

def setup(bot):
    bot.add_cog(Info(bot))