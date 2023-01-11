import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BHW_TOKEN')

# bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

# @bot.event
# async def on_ready():
#     print(f'{bot.user} has connected to Discord!')

# @bot.command(name='ping')
# async def ping(ctx):
#     print('pong')
#     await ctx.send('pong')


# bot.run(TOKEN)

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == 'ping':
        await message.channel.send('pong')

client.run(TOKEN)