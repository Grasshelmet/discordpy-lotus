import discord
from discord.ext import commands
from discord import Embed

class Logging(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.last_member=None

    #listenr for dms sent to the bot
    @commands.Cog.listener('on_message')
    async def botdms(self,message):
        if not (isinstance(message.channel,discord.DMChannel)):
            return
        if message.author.id == self.bot.user.id:
            return
        channel = self.bot.get_channel(809190457044107315)
        
        mesEmbed = Embed(title='{0}: {0.id}'.format(message.author),type='rich',color=0xd010d0,timestamp=message.created_at)
        mesEmbed.set_thumbnail(url=message.author.avatar_url)
        mesEmbed.add_field(name='__Message:__',value=message.content,inline=False)

        await channel.send(embed=mesEmbed)

def setup(bot):
    bot.add_cog(Logging(bot))