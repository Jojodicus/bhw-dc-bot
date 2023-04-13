#! /usr/bin/env python3

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import re
import requests
import shlex
from bs4 import BeautifulSoup
import json

load_dotenv()
TOKEN = os.getenv('BHW_TOKEN')
API_COOKIE = os.getenv('GH_API_COOKIE')

intents = discord.Intents.default()
intents.message_content = True

prefix = '%'
bot = discord.Bot(intents=intents)

async def send_msg_to_dev(msg):
    jojo = await bot.fetch_user(226054688368361474) # Jojodicus#0001, bot dev
    await jojo.send(msg)

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

    # local/private lists
    locals = re.findall(r'https?://geizhals..?.?/wishlists/local-[0-9]+', message.content)
    if locals:
        await message.reply(f'Diese Wunschliste (<{locals[0]}>) ist lokal und nicht öffentlich in deinem Account hinterlegt\nFür eine Anleitung zum Erstellen von Geizhals-Listen -> <#934229012069376071>')
        return
    private = re.findall(r'https?://geizhals..?.?/wishlists/[0-9]+', message.content)
    for link in private:
        page = re.sub(r'https?://geizhals..?.?/wishlists/', 'https://geizhals.de/api/usercontent/v0/wishlist/', link)
        page = requests.get(page, headers={'cookie': API_COOKIE})
        if r'{"response":null}' in page.text:
            await message.reply(f'Diese Wunschliste (<{link}>) ist nicht öffentlich in deinem Account hinterlegt\nFür eine Anleitung zum Erstellen von Geizhals-Listen -> <#934229012069376071>')
            return
        if r'{"code":403,"error":"Authentication failed"}' in page.text:
            await send_msg_to_dev(f'API Cookie für Geizhals ist abgelaufen, bitte erneuern: {API_COOKIE}')
            # TODO: DM to bot sets new api cookie

    """ LEGACY
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
        if 'STATUS Code: 403 - Forbidden' in page.text:
            await message.reply(f'Diese Wunschliste (<{link}>) ist nicht öffentlich in deinem Account hinterlegt\nFür eine Anleitung zum Erstellen von Geizhals-Listen -> <#934229012069376071>')
            return
    """

def has_role_or_higher(user, rolename, guild):
    rns = list(map(lambda x: x.name, guild.roles))

    if rolename not in rns:
            return True

    highest = user.roles[-1].name
    return rns.index(highest) > rns.index(rolename)

def is_atleast(rolename):
    async def predicate(ctx):
        return has_role_or_higher(ctx.author, rolename, ctx.guild)
    return commands.check(predicate)

minRole = 'Silber'

