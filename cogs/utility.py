import discord,time,pytz,json, binascii
from datetime import datetime,timezone
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.last_member = None


    @commands.group(invoke_without_command =True,aliases=['tz','time'],brief='Timezone converter command')
    async def timezone(self,ctx,member : discord.Member=None):
        frmt = '%I:%M %p %Z'
        c_utc = datetime.now(pytz.timezone('UTC'))
        if member == None:
            await ctx.channel.send('Current time is {}'.format(c_utc.strftime(frmt) ))
            return
        try:
            with open('bot_config/timezones.json','r') as f:
                data = json.load(f)
        except Exception as e:
            jd ='{}'
            data = json.loads(jd)

        try:
            tz = data[str(member.id)]
        except Exception as e:
            await ctx.channel.send('User {} has no set timezone'.format(member))
            return

        c_tz = c_utc.astimezone(pytz.timezone(tz))
        await ctx.channel.send('Current time for {} is {}'.format(member,c_tz.strftime(frmt) ))
    
    #set timezone of self
    @timezone.command()
    async def setself(self,ctx,arg):
        abbrvs ={
                    'PST':'America/Los_Angeles',
                    'CST':'CST6CDT',
                    'AEST':'Australia/Brisbane'
                }
        result = abbrvs.get(arg,'NONE')
        if result != 'NONE':
            arg = result
        try:
            pytz.timezone(arg)
        except Exception as e:
            await ctx.channel.send('Argument was not a valid timezone')


        try:
            with open('bot_config/timezones.json','r') as f:
                data = json.load(f)
        except Exception as e:
            jd ='{}'
            data = json.loads(jd)

        try:
            data[str(ctx.author.id)] = arg
        except Exception as e:
            print('{}: e'.format(e.__name__,e))
            await ctx.channel.send('Argument was not a valid timezone')
            return

        with open('bot_config/timezones.json','w') as f:
            json.dump(data,f)
        await ctx.channel.send('Timezone for {} set to: {}'.format(ctx.author,pytz.timezone(arg)))

    #set timezone of mentioned member
    @timezone.command(invoke_without_command=True)
    async def set(self,ctx,member : discord.Member,arg):

        abbrvs ={
                    'PST':'America/Los_Angeles',
                    'CST':'CST6CDT',
                    'AEST':'Australia/Brisbane'
                }
        result = abbrvs.get(arg,'NONE')
        if result != 'NONE':
            arg = result
        try:
            pytz.timezone(arg)
        except Exception as e:
            await ctx.channel.send('Argument was not a valid timezone')


        try:
            with open('bot_config/timezones.json','r') as f:
                data = json.load(f)
        except Exception as e:
            jd ='{}'
            data = json.loads(jd)

        try:
            data[str(member.id)] = arg
        except Exception as e:
            print('{}: e'.format(e.__name__,e))
            await ctx.channel.send('Argument was not a valid timezone')
            return

        with open('bot_config/timezones.json','w') as f:
            json.dump(data,f)
        await ctx.channel.send('Timezone for {} set to: {}'.format(member,pytz.timezone(arg)))

    #get time of specfied zone
    @timezone.command()
    async def zone(self,ctx,arg1=None):
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

    #Dispay times of all set members in guild
    @timezone.command()
    async def all(self,ctx):
        frmt = '%I:%M %p %Z'
        c_utc = datetime.now(pytz.timezone('UTC'))
        try:
            with open('bot_config/timezones.json','r') as f:
                data = json.load(f)
        except Exception as e:
            jd ='{}'
            data = json.loads(jd)

        members = await ctx.guild.fetch_members(limit=None).flatten()
        for member in members:
            if str(member.id) in data:
                tz = data[str(member.id)]
                c_tz = c_utc.astimezone(pytz.timezone(tz))
                await ctx.channel.send('Current time for {} is: {}'.format(member,c_tz.strftime(frmt) ))

    #Convert and display number binary into ascii
    @commands.group(aliases=['cvrt'],invoke_without_command = True,brief='Convert binary into ascii')
    async def convert(self,ctx,*,args):
        input= str(args)
        bis = input.split(' ')
        con = ''
        for byte in bis:
            con= ''.join([con,chr(int(byte,2))])
        await ctx.channel.send(con)

    #convert ascii into binary
    @convert.command(aliases=['bi'],brief='Convert asci into binary')
    async def binary(self,ctx,*,args):
        input =str(args)
        con = ''
        for char in input:
            asc = (bin(ord(char))[2:].zfill(8))
            con = ' '.join([con,asc])
        await ctx.channel.send(con)


    #gives an invite link by which to invite the bot to other servers
    @commands.command(brief='Gives a Link by which to invite bot to server,default admin link')
    async def invitelink(self,ctx,member : discord.Member = None):
        dest = ctx.channel
        if member != None:
            dest = member.dm_channel
            if dest == None:
                dest = await member.create_dm()
        try:
            await dest.send('https://discord.com/oauth2/authorize?client_id=762960764977545226&scope=bot')
            print('Invite Link sent to {}'.format(dest))
        except Exception as e:
            print('Failed to send\n {}:{}\n'.format(e,e.__str__))


def setup(bot):
    bot.add_cog(Utility(bot))
