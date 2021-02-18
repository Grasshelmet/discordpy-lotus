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
        self.connection.close()

    async def check_connection(ctx):
        if ctx.cog.connection == None:
            ctx.send('No sqlserver connected to')
            return False
        else:
            return True


    #refresh the connection to the server
    @commands.command(brief='Refreshes the connection to the mysql server')
    async def refresh(self,ctx):
        self.connection.close()
        self.connection = dbinit()
        if self.connection == None:
            ctx.send('Connection to database {} failed'.format(sqlconfig['database']))
        else:
            ctx.send('Connection to database {} successful'.format(sqlconfig['database']))

    @commands.command(brief='adds a certain channel to a logging table')
    @commands.check(check_connection)
    async def addchannel(self,ctx,tbname,channel : typing.Union[discord.TextChannel, int]=None):
        if type(channel) is not int:
            channel = channel.id
        if channel == None:
            ctx.send('Channel unable to be found')
            return

        try:

            #insert channel into table
            insert_channel = ("""INSERT INTO {} 
                              (chanid)
                              VALUES ({})""".format(tbname,channel)

                              )
            execute_query(self.connection,insert_channel)
        except mysql.connector.Error as e:
            if e.errno == errorcode.ER_NO_SUCH_TABLE:
                #creates table
                create_table = """
                CREATE TABLE IF NOT EXISTS {} (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    chanid VARCHAR(18)
                    ) ENGINE=InnoDB
                """.format(tbname)
                execute_query(self.connection,create_table)

                #insert channel into table
                insert_channel = ("""INSERT INTO {} 
                              (chanid)
                              VALUES ({})""".format(tbname,channel)

                              )
                execute_query(self.connection,insert_channel)

    @commands.command(brief='Drops a Channel Id from a table')
    @commands.check(check_connection)
    async def rmvchannel(self,ctx,tbname,channel : typing.Union[discord.TextChannel, int]=None):
        if type(channel) is not int:
            channel = channel.id
        if channel == None:
            ctx.send('Channel unable to be found')
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


        

def setup(bot):
    bot.add_cog(Logging(bot))