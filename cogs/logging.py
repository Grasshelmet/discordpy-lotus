import discord, mysql.connector
from mysql.connector import Error
from discord.ext import commands
from discord import Embed


def create_connection(host_name,user_name,user_password,db_name):
    connection = None
    try:
        connection = mysql.connector.connect(host = host_name,user=user_name,
                                             passwd=user_password,database=db_name)
        print("Connection to database {} successful".format(db_name))
    except Error as e:
        print("Failed to connect to {0}\n Error: {1}".format(db_name,e))

        return connection

def create_database(connection,query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print ("Database created successfully")
    except Error as e:
        print("Database not created\nError: {}".format(e))

class Logging(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.last_member=None
        self.connection = create_connection("localhost","root","")

    #listenr for dms sent to the bot
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