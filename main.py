import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import re
import requests
import shlex

load_dotenv()
TOKEN = os.getenv('BHW_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

prefix = '%'
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is up and running on {len(bot.guilds)} servers!')

# @bot.event
# async def on_error(event, *args, **kwargs):
#     print(f'{event} - {args} - {kwargs}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # makeshift prefix commands
    if message.content.startswith(prefix):
        await command_handler(message)
        return

    # TODO: more efficient link searching

    # fix broken links
    links = re.findall(r'https?://geizhals..?.?/https?%3A%2F%2Fgeizhals..?.?%2F%3Fcat%3DWL-[0-9]+', message.content)
    if links:
        links = '\n'.join([re.sub(r'https?%3A%2F%2Fgeizhals..?.?%2F%3Fcat%3D', '?cat=', link) for link in links])
        await message.reply(f'Die Nachricht enthält kaputte Geizhals-Links, hier einmal korrigiert:\n{links}')
        return

    # local/private lists
    links = re.findall(r'https?://geizhals..?.?/\?cat=WL-?[0-9]*', message.content)
    for link in links:
        # local list
        if sum([c.isdigit() for c in link]) <= 1:
            await message.reply(f'Diese Wunschliste (<{link}>) ist lokal und nicht öffentlich in deinem Account hinterlegt\nFür eine Anleitung zum Erstellen von Geizhals-Listen -> <#934229012069376071>')
            return
        
        # private list
        page = requests.get(link)
        if 'Wunschliste ist nicht vorhanden' in page.text:
            await message.reply(f'Diese Wunschliste (<{link}>) ist nicht öffentlich in deinem Account hinterlegt\nFür eine Anleitung zum Erstellen von Geizhals-Listen -> <#934229012069376071>')
            return

@bot.slash_command(name='1tbssd', description='Bens Empfehlung für 1TB SSDs')
async def ssd1tb(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten 1TB-SSDs: https://gh.de/g/q0\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='2tbssd', description='Bens Empfehlung für 2TB SSDs')
async def ssd2tb(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten 2TB-SSDs: https://gh.de/g/qP\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='4tbssd', description='Bens Empfehlung für 4TB SSDs')
async def ssd4tb(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten 4TB-SSDs: https://gh.de/g/qW\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='aio', description='Bens Empfehlung für AIO-Wasserkühlungen')
async def aio(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten AiO-Wasserkühlungen: https://gh.de/g/Xg\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='case', description='Bens Empfehlung für Gehäuse')
async def case(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten Gehäuse für guten Airflow: https://gh.de/g/XY\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='cpukühler', description='Bens Empfehlung für CPU-Kühler')
async def cpukühler(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten CPU-Luftkühler: https://gh.de/g/Xn\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='gehäuse', description='Bens Empfehlung für Gehäuse')
async def gehäuse(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten Gehäuse für guten Airflow: https://gh.de/g/XY\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='lüfter', description='Bens Empfehlung für Lüfter ohne RGB')
async def lüfter(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten Gehäuselüfter ohne RGB: https://gh.de/g/q6\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='netzteil', description='Bens Empfehlung für Netzteile')
async def netzteil(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten Netzteile: https://gh.de/g/1H\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='ram', description='Bens Empfehlung für RAM')
async def ram(ctx):
    await ctx.respond(f'Hier findet Ihr den aktuell besten RAM: https://gh.de/g/qC\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='rgblüfter', description='Bens Empfehlung für Lüfter mit RGB')
async def rgblüfter(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten RGB-Gehäuselüfter: https://gh.de/g/XQ\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='gpu-ranking', description='Leistungsranking von Grafikkarten anhand der FPS')
async def gpu_ranking(ctx, resolution: str):
    # TODO: scrape from website
    match resolution:
        case '1080p' | '1080' | 'fhd' | 'fullhd' | 'FHD' | '2k':
            f = 'assets/gpu-1080.png.webp'
        case '1440p' | '1440' | 'qhd' | 'QHD' | 'wqhd' | 'WQHD' | '2.5k' | '2,5k':
            f = 'assets/gpu-1440.png.webp'
        case '2160p' | '2160' | 'uhd' | 'UHD' | '4k':
            f = 'assets/gpu-2160.png.webp'
        case _:
            await ctx.respond(f'Unbekannte Auflösung: {resolution}', ephemeral=True, delete_after=10)
            return

    await ctx.respond('Quelle: <https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html>', file=discord.File(f))

async def command_handler(message):
    cmd = shlex.split(message.content[len(prefix):])

    match cmd:
        case ['ping']:
            await ping(message)
        case ['meta' | 'metafrage']:
            await metafrage(message)
        case ['psu']:
            await psu(message)
        case _:
            await message.reply('Unbekannter Befehl')

async def ping(message):
    await message.reply(f'pong - {int(bot.latency * 1000)}ms')

async def metafrage(message):
    embed = discord.Embed(title='Metafragen', color=discord.Color.brand_red(), url='https://wiki.tilde.fun/de/guide/questions')
    embed.add_field(name='', value='''Metafragen sind Fragen, welche oft vor einer richtigen Frage gestellt werden.

Klassische Beispiele für Metafragen sind:
- Kann mir jemand bei Monitoren helfen?
- Kennt sich hier jemand mit Tastaturen aus?

Solche Fragen verhindern eine schnelle Antwort auf die eigentliche Frage. Oft denkt jemand nicht, im Fachgebiet "gut genug" zu sein, kennt aber die Antwort und könnte trotzdem nicht antworten. Auch wenn sich jemand meldet, muss er erst auf die Antwort des Fragestellers warten, bis er antworten kann.

Stelle deine Frage direkt, ohne erstmal nach einem Experten zu suchen. Dies erspart dir Zeit und erhöht die Chance auf eine Antwort.''')

    if message.reference:
        await message.channel.send(embed=embed, reference=message.reference)
    else:
        await message.reply(embed=embed)
    return

async def psu(message):
    embed = discord.Embed(title='Tier A Netzteile (nach cultists.network)', color=discord.Color.blue(), url='https://cultists.network/140/psu-tier-list/')
    embed.add_field(name='1000+W', value='https://geizhals.de/?cat=WL-2652571')
    embed.add_field(name='800+W', value='https://geizhals.de/?cat=WL-2652570')
    embed.add_field(name='700+W', value='https://geizhals.de/?cat=WL-2652569')
    embed.add_field(name='600+W', value='https://geizhals.de/?cat=WL-2652568')
    embed.add_field(name='500+W', value='https://geizhals.de/?cat=WL-2652566')
    embed.add_field(name='Seasonic', value='https://geizhals.de/?cat=WL-2678896')
    await message.reply(embed=embed)



# TODO: cpu ranking links thw

bot.run(TOKEN)
