import discord
from discord.ext import commands
from bot_config.checks import check_owner

class Messaging(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.port_pairs = {}
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

    #Set a channel to respond to
    @commands.group(invoke_without_command=True)
    @commands.check(check_owner)
    async def portal(self,ctx,channel : discord.TextChannel):
        print(self.port_pairs)
        try:
            if self.port_pairs[channel] != None:
                await ctx.channel.send('Portal Closed in {0}'.format(channel))
                self.port_pairs[channel] = None
            else:
                await ctx.channel.send('Portal Opened in {0}'.format(channel))
                self.port_pairs[channel] = ctx.channel
        except:
            await ctx.channel.send('Portal Opened in {0}'.format(channel))
            self.port_pairs[channel] = ctx.channel

    @portal.command()
    async def look(self,ctx,gid):
        channel = self.bot.get_channel(int(gid))
        if channel == None:
            await ctx.channel.send('Failed to find channel')
            return 

        try:
            if self.port_pairs[channel] != None:
                await ctx.channel.send('Portal Closed in {0}'.format(channel))
                self.port_pairs[channel] = None
            else:
                await ctx.channel.send('Portal Opened in {0}'.format(channel))
                self.port_pairs[channel] = ctx.channel
        except:
            await ctx.channel.send('Portal Opened in {0}'.format(channel))
            self.port_pairs[channel] = ctx.channel


    @portal.command()
    async def clear(self,ctx):
        self.port_pairs = {}
        await ctx.channel.send(self.port_pairs)

    @portal.command()
    async def see(self,ctx):
        await ctx.channel.send(self.port_pairs)

    @commands.Cog.listener('on_message')
    async def port(self,message):
        if message.content.startswith('!portal'):
            return
        if message.author.bot:
            return
        for channel in self.port_pairs:
            if self.port_pairs[channel] != None:
                if message.channel == self.port_pairs[channel]:
                    await channel.send(message.content)

        

def setup(bot):
    bot.add_cog(Messaging(bot))