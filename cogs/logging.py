import discord, mysql.connector
from cogs.cog_config.mysqldata import sqlconfig
from mysql.connector import Error
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





    #refresh the connection to the server
    @commands.command(brief='Refreshes the connection to the mysql server')
    async def refresh(self,ctx):
        self.connection.close()
        self.connection = dbinit()
        pass

    #listener for dms sent to the bot
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