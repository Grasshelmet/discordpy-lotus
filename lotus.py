from discord.ext import commands
from checks import check_owner,TOKEN
import os,json

description = '''Beep Beep boop boop'''
startup_extensions = ['basic','info']
default_prefix = '!'

#retrieves server specific prefixes or gives default !
def get_prefix(bot,message):
    with open('bot_config/prefixes.json','r') as f:
        data = json.load(f)
    if not str(message.guild.id) in data:
        return commands.when_mentioned_or('!')(bot,message)
    return commands.when_mentioned_or(data[str(message.guild.id)])(bot,message)




bot = commands.Bot(command_prefix=get_prefix,description=description)


class Core(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self._last_member = None

    #loads in a cog extension
    @commands.command()
    async def loadcog(self,ctx,arg1):
        try:
            bot.load_extension('cogs.{}'.format(arg1))
            await ctx.channel.send('Loaded Extension {}.'.format(arg1))
        except Exception as e:
            exe = '{}: {}'.format(e.name,e)
            await ctx.channel.send('Unable to load Extension {}\n{}'.format(arg1,exe))

    #unloads a cog extension
    @commands.command()
    async def unloadcog(self,ctx,arg1):
        if arg1 == 'core':
            return await ctx.channel.send('{0.message.author.mention} Cannot unload core cog'.format(ctx))
        try:
            bot.unload_extension('cogs.{}'.format(arg1))
            await ctx.channel.send('Cog {} unloaded'.format(arg1))
        except Exception as e:
            exe = '{}: {}'.format(e.name,e)
            await ctx.channel.send('Unable to unload Extension {}\n{}'.format(arg1,exe))

    #restarts a cog
    @commands.command()
    async def reloadcog(self,ctx,arg1):
        try:
            bot.reload_extension('cogs.{}'.format(arg1))
            await ctx.channel.send('{} Extension Reloaded'.format(arg1))
        except Exception as e:
            exe = '{}: {}'.format(e.__name__,e)
            print(exe)
            await ctx.channel.send('Cog {} could not be reloaded: {}'.format(arg1,e.name))
    
    #restarts the bot
    @commands.command()
    async def restart(self,ctx):
        try:
            print('Closing Bot.\n\n')
            await self.bot.logout()
        except:
            pass
        finally:
                os.system('py lotus.py')

    #quits the bot
    @commands.command()
    async def quit(self,ctx):
        await self.bot.logout()

    #sets server prefix
    @commands.group(invoke_without_command=True)
    async def prefix(self,ctx,args):
        if ctx.invoked_subcommand is None:
            with open('bot_config/prefixes.json','r') as f:
                data = json.load(f)
            data[str(ctx.guild.id)] = args
            with open('bot_config/prefixes.json','w') as f:
                json.dump(data,f)
            await ctx.channel.send('Server Prefix Successfully set to: {}'.format(args))
    
    #Remove a guilds set prefix
    @prefix.command()
    async def rmv(self,ctx):
        with open('bot_config/prefixes.json','r') as f:
            data = json.load(f)
        try:
            data.pop('{}'.format(ctx.guild.id),None)
            with open('bot_config/prefixes.json','w') as f:
                json.dump(data,f)
            await ctx.channel.send('Server Prefix Removed, Default Prefix: {}'.format(default_prefix))
        except Exception as e:
            await ctx.channel.send('Server had no custom prefix, Default Prefix: {}'.format(default_prefix))
        

    #makes core commands only available to the owner
    async def cog_check(self,ctx):
        if not check_owner(ctx):
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
        exe = '{}: {}'.format(e.__name__,e)
        print('Unable to load Exstension {}\n {}'.format(extention,exe))


bot.run(TOKEN)