@bot.slash_command(name='1tbssd', description='Bens Empfehlung für 1TB SSDs')
@is_atleast(minRole)
async def ssd1tb(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten 1TB-SSDs: https://gh.de/g/q0\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='2tbssd', description='Bens Empfehlung für 2TB SSDs')
@is_atleast(minRole)
async def ssd2tb(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten 2TB-SSDs: https://gh.de/g/qP\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='4tbssd', description='Bens Empfehlung für 4TB SSDs')
@is_atleast(minRole)
async def ssd4tb(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten 4TB-SSDs: https://gh.de/g/qW\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='aio', description='Bens Empfehlung für AIO-Wasserkühlungen')
@is_atleast(minRole)
async def aio(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten AiO-Wasserkühlungen: https://gh.de/g/Xg\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='case', description='Bens Empfehlung für Gehäuse')
@is_atleast(minRole)
async def case(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten Gehäuse für guten Airflow: https://gh.de/g/XY\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='cpukühler', description='Bens Empfehlung für CPU-Kühler')
@is_atleast(minRole)
async def cpukühler(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten CPU-Luftkühler: https://gh.de/g/Xn\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='gehäuse', description='Bens Empfehlung für Gehäuse')
@is_atleast(minRole)
async def gehäuse(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten Gehäuse für guten Airflow: https://gh.de/g/XY\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='lüfter', description='Bens Empfehlung für Lüfter ohne RGB')
@is_atleast(minRole)
async def lüfter(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten Gehäuselüfter ohne RGB: https://gh.de/g/q6\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='netzteil', description='Bens Empfehlung für Netzteile')
@is_atleast(minRole)
async def netzteil(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten Netzteile: https://gh.de/g/1H\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='ram', description='Bens Empfehlung für RAM')
@is_atleast(minRole)
async def ram(ctx):
    await ctx.respond(f'Hier findet Ihr den aktuell besten RAM: https://gh.de/g/qC\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

@bot.slash_command(name='rgblüfter', description='Bens Empfehlung für Lüfter mit RGB')
@is_atleast(minRole)
async def rgblüfter(ctx):
    await ctx.respond(f'Hier findet Ihr die aktuell besten RGB-Gehäuselüfter: https://gh.de/g/XQ\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

# todo: add rt
def find_image(resolution: str) -> str:
    data = requests.get('https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html')
    soup = BeautifulSoup(data.text, 'html.parser')
    for s in soup.find_all('script', type='text/javascript'):
        if not 'GPU benchmarks hierarchy rasterization generational performance chart' in s.text:
            continue
        for line in s.text.split('\n'):
            if not 'var data = ' in line:
                continue
            line = line.replace('var data = ', '')
            line = line.replace(';', '')

            data = json.loads(line)
            for row in data['galleryData']:
                img = row['image']
                if img['name'] == f'gpu-benchmarks-rast-generational-performance-chart-{resolution}.png':
                    return img['src']

@bot.slash_command(name='gpu-ranking', description='Leistungsranking von Grafikkarten anhand der FPS. Optionen: 1080p, 1440p, 2160p')
@is_atleast(minRole)
async def gpu_ranking(ctx, resolution: str):
    # TODO: scrape from website
    match resolution:
        case '1080p' | '1080' | 'fhd' | 'fullhd' | 'FHD' | '2k':
            cdn = find_image('1080p-ult')
        case '1440p' | '1440' | 'qhd' | 'QHD' | 'wqhd' | 'WQHD' | '2.5k' | '2,5k':
            cdn = find_image('1440p-ult')
        case '2160p' | '2160' | 'uhd' | 'UHD' | '4k':
            cdn = find_image('2160p-ult')
        case _:
            await ctx.respond(f'Unbekannte Auflösung: {resolution}', ephemeral=True, delete_after=10)
            return
    
    # save file if not already cached
    filename = '.cache' + cdn[cdn.rfind('/'):]
    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            f.write(requests.get(cdn).content)

    await ctx.respond('Quelle: <https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html>', file=discord.File(filename))

@ssd1tb.error
@ssd2tb.error
@ssd4tb.error
@aio.error
@case.error
@cpukühler.error
@gehäuse.error
@lüfter.error
@netzteil.error
@ram.error
@rgblüfter.error
@gpu_ranking.error
async def insufficient_role(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.respond(f'Du brauchst mindestens die Rolle \'{minRole}\' für diesen Befehl.', ephemeral=True, delete_after=10)
    else:
        await send_msg_to_dev(f'ctx: {ctx}\n\nerror:{error}')

async def command_handler(message):
    cmd = shlex.split(message.content[len(prefix):])

    match cmd:
        case ['ping']:
            await ping(message)
        case ['meta' | 'metafrage']:
            await metafrage(message)
        case ['psu']:
            await psu(message)
        case ['ssd' | 'ssds' | '1tbssd' | '1tb-ssd' | 'ssd1tb' | 'ssd-1tb']:
            await ssd_1tb(message)
        case ['2tbssd' | '2tb-ssd' | 'ssd2tb' | 'ssd-2tb']:
            await ssd_2tb(message)
        case ['4tbssd' | '4tb-ssd' | 'ssd4tb' | 'ssd-4tb']:
            await ssd_4tb(message)
        case ['aio' | 'wasserkühlung' | 'wasserkühler']:
            await allinone(message)
        case ['case' | 'gehäuse']:
            await cases(message)
        case ['cpukühler' | 'cpu-kühler' | 'cpu-cooler']:
            await cpu_cooler(message)
        case ['lüfter' | 'fan' | 'fans']:
            await fans(message)
        case ['netzteil' | 'nt']:
            await psus(message)
        case ['ram']:
            await rams(message)
        case ['rgblüfter' | 'rgb-lüfter' | 'rgb-fan' | 'rgb-fans']:
            await rgb_fans(message)

async def ping(message):
    if message.author.guild_permissions.administrator:
        await message.reply(f'pong - {int(bot.latency * 1000)}ms')

minRole2 = 'Silber'

async def metafrage(message):
    if not has_role_or_higher(message.author, minRole2, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return

    embed = discord.Embed(title='Metafragen', color=discord.Color.blurple(), url='https://wiki.tilde.fun/de/guide/questions')
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
    if not has_role_or_higher(message.author, minRole2, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return

    embed = discord.Embed(title='Tier A Netzteile (nach cultists.network rev. 17.0f)', color=discord.Color.blurple(), url='https://cultists.network/140/psu-tier-list/')
    embed.add_field(name='1000+W', value='https://geizhals.de/?cat=WL-2652571')
    embed.add_field(name='800+W', value='https://geizhals.de/?cat=WL-2652570')
    embed.add_field(name='700+W', value='https://geizhals.de/?cat=WL-2652569')
    embed.add_field(name='600+W', value='https://geizhals.de/?cat=WL-2652568')
    embed.add_field(name='500+W', value='https://geizhals.de/?cat=WL-2652566')
    embed.add_field(name='Disclaimer:', value='Keine Garantie für Vollständigkeit und Aktualität!')
    # embed.add_field(name='Seasonic', value='https://geizhals.de/?cat=WL-2678896')
    await message.reply(embed=embed)

async def ssd_1tb(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return
    await message.reply(f'Hier findet Ihr die aktuell besten 1TB-SSDs: https://gh.de/g/q0\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

async def ssd_2tb(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return
    await message.reply(f'Hier findet Ihr die aktuell besten 2TB-SSDs: https://gh.de/g/qP\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

async def ssd_4tb(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return
    await message.reply(f'Hier findet Ihr die aktuell besten 4TB-SSDs: https://gh.de/g/qW\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

async def allinone(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return
    await message.reply(f'Hier findet Ihr die aktuell besten AiO-Wasserkühlungen: https://gh.de/g/Xg\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

async def cases(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return
    await message.reply(f'Hier findet Ihr die aktuell besten Gehäuse für guten Airflow: https://gh.de/g/XY\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

async def cpu_cooler(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return
    await message.reply(f'Hier findet Ihr die aktuell besten CPU-Luftkühler: https://gh.de/g/Xn\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

async def fans(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return
    await message.reply(f'Hier findet Ihr die aktuell besten Gehäuselüfter ohne RGB: https://gh.de/g/q6\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

async def psus(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return
    await message.reply(f'Hier findet Ihr die aktuell besten Netzteile: https://gh.de/g/1H\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

async def rams(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return
    await message.reply(f'Hier findet Ihr den aktuell besten RAM: https://gh.de/g/qC\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

async def rgb_fans(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole2}\' für diesen Befehl.')
        await m.delete(delay=10)
        return
    await message.reply(f'Hier findet Ihr die aktuell besten RGB-Gehäuselüfter: https://gh.de/g/XQ\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')

# TODO: cpu ranking links thw

bot.run(TOKEN)
