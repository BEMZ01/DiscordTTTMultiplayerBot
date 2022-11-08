import discord
from discord import ApplicationCommand
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import pandas as pd

load_dotenv()

bot = discord.Bot()
games = []


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_message(message):
    global games
    # check file /dev/TTTbot/searching.csv for a list of users who are searching for a game
    # if the user is in the list, send a message to the user and remove them from the list
    f = pd.read_csv(f"~/.TTTbot/searching.csv")
    if len(f['id']) > 2:
        if message.author.id == f['id'][0]:
            player1 = f['id'][0]
            player2 = f['id'][1]
            await message.channel.send(f"Your opponent is {f['id'][1]}")
            f = f.drop([0, 1])
            f.to_csv(f"~/.TTTbot/searching.csv", index=False)
            # start a game between the two players
            print(f"Starting a game between {player1.name} and {player2.name}")
            games.append(TicTacToe(bot, player1, player2).startGame())


@bot.slash_command(name="search", description="Search for a game of Tic Tac Toe")
async def search(ctx):
    # test if the user is already in the list
    f = pd.read_csv(f"~/.TTTbot/searching.csv")
    if ctx.author.id in f['id'].values:
        # remove from list
        f = f[f.id != ctx.author.id]
        f.to_csv(f"~/.TTTbot/searching.csv", index=False)
        await ctx.respond("You have been removed from the queue.", delete_after=5)
    else:
        # add to list
        f = f.concat({'id': ctx.author.id}, ignore_index=True)
        f.to_csv(f"~/.TTTbot/searching.csv", index=False)
        await ctx.respond("You have been added to the queue. I will DM you when you have been matched with a player.", delete_after=10)


class TicTacToe(commands.Cog):
    def __init__(self, bot, player1, player2):
        self.bot = bot
        self.player1 = player1
        self.player1_board = None
        self.player2 = player2
        self.player2_board = None
        self.board = ["0", "0", "0", "0", "0", "0", "0", "0", "0"]
        self.winning_positions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8],
                                  [2, 4, 6]]
        self.turn = random.choice([self.player1, self.player2])

    async def sendMessage(self, message):
        await self.player1.dm_channel.send(message)
        await self.player2.dm_channel.send(message)

    async def getEmbed(self):
        embed = discord.Embed(title="TicTacToe", description="Use the numbers to place your mark.")
        lboard = self.board.copy()
        for x in range(0, len(lboard)):
            lboard[x] = lboard[x].replace("0", "⬜").replace("1", "❌").replace("2", "⭕")
        embed.add_field(name="⠀", value=f"{lboard[0]}⠀{lboard[1]}⠀{lboard[2]}", inline=False)
        embed.add_field(name="⠀", value=f"{lboard[3]}⠀{lboard[4]}⠀{lboard[5]}", inline=False)
        embed.add_field(name="⠀", value=f"{lboard[6]}⠀{lboard[7]}⠀{lboard[8]}", inline=False)
        if self.turn == 1:
            embed.set_footer(text=f"{self.player1.name} (Player 1)'s turn.")
        elif self.turn == 2:
            try:
                embed.set_footer(text=f"{self.player2.name} (Player 2)'s turn.")
            except AttributeError:
                embed.set_footer(text=f"{self.player2} (Player 2)'s turn.")
        return embed

    async def sendBoard(self):
        await self.player1_board.edit(embed=await self.getEmbed())
        await self.player2_board.edit(embed=await self.getEmbed())

    async def addReactions(self):
        for i in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]:
            await self.player1_board.add_reaction(i)
            await self.player2_board.add_reaction(i)

    async def startGame(self):
        self.player1_board = await self.player1.dm_channel.send("You are playing Tic Tac Toe against " +
                                                                self.player2.name)
        self.player2_board = await self.player2.dm_channel.send("You are playing Tic Tac Toe against " +
                                                                self.player1.name)
        await self.addReactions()
        await self.sendBoard()


bot.run(os.getenv('DISCORD_TOKEN'))
