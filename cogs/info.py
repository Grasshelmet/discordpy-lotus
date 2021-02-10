import discord,os
from discord.ext import commands
from discord import Embed

class Info(commands.Cog):
    def __init__(self,bot):
        bot.remove_command('help')
        self.bot = bot
        self._last_member = None
    
    @commands.command(brief='Displays the permissions of a member in that guild.')
    async def perms(self,ctx,member : discord.Member):
        pers = member.guild_permissions
        prin = 'Permissions for {0} in Guild {1}:\n'.format(member,ctx.guild)
        for pe in pers:
            prin = prin + '\t{0[0]}: {0[1]}\n'.format(pe)
        await ctx.channel.send('```{0}```'.format(prin))


    #displays names on all this bots cogs and whether they are loaded or not.
    @commands.command(brief='Shows Loaded and unloaded cogs')
    async def cogs(self,ctx):
        loadedcogs = dict(self.bot.cogs)

        lcogs =''
        for key in loadedcogs.keys():
            if key.lower() == 'core':
                lcogs = 'core'
            else:
                lcogs = ','.join([lcogs,key.lower()])

        cogembed = Embed(title='Cogs:',type='rich',color=0x4080A0)
        cogembed.add_field(name='Loaded Cogs:',value=lcogs,inline=True)

        #get names of all cogs in cogs folder 
        path = 'cogs'
        uncogs = ''
        for filename in os.listdir(path):
            if filename.endswith('.py')and not loadedcogs.__contains__(filename.replace('.py','').capitalize()):
                uncogs = ','.join([uncogs,filename.replace('.py','')])
        uncogs = uncogs.replace(',','',1)
        
        cogembed.add_field(name='Unloaded Cogs:',value=uncogs,inline=False)
        await ctx.send(embed=cogembed)


    @commands.command(invoke_without_command=True,brief='Help Function,use {prefix}help {command} for help on a command')
    async def help(self,ctx,*args):
        cogs = dict(self.bot.cogs)
        

        if not args:
            comlist=''
            for cog in cogs.keys():
                comlist+= '**__' + cog + '__**:\n'
                for com in cogs.get(cog).get_commands():
                    bs=''
                    if com.brief != None:
                        bs = ': '+ str(com.brief)
                    
                    comlist+= '**' + str(com.name) + '**' + bs + '\n'
                comlist += '\n'
            await ctx.send(''+comlist+'')
            return

        #if argument was supplied
        else:

            comlist =[]
            foundcom=None
            for cog in cogs.keys():
                for com in (cogs.get(cog).walk_commands()):
                    if com.name == args[0]:
                        foundcom = com
                        break
            if foundcom == None:
                await ctx.send('Command not found.')
                return

            comstr=''
            if foundcom.description:
                comstr = str(foundcom.description)
            else:
                comstr = str(foundcom.brief)


            comBed = Embed(title='{}:'.format(foundcom),type='rich',color=0x4080A0)
            comBed.add_field(name='Description:',value=comstr,inline=True)

            
            try:
                sublist=''
                for com in foundcom.walk_commands():
                    if com.parent():
                        sublist += com.name + ': ' + str(com.brief) + '\n'
                comBed.add_field(name='Subcommands',value=sublist,inline=False)
            except:
                pass

            await ctx.send(embed=comBed)            
   

def setup(bot):
    bot.add_cog(Info(bot))
