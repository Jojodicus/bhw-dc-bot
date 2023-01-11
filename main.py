import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BHW_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is up and running on {len(bot.guilds)} servers!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # TODO: geizhals link fix

@bot.slash_command(name="1tbssd", description="Bens Empfehlung für 1TB SSDs")
async def ssd1tb(ctx):
    await ctx.respond(f"Hier findet Ihr die aktuell besten 1TB-SSDs: https://gh.de/g/q0\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")

@bot.slash_command(name="2tbssd", description="Bens Empfehlung für 2TB SSDs")
async def ssd2tb(ctx):
    await ctx.respond(f"Hier findet Ihr die aktuell besten 2TB-SSDs: https://gh.de/g/qP\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")

@bot.slash_command(name="4tbssd", description="Bens Empfehlung für 4TB SSDs")
async def ssd4tb(ctx):
    await ctx.respond(f"Hier findet Ihr die aktuell besten 4TB-SSDs: https://gh.de/g/qW\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")

@bot.slash_command(name="aio", description="Bens Empfehlung für AIO-Wasserkühlungen")
async def aio(ctx):
    await ctx.respond(f"Hier findet Ihr die aktuell besten AiO-Wasserkühlungen: https://gh.de/g/Xg\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")

@bot.slash_command(name="case", description="Bens Empfehlung für Gehäuse")
async def case(ctx):
    await ctx.respond(f"Hier findet Ihr die aktuell besten Gehäuse für guten Airflow: https://gh.de/g/XY\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")

@bot.slash_command(name="cpukühler", description="Bens Empfehlung für CPU-Kühler")
async def cpukühler(ctx):
    await ctx.respond(f"Hier findet Ihr die aktuell besten CPU-Luftkühler: https://gh.de/g/Xn\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")

@bot.slash_command(name="gehäuse", description="Bens Empfehlung für Gehäuse")
async def gehäuse(ctx):
    await ctx.respond(f"Hier findet Ihr die aktuell besten Gehäuse für guten Airflow: https://gh.de/g/XY\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")

@bot.slash_command(name="lüfter", description="Bens Empfehlung für Lüfter ohne RGB")
async def lüfter(ctx):
    await ctx.respond(f"Hier findet Ihr die aktuell besten Gehäuselüfter ohne RGB: https://gh.de/g/q6\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")

@bot.slash_command(name="netzteil", description="Bens Empfehlung für Netzteile")
async def netzteil(ctx):
    await ctx.respond(f"Hier findet Ihr die aktuell besten Netzteile: https://gh.de/g/1H\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")

@bot.slash_command(name="ram", description="Bens Empfehlung für RAM")
async def ram(ctx):
    await ctx.respond(f"Hier findet Ihr den aktuell besten RAM: https://gh.de/g/qC\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")

@bot.slash_command(name="rgblüfter", description="Bens Empfehlung für Lüfter mit RGB")
async def rgblüfter(ctx):
    await ctx.respond(f"Hier findet Ihr die aktuell besten RGB-Gehäuselüfter: https://gh.de/g/XQ\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>")


bot.run(TOKEN)
