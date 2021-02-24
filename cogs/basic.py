import discord,time,random,typing
from discord.ext import commands
from discord import Embed

description = 'Simple cpg with {}ping and {}nick'

class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    #a class ping/pong command
    @commands.group(brief='The most basic ping command')
    async def ping(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('pong')

    @ping.command()
    async def pong(self,ctx):
        await ctx.send('ping pong')

    #basic dice rolling function
    @commands.command(brief='Rolls a dice, add a number ater to roll a die of that size')
    async def roll(self,ctx,arg1: typing.Union[int,str]=6):
        if type(arg1) is str:
            if arg1.startswith('d') == True:
                replaced = arg1.replace('d','')
                arg1 = int(replaced)
        random.seed()
        result = random.randint(1,arg1)
        await ctx.send('d{} rolled a {}'.format(arg1,result))


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

