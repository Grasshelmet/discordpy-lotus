import discord,time,pytz
from datetime import datetime,timezone
from discord.ext import commands
from checks import check_owner

class Utility(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.last_membner = None

    @commands.command(aliases=['tz','time'])
    @commands.group()
    async def timezone(self,ctx,arg1=None):
        frmt = '%I:%M %p %Z'
        c_utc = datetime.now(pytz.timezone('UTC'))
        if arg1 == None:
            await ctx.channel.send('Current time is {}'.format(c_utc.strftime(frmt) ))
        else:
            abbrvs ={
                    'PST':'America/Los_Angeles',
                    'CST':'CST6CDT',
                    'AEST':'Australia/Brisbane'
                }
            result = abbrvs.get(arg1,'NONE')
            if result != 'NONE':
                arg1 = result
            tz = pytz.timezone(arg1)
            ti = c_utc.astimezone(tz)
            await ctx.channel.send('Current time is {}'.format(ti.strftime(frmt) ))


def setup(bot):
    bot.add_cog(Utility(bot))
