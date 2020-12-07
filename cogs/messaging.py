import discord
from discord.ext import commands
from checks import check_owner

class Messaging(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self._last_member = None

    #repeats a message 
    @commands.command()
    async def repeat(self,ctx,arg1,arg2=1,arg3=None):
        if arg3=='del':
            await ctx.message.delete()
        for x in range(arg2):
            await ctx.send('{0}'.format(arg1))

    #Dm a user
    @commands.command()
    @commands.check(check_owner)
    async def dmuser(self,ctx, member : discord.Member,*,args):
        channel = member.dm_channel
        if channel == None:
            channel = await member.create_dm()
        try:
            await channel.send(args)
            print('Message sent')
        except Exception as e:
            print('Failed to send. {}'.format(e.name))

def setup(bot):
    bot.add_cog(Messaging(bot))