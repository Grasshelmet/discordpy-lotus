import discord, mysql.connector,typing,datetime
from cogs.cog_config.mysqldata import sqlconfig
from mysql.connector import Error,errorcode
from discord.ext import commands
from discord import Embed



#Creates the upfront connection to a server
def create_connection(host,user,password,database=None):
    connection = None
    try:
        if database!=None:
            connection = mysql.connector.connect(host = host,user=user,
                                             password=password,database=database)
            print("Connection to database {} successful".format(database))
        else:
            connection = mysql.connector.connect(host = host,user=user,
                                             passwd=password)
            print("Connection to database {} successful".format(database))
    except Error as e:
        print("Failed to connect to {0}\n Error: {1}".format(database,e))

    return connection

#creates database within a server connection
def create_database(connection,query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print ("Database created successfully")
    except Error as e:
        print("Database not created\nError: {}".format(e))

#initializes connection to server,calls create_database if needed
def dbinit():
    connection = create_connection(**sqlconfig)
    if connection == None:
        connection = create_connection(sqlconfig['host'],sqlconfig['user'],sqlconfig['password'])
        if connection != None:
            create_database(connection,'CREATE DATABASE {}'.format(sqlconfig['database']))
            connection.cmd_quit()
            return create_connection(**sqlconfig)
    else:
        return connection

#Executes not returnable query
def execute_query(connection,query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print ("Query executed successfully")
    except Error as e:
        print("Error: {}".format(e))
        raise e

#Read query,will return list of data
def execute_read_query(connection,query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print("Error: {}".format(e))

#Get table name list
def getTableName(tbname):
    logtables = {
            "commsdms":"commsdms",
            "commanddms":"commsdms",
            "plaindms":"plaindms",
            "editlogs":"editlogs",
            "editlog":"editlogs",
            "edit":"editlogs",
            "messageedits":"editlogs",
            "deletelogs":"deletelogs",
            "delete":"deletelogs"
            }

    return logtables.get(tbname,"None")

class Logging(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.last_member=None
        self.connection = dbinit()

    #destrutcor
    def __del__(self):
        print('Closing logging cog')
        if self.connection != None:
            self.connection.cmd_quit()
        self.connection = None

    #connection check
    async def check_connection(ctx):
        if ctx.cog.connection == None:
            await ctx.send('No sqlserver connected to')
            return False
        else:
            return True


    #refresh the connection to the server
    @commands.command(brief='Refreshes the connection to the mysql server')
    async def refresh(self,ctx):
        if self.connection != None:
            self.connection.cmd_quit()
            self.connection = None
        self.connection = dbinit()
        if self.connection == None:
            await ctx.send('Connection to database {} failed'.format(sqlconfig['database']))
        else:
            await ctx.send('Connection to database {} successful'.format(sqlconfig['database']))

    #closes the connection to the server
    @commands.command(brief='Closes the connection to the mysql server')
    async def close(self,ctx):
        if self.connection != None:
            self.connection.cmd_quit()
            self.connection = None
            await ctx.send('Connection to server closed')
        else:
            await ctx.send('No connection available to close, hurray?')

    @commands.command(brief='Checks if cog is connected to server/database')
    async def check(self,ctx):
        if self.connection == None:
            await ctx.send('No server connection established')
        else:
            await ctx.send('Cog is connected to server: {} database: {}'.format(self.connection.server_host,self.connection._database))

    #adds channel to database table
    @commands.command(brief='adds a certain channel to a database table',aliases=['setchannel'])
    @commands.check(check_connection)
    async def addchannel(self,ctx,tbname,channel : typing.Union[discord.TextChannel, int]=None):
        if channel == None:
            channel = ctx.channel.id
        elif type(channel) is int:
            channel = self.bot.get_channel(channel)
            if channel == None:
                await ctx.send('Channel could not be found')
                return
        if type(channel) is not int:
            channel = channel.id

        tbname = getTableName(tbname)
       
        insert_channel=""
        create_table=""

        if tbname == "None":
            await ctx.send('Invalid database table')
            return
        #What to set insert channel and create table to if edit logs
        elif tbname == "editlogs" or tbname == "deletelogs":
            insert_channel = ("""INSERT INTO {} 
                                  (guildid,chanid)
                                  VALUES ({},{})""".format(tbname,ctx.guild.id,channel)

                                  )
            create_table = """
                CREATE TABLE IF NOT EXISTS {} (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    guildid VARCHAR(18),
                    chanid VARCHAR(18)
                    ) ENGINE=InnoDB
                """.format(tbname)
        #What to set for plain text and commands sent to bot dms
        elif tbname == "plaindms" or tbname == "commsdms":
            insert_channel = ("""INSERT INTO {} 
                                  (chanid)
                                  VALUES ({})""".format(tbname,channel)

                                  )
            create_table = """
                CREATE TABLE IF NOT EXISTS {} (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    chanid VARCHAR(18)
                    ) ENGINE=InnoDB
                """.format(tbname)


        try:

            #insert channel into table
            execute_query(self.connection,insert_channel)

        except mysql.connector.Error as e:
            try:
                if e.errno == errorcode.ER_NO_SUCH_TABLE:
                    #create table
                    execute_query(self.connection,create_table)

                    #insert channel into table
                    execute_query(self.connection,insert_channel)
            except Error as e:
                await ctx.send('Failed to add channel\n Error: {}'.format(e.__cause__))
                return

        await ctx.send('{} added to {} database'.format(self.bot.get_channel(channel).mention,tbname))

    @commands.command(brief='Drops a Channel Id from a table')
    @commands.check(check_connection)
    async def rmvchannel(self,ctx,tbname,channel : typing.Union[discord.TextChannel, int]=None):
        if channel == None:
            channel = ctx.channel.id
        elif type(channel) is int:
            channel = self.bot.get_channel(channel)
            if channel == None:
                await ctx.send('Channel could not be found')
                return
        if type(channel) is not int:
            channel = channel.id

        tbname = getTableName(tbname)
        
        if tbname == "None":
            await ctx.send('Invalid database table')
            return

        try:
            delete_channel = ("""DELETE FROM {} WHERE chanid ={}""".format(tbname,channel))
            execute_query(self.connection,delete_channel)
        except Error as e:
            await ctx.send('Failed to add channel\n Error: {}'.format(e.__cause__))
            return

        await ctx.send('{} Removed from {} database'.format(self.bot.get_channel(channel).mention,tbname))

    #listener for dms sent to the bot
    @commands.Cog.listener('on_message')
    async def botdms(self,message):
        if not (isinstance(message.channel,discord.DMChannel)):
            return
        if message.author.id == self.bot.user.id:
            return
        

        
        
        mesEmbed = Embed(title='{0}: {0.id}'.format(message.author),type='rich',color=0xd010d0,timestamp=message.created_at)
        mesEmbed.set_thumbnail(url=message.author.avatar_url)
        mesEmbed.add_field(name='__Message:__',value=message.content,inline=False)

        if str(message.content).startswith(tuple(await self.bot.get_prefix(message))):
            select_plain = "SELECT chanid FROM commsdms"
            plainchans = execute_read_query(self.connection,select_plain)

            for chan in plainchans:
                channel = self.bot.get_channel(int(chan[0]))
                await channel.send(embed=mesEmbed)
        else:
            select_plain = "SELECT chanid FROM plaindms"
            plainchans = execute_read_query(self.connection,select_plain)

            for chan in plainchans:
                channel = self.bot.get_channel(int(chan[0]))
                await channel.send(embed=mesEmbed)

    @commands.Cog.listener('on_raw_message_edit')
    async def messedit(self,payload):
        ctxchan = self.bot.get_channel(payload.channel_id)
        #retrieves before and after messages, before will get set to none if not in cache
        before = payload.cached_message
        after = await ctxchan.fetch_message(payload.message_id)

        try:
            #list of channels for the guild from sql database
            select_edit = "SELECT chanid FROM editlogs WHERE guildid = {}".format(after.guild.id)
            editchans = execute_read_query(self.connection,select_edit)
            
            #create embed, if before is none, doesn't include the before field
            editEmbed = Embed(title='{0}: {0.id}'.format(after.author),type='rich',color=0xd010d0,timestamp=after.edited_at,description="[Click here for context.]({})".format(after.jump_url))
            editEmbed.set_thumbnail(url=after.author.avatar_url)
            if before != None:
                editEmbed.add_field(name='__Before Message:__',value=before.content,inline=False)
            editEmbed.add_field(name='__Edited Message:__',value=after.content,inline=False)

            #sends the embed to list of channels
            for chan in editchans:
                channel = self.bot.get_channel(int(chan[0]))
                await channel.send(embed=editEmbed)
        except Error as e:
            print("{}: {}".format(e,e.__cause__))

    @commands.Cog.listener('on_raw_message_delete')
    async def messdel(self,payload):
        ctxchan = self.bot.get_channel(payload.channel_id)
        before = payload.cached_message

        try:
            #list of channels from the sql database
            select_del = "SELECT chanid FROM deletelogs WHERE guildid = {}".format(payload.guild_id)
            delchans = execute_read_query(self.connection,select_del)

            #create embed,will record that a message was deleted if not in chache,but no other data
            if before == None:
                delEmbed = Embed(title='Message Deleted',type='rich',color=0xd020d0,timestamp=datetime.datetime.utcnow(),description = 'Message deleted in {}'.format(ctxchan.mention))
            else:
                delEmbed = Embed(title='{0}: {0.id}'.format(before.author),type='rich',color=0xd010d0,timestamp=datetime.datetime.utcnow(),description="[Click here for context.]({})".format(before.jump_url))
                delEmbed.add_field(name='__Deleted Message__',value=before.content,inline =False)

            #sends the embed to list of channels
            for chan in delchans:
                channel = self.bot.get_channel(int(chan[0]))
                await channel.send(embed=delEmbed)
        except Error as e:
            print('{}: {}'.format(e,e.__cause__))
        

def setup(bot):
    bot.add_cog(Logging(bot))