import discord,time
from discord.ext import commands
from discord import Embed

description = 'Simple cpg with {}ping and {}nick'

class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    #a class ping/pong command
    @commands.group()
    async def ping(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('pong')

    @ping.command()
    async def pong(self,ctx):
        await ctx.send('ping pong')

    #renames a single users nickname
    @commands.command()
    async def nick(self,ctx,member: discord.Member,*,args):
        if ctx.message.author == member:
            try:
                await member.edit(nick=args)
            except Exception as e:
                await ctx.channel.send('{0.mention}: Lacking Permission to change nickname.'.format(member))

        elif ctx.message.author.guild_permissions.manage_nicknames:
            await member.edit(nick=args)
        else:
            await ctx.channel.send('{0.mention}: Lacking Permission to change others nicknames.'.format(member))
    
    #deletes certain number of messages
    @commands.command()
    async def delete(self,atx,arg1, member : discord.Member = None):
        return
        
        

def setup(bot):
    bot.add_cog(Basic(bot))

