from __future__ import unicode_literals
import discord,typing,time,asyncio,youtube_dl,os
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
    async def play(self,ctx,url):
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

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            }],
        }


        for file in os.listdir('./'):
            if file.endswith('.mp3'):
                os.remove(file)


        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir('./'):
            if file.endswith('.mp3'):
                os.rename(file,'song.mp3')

        vc.play(discord.FFmpegPCMAudio('song.mp3'),after=lambda e: print("Failed to play",e))
        while vc.is_playing() or vc.is_paused():
            await asyncio.sleep(.5)
        await vc.disconnect()
        vc.cleanup()

    #command to pause currently playing audio
    @commands.command()
    async def pause(self,ctx): 
        channel = ctx.author.voice.channel
        vc = discord.utils.get(self.bot.voice_clients,guild=ctx.guild)

        if vc and vc.is_connected() and vc.is_playing() and not vc.is_paused():
            vc.pause()
    
    #command to resume paused audio
    @commands.command()
    async def resume(self,ctx):
        channel = ctx.author.voice.channel
        vc = discord.utils.get(self.bot.voice_clients,guild=ctx.guild)

        if vc and vc.is_connected() and vc.is_paused():
            vc.resume()

    #command to stop playing
    @commands.command()
    async def stop(self,ctx):
        channel = ctx.author.voice.channel
        vc = discord.utils.get(self.bot.voice_clients,guild=ctx.guild)

        if vc and vc.is_connected():
            vc.stop()
def setup(bot):
    bot.add_cog(Voice(bot))
