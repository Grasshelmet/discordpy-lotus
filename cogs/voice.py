import discord,typing,time
from discord.ext import commands

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Voice(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.last_member = None
        self.active_vcs = []

    #connects bot to vc
    @commands.command(aliases=['ct','cnt'])
    async def connect(self,ctx):
        channel = ctx.author.voice.channel
        vc = discord.utils.get(self.bot.voice_clients,guild=ctx.guild)

        if vc and vc.is_connected():
            await vc.move_to(channel)
        else:
            try:
                vc = await channel.connect()
            except Exception as er:
                await ctx.send("Failed to connect to {}\nError: {}".format(channel.mention,er))
                return

    #Disconnects bot from vc
    @commands.command(aliases=['dt','dsct'])
    async def disconnect(self,ctx,):
        channel = ctx.author.voice.channel
        vc = discord.utils.get(self.bot.voice_clients,guild=ctx.guild)

        await vc.disconnect()
        vc.cleanup()

    #plays an audio file at the specified location
    @commands.command()
    async def play(self,ctx,file):
        channel = ctx.author.voice.channel
        vc = discord.utils.get(self.bot.voice_clients,guild=ctx.guild)

        if vc and vc.is_connected():
            await vc.move_to(channel)
        else:
            try:
                vc = await channel.connect()
            except Exception as er:
                await ctx.send("Failed to connect to {}\nError: {}".format(channel.mention,er))
                return


        vc.play(discord.FFmpegPCMAudio(file,**FFMPEG_OPTIONS),after=lambda e: print("Failed to play",e))
        vc.is_playing()
        
def setup(bot):
    bot.add_cog(Voice(bot))
