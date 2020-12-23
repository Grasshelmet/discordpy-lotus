import discord,random
from discord.ext import commands


class Card():
    def __init__(self,suit,value):
        self.suit = suit
        self.value = value

class Deck():
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        for s in ['Clubs','Diamonds','Hearts','Spades']:
            for v in ['Ace','2','3','4','5','6','7','8','9','10','Jack','Queen','King']:
                self.cards.append(Card(s,v))

    def shuffle(self):
        for i in range(len(self.cards) - 1,0,-1):
            r = random.randint(0,i)
            self.cards[i],self.cards[r] = self.cards[r],self.cards[i]

    async def show(self,channel):
        out = "```Deck:"
        for c in self.cards:
            cs = '\n{} of {}'.format(c.value,c.suit)
            out += cs
        out += "```"
        await channel.send(out)

        
class Games(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self._last_member = None
        self.black_jack_deck = Deck()

    #create a blackjack game
    @commands.group(invoke_without_command = True,aliases=['blj'])
    async def blackjack(self,ctx):
        ogauthor = ctx.message.author

        description ='Also known as twenty-one. Each player is dealt one card face up and one face down.'
        description += 'The goal is to get to 21 without going over. Face cards are worth 10,and an ace is either 1 or 11.'
        description += 'The dealer will give you your cards,then every turn you can pass or hit for another card.'
        description += 'If you go over 21, you automatically lose.'

        bjem = discord.Embed(title='BlackJack',description=description,color=0xd02030)

        msg = await ctx.channel.send(embed=bjem)

        reactions =['⬆️','✅','\N{CROSS MARK}']

        for react in reactions:
            await msg.add_reaction(react)

        try:
            msgFlag= False
            while not msgFlag:
                reaction,user = await self.bot.wait_for('reaction_add',check = lambda reaction,user : user == ctx.author and str(reaction.emoji) in ['✅','\N{CROSS MARK}'])
                if reaction.message.id == msg.id:
                    msgFlag = True

        except Exception as e:
            pass
        else:
            
            if str(reaction.emoji) == '\N{CROSS MARK}':
                await msg.delete()
            elif str(reaction.emoji) == '✅':
                msg = await ctx.fetch_message(msg.id)
                for re in msg.reactions:
                    if str(re.emoji) == '⬆️':
                        playre = re
                        reactUsers = await playre.users().flatten()

                playin= []
                for use in reactUsers:
                    if use.bot==False:
                        await ctx.channel.send('{} is playing.'.format(use))
                        playin.append(use)
 


    #Shows the blackjack deck
    @blackjack.command(aliases=['sho'])
    async def show(self,ctx):
        await self.black_jack_deck.show(ctx.channel)

    #Shuffles the blackjack deck
    @blackjack.command(aliases=['shu'])
    async def shuffle(self,ctx,arg=1):
        for i in range(arg):
            self.black_jack_deck.shuffle()
        await ctx.channel.send('The Blackjack deck has been shuffled')

def setup(bot):
    bot.add_cog(Games(bot))
