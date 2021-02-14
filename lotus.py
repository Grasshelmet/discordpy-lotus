from discord.ext import commands
from bot_config.tok import TOKEN
from bot_config.checks import check_owner
import os,json,discord


description = '''Beep Beep boop boop'''
startup_extensions = ['basic','info']
default_prefix = '!'

#retrieves server specific prefixes or gives default !
def get_prefix(bot,message):
    try:
        with open('bot_config/prefixes.json','r') as f:
            data = json.load(f)
    except Exception as e:
        return commands.when_mentioned_or('!')(bot,message)

    if message.guild == None:
        if not str(message.channel.id) in data:
            return commands.when_mentioned_or('!')(bot,message)
        return commands.when_mentioned_or(data[str(message.channel.id)])(bot,message)
    
    if not str(message.guild.id) in data:
        return commands.when_mentioned_or('!')(bot,message)
    return commands.when_mentioned_or(data[str(message.guild.id)])(bot,message)

intents = discord.Intents.default()
intents.members = True


bot = commands.Bot(command_prefix=get_prefix,description=description,intents=intents)




class Core(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self._last_member = None

    #loads in a cog extension
    @commands.command(brief='loads an unloaded cog')
    async def loadcog(self,ctx,*args):
        for arg1 in args:
            try:
                bot.load_extension('cogs.{}'.format(arg1))
                print('--------------------------------\n')
                print('\t{} Cog loaded\n'.format(arg1))
                print('--------------------------------\n')
                await ctx.channel.send('Loaded Extension {}.'.format(arg1))
            except Exception as e:
                exe = '{}: {}'.format(e.__cause__,e)
                await ctx.channel.send('Unable to load Extension {}\n{}'.format(arg1,exe))

    #unloads a cog extension
    @commands.command(brief='unloads a loaded cog')
    async def unloadcog(self,ctx,*args):
        for arg1 in args:
            if arg1 == 'core':
                return await ctx.channel.send('{0.message.author.mention} Cannot unload core cog'.format(ctx))
            try:
                bot.unload_extension('cogs.{}'.format(arg1))
                await ctx.channel.send('Cog {} unloaded'.format(arg1))
            except Exception as e:
                exe = '{}: {}'.format(e.__cause__,e)
                await ctx.channel.send('Unable to unload Extension {}\n{}'.format(arg1,exe))

    #restarts a cog
    @commands.command(brief='reloads a loaded cog')
    async def reloadcog(self,ctx,*args):
        for arg1 in args:
            if(arg1 =='core'):
                await ctx.send('Can\'t reload core cog')
                continue
            try:
                bot.reload_extension('cogs.{}'.format(arg1))
                print('--------------------------------\n')
                print('\t{} Cog reloaded\n'.format(arg1))
                print('--------------------------------\n')
                await ctx.channel.send('{} Extension Reloaded'.format(arg1))
            except Exception as e:
                exe = '{}: {}'.format(e.name,e)
                await ctx.channel.send('Cog {} could not be reloaded: {}'.format(arg1,e.__cause__))
    
    #restarts the bot
    @commands.command(brief='restarts the bot entirely')
    async def restart(self,ctx):
        try:
            print('Closing Bot.\n\n')
            js = '{"restart":"None"}'
            r = json.loads(js)
            r['restart'] = ctx.channel.id
            with open('bot_config/restartChannel.json','w') as f:
                json.dump(r,f)
                

            await self.bot.logout()

        except:
            pass
        finally:
                os.system('py lotus.py')

    #on ready
    #Sends message to console on startup
    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as {0.user}'.format(self.bot))

        try:
            with open('bot_config/restartChannel.json','r') as f:
                data = json.load(f)
            id=data['restart']
            data['restart'] = None
            with open('bot_config/restartChannel.json','w') as f:
                json.dump(data,f)
            await self.bot.get_channel(id).send('Bot sussesfully restarted')
        except Exception as e:
            print(e.__cause__)

    #quits the bot
    @commands.command(brief='shutsdown the bot')
    async def quit(self,ctx):
        await self.bot.logout()

    #sets server prefix
    @commands.group(invoke_without_command=True,aliases=['setprefix'],brief='sets the prefix for the server')
    async def prefix(self,ctx,*args):
        if not args:
            await ctx.send('Please include the prefix as an argument')
            return
        id = 0
        if ctx.guild == None:
            id =ctx.channel.id
        else:
            id = ctx.guild.id

        try:
            with open('bot_config/prefixes.json','r') as f:
                data = json.load(f)
        except Exception as e:
            d = '{}'
            data = json.loads(d)

        data[str(id)] = args[0]
        with open('bot_config/prefixes.json','w') as f:
            json.dump(data,f)
        await ctx.channel.send('Server Prefix Successfully set to: {}'.format(args[0]))
    
    #Remove a guilds set prefix
    @prefix.command(brief='Removes the set prefix for the server command is used in')
    async def rmv(self,ctx):
        id = 0
        if ctx.guild == None:
            id =ctx.channel.id
        else:
            id = ctx.guild.id

        with open('bot_config/prefixes.json','r') as f:
            data = json.load(f)
        try:
            data.pop('{}'.format(id),None)
            with open('bot_config/prefixes.json','w') as f:
                json.dump(data,f)
            await ctx.channel.send('Server Prefix Removed, Default Prefix: {}'.format(default_prefix))
        except Exception as e:
            await ctx.channel.send('Server had no custom prefix, Default Prefix: {}'.format(default_prefix))
        

    #makes core commands only available to the owner
    async def cog_check(self,ctx):
        if not await check_owner(ctx):
            await ctx.channel.send('{} You do not own this bot.'.format(ctx.message.author.mention))
            return False
        else:
            return True

def setup(bot):
    bot.add_cog(Core(bot))

#load core extension
try:
    setup(bot)
    print('--------------------------------\n')
    print('\tCore Cog loaded\n')
    print('--------------------------------\n')
except Exception as e:
    exe = '{}: {}'.format(e.name,e)
    print('Unable to load Exstension {}\n{}'.format('core',exe))

#load startup exstensions
for extension in startup_extensions:
    try:
       bot.load_extension('cogs.{}'.format(extension))
       print('--------------------------------\n')
       print('\t{} Cog loaded\n'.format(extension))
       print('--------------------------------\n')
    except Exception as e:
        exe = '{}: {}'.format(e.name,e)
        print('Unable to load Exstension {}\n {}'.format(extension,exe))


bot.run(TOKEN)
