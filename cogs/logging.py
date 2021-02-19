import discord, mysql.connector,typing
from cogs.cog_config.mysqldata import sqlconfig
from mysql.connector import Error,errorcode
from discord.ext import commands
from discord import Embed




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

def create_database(connection,query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print ("Database created successfully")
    except Error as e:
        print("Database not created\nError: {}".format(e))

def dbinit():
    connection = create_connection(**sqlconfig)
    if connection == None:
        connection = create_connection(sqlconfig['host'],sqlconfig['user'],sqlconfig['password'])
        if connection != None:
            create_database(connection,'CREATE DATABASE {}'.format(sqlconfig['database']))
            connection.close()
            return create_connection(**sqlconfig)
    else:
        return connection

def execute_query(connection,query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print ("Query executed successfully")
    except Error as e:
        print("Error: {}".format(e))
        raise e

def execute_read_query(connection,query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print("Error: {}".format(e))



class Logging(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.last_member=None
        self.connection = dbinit()

    def __del__(self):
        print('Closing logging cog')
        self.connection.cmd_quit()
        self.connection = None

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

    @commands.command(brief='Closes the connection to the mysql server')
    async def close(self,ctx):
        self.connection.cmd_quit()
        self.connection = None

    @commands.command(brief='Checks if cog is connected to server/database')
    async def check(self,ctx):
        if self.connection == None:
            await ctx.send('No server connection established')
        else:
            await ctx.send('Cog is connected to server: {} database: {}'.format(self.connection.server_host,self.connection._database))

    @commands.command(brief='adds a certain channel to a logging table')
    @commands.check(check_connection)
    async def addchannel(self,ctx,tbname,channel : typing.Union[discord.TextChannel, int]=None):
        if type(channel) is not int:
            channel = channel.id
        if channel == None:
            await ctx.send('Channel unable to be found')
            return

        logtables = {
            "commsdms":"commsdms",
            "commanddms":"commsdms",
            "plaindms":"plaindms",
            "editlogs":"editlogs",
            "editlog":"editlogs",
            "messageedits":"editlogs"
            }

        tbname = logtables.get(tbname,"None")

        insert_channel=""
        create_table=""

        if tbname == "None":
            await ctx.send('Invalid database table')
            return
        #What to set insert channel and create table to if edit logs
        elif tbname == "editlogs":
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


        try:

            #insert channel into table
            execute_query(self.connection,insert_channel)

        except mysql.connector.Error as e:
            if e.errno == errorcode.ER_NO_SUCH_TABLE:
                #create table
                execute_query(self.connection,create_table)

                #insert channel into table
                execute_query(self.connection,insert_channel)

    @commands.command(brief='Drops a Channel Id from a table')
    @commands.check(check_connection)
    async def rmvchannel(self,ctx,tbname,channel : typing.Union[discord.TextChannel, int]=None):
        if type(channel) is not int:
            channel = channel.id
        if channel == None:
            await ctx.send('Channel unable to be found')
            return

        logtables = {
            "commsdms":"commsdms",
            "commanddms":"commsdms",
            "plaindms":"plaindms",
            "editlogs":"editlogs",
            "messageedits":"editlogs"
            }

        
        tbname = logtables.get(tbname,"None")
        
        if tbname == "None":
            await ctx.send('Invalid database table')
            return


        delete_channel = ("""DELETE FROM {} WHERE chanid ={}""".format(tbname,channel))
        execute_query(self.connection,delete_channel)

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

        @commands.Cog.listener('on_message_edit')
        async def messedit(self,before,after):
            try:
                select_edit = "SELECT chanid FROM commsdms"
                plainchans = execute_read_query(self.connection,select_edit)

                for chan in plainchans:
                    channel = self.bot.get_channel(int(chan[0]))
                    await channel.send(embed=mesEmbed)
            except:
                pass
        

def setup(bot):
    bot.add_cog(Logging(bot))