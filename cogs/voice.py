import discord,typing
from discord.ext import commands

class Voice(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.last_member = None
        self.active_vcs = []

    @commands.command(aliases=['ct','cnt'])
    async def connect(self,ctx, channel: typing.Union[discord.VoiceChannel, int]):
        if type(channel) is int:
            channel = self.bot.get_channel(channel)
        if channel == None:
            await ctx.channel.send('Failed to find channel')
            return
        try:
            self.active_vcs.append(await channel.connect())
        except Exception as e:
            await ctx.send("Failed to connect to {}\nError: {}".format(channel.mention,e))

    @commands.command(aliases=['dt','dsct'])
    async def disconnect(self,ctx,channel: typing.Union[discord.VoiceChannel, int]):
        if type(channel) is int:
            channel = self.bot.get_channel(channel)
        if channel == None:
            await ctx.channel.send('Failed to find channel')
            return
          
        activeCon = None
        for con in self.active_vcs:
            if con.channel == channel:
                activeCon = con
        if activeCon == None:
            await ctx.channel.send("Couldn't find active connection")
            return
        await con.disconnect()
        con.cleanup()
def setup(bot):
    bot.add_cog(Voice(bot))
