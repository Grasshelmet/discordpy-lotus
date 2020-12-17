import discord,os
from discord.ext import commands
from discord import Embed

class Info(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self._last_member = None
    
    @commands.command()
    async def perms(self,ctx,member : discord.Member):
        pers = member.guild_permissions
        prin = 'Permissions for {0} in Guild {1}:\n'.format(member,ctx.guild)
        for pe in pers:
            prin = prin + '\t{0[0]}: {0[1]}\n'.format(pe)
        await ctv.channel.send('```{0}```'.format(prin))

    #displays names on all this bots cogs and whether they are loaded or not.
    @commands.command()
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

def setup(bot):
    bot.add_cog(Info(bot))