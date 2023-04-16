#! /usr/bin/env python3

import os
import sys
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

# minimum role to use commands
minRole = 'Silber'

async def send_msg_to_dev(msg):
    jojo = await bot.fetch_user(226054688368361474) # Jojodicus#0001, bot dev
    await jojo.send(msg)


@bot.event
async def on_ready():
    print(f'{bot.user} is up and running on {len(bot.guilds)} servers!')


@bot.event
async def on_application_command_error(ctx, error):
    await send_msg_to_dev(f'Error in command {ctx.command.name}:\n{ctx}\n{error}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # makeshift prefix commands
    if message.content.startswith(prefix):
        await command_handler(message)
        return

    # Ben pings
    if '<@234720287449546753>' in message.content:
        embed = discord.Embed(title='Ben pingen', color=discord.Color.blurple())
        embed.add_field(name='', value='''Bitte beachte, dass es nicht erwünscht ist, Ben in Nachrichten zu erwähnen. Er erhält täglich viele Pings und Privatnachrichten und kann nicht jedem antworten. Wenn du Ben kontaktieren möchtet, solltest du das über den Twitch-Chat tun.
Wir bitten daher, Ben (wenn überhaupt) nur in dringlichen Situationen zu pingen, oder wenn dies explizit gewünscht ist. Weitere Informationen dazu findest du im <#925137616481947678>''')
        await message.reply(embed=embed)

    # TODO: more efficient link searching

    # local/private lists
    locals = re.findall(r'https?://geizhals..?.?/wishlists/local-[0-9]+', message.content)
    if locals:
        await message.reply(f'Diese Wunschliste (<{locals[0]}>) ist lokal und nicht öffentlich in deinem Account hinterlegt.\nFür eine Anleitung zum Erstellen von Geizhals-Listen -> <#934229012069376071>')
        return
    private = re.findall(r'https?://geizhals..?.?/wishlists/[0-9]+', message.content)
    for link in private:
        page = re.sub(r'https?://geizhals..?.?/wishlists/', 'https://geizhals.de/api/usercontent/v0/wishlist/', link)
        page = requests.get(page, headers={'cookie': API_COOKIE})
        if r'{"response":null}' in page.text:
            await message.reply(f'Diese Wunschliste (<{link}>) ist nicht öffentlich in deinem Account hinterlegt.\nFür eine Anleitung zum Erstellen von Geizhals-Listen -> <#934229012069376071>')
            return
        if r'{"code":403,"error":"Authentication failed"}' in page.text:
            await send_msg_to_dev(f'API Cookie für Geizhals ist abgelaufen, bitte erneuern: {API_COOKIE}')
            # TODO: DM to bot sets new api cookie

    # LEGACY
    # # fix broken links
    # links = re.findall(r'https?://geizhals..?.?/https?%3A%2F%2Fgeizhals..?.?%2F%3Fcat%3DWL-[0-9]+', message.content)
    # if links:
    #     links = '\n'.join([re.sub(r'https?%3A%2F%2Fgeizhals..?.?%2F%3Fcat%3D', '?cat=', link) for link in links])
    #     await message.reply(f'Die Nachricht enthält kaputte Geizhals-Links, hier einmal korrigiert:\n{links}')
    #     return

    # # local/private lists
    # links = re.findall(r'https?://geizhals..?.?/\?cat=WL-?[0-9]*', message.content)
    # for link in links:
    #     # local list
    #     if sum([c.isdigit() for c in link]) <= 1:
    #         await message.reply(f'Diese Wunschliste (<{link}>) ist lokal und nicht öffentlich in deinem Account hinterlegt.\nFür eine Anleitung zum Erstellen von Geizhals-Listen -> <#934229012069376071>')
    #         return
        
    #     # private list
    #     page = requests.get(link)
    #     if 'STATUS Code: 403 - Forbidden' in page.text:
    #         await message.reply(f'Diese Wunschliste (<{link}>) ist nicht öffentlich in deinem Account hinterlegt.\nFür eine Anleitung zum Erstellen von Geizhals-Listen -> <#934229012069376071>')
    #         return

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


async def command_handler(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du musst mindestens {minRole} sein, um Befehle zu nutzen')
        await m.delete(delay=10)
        return

    cmd = shlex.split(message.content[len(prefix):])

    match cmd:
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
            await aio(message)
        case ['case' | 'gehäuse']:
            await case(message)
        case ['cpukühler' | 'cpu-kühler' | 'cpu-cooler']:
            await cpukuehler(message)
        case ['lüfter' | 'fan' | 'fans']:
            await fans(message)
        case ['netzteil' | 'nt']:
            await netzteil(message)
        case ['ram']:
            await ram(message)
        case ['rgblüfter' | 'rgb-lüfter' | 'rgb-fan' | 'rgb-fans']:
            await rgbluefter(message)
        case ['gpu-ranking' | 'gpu-rank' | 'gpu-benchmark']:
            await message.reply(r'Bitte gib eine Auflösung an: `%gpu-ranking (1080p, 1440p, 2160p)`')
        case ['gpu-ranking' | 'gpu-rank' | 'gpu-benchmark', resolution]:
            await gpu_ranking(message, resolution)


async def metafrage(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du benötigst mindestens die Rolle \'{minRole}\' für diesen Befehl.')
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
    embed = discord.Embed(title='Tier A Netzteile (nach cultists.network rev. 17.0f)', color=discord.Color.brand_red(), url='https://cultists.network/140/psu-tier-list/')
    embed.add_field(name='1000+W', value='https://geizhals.de/?cat=WL-2652571')
    embed.add_field(name='800+W', value='https://geizhals.de/?cat=WL-2652570')
    embed.add_field(name='700+W', value='https://geizhals.de/?cat=WL-2652569')
    embed.add_field(name='600+W', value='https://geizhals.de/?cat=WL-2652568')
    embed.add_field(name='500+W', value='https://geizhals.de/?cat=WL-2652566')
    embed.add_field(name='Disclaimer:', value='Keine Garantie für Vollständigkeit und Aktualität!')
    # embed.add_field(name='Seasonic', value='https://geizhals.de/?cat=WL-2678896')
    await message.reply(embed=embed)


async def ssd_1tb(message):
    await message.reply(f'Hier findet Ihr die aktuell besten 1TB-SSDs: https://gh.de/g/q0\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')


async def ssd_2tb(message):
    await message.reply(f'Hier findet Ihr die aktuell besten 2TB-SSDs: https://gh.de/g/qP\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')


async def ssd_4tb(message):
    # embed = discord.Embed(title='4TB-SSDs', color=0x008380, url='https://gh.de/g/qW')
    # embed.set_thumbnail(url='https://images.samsung.com/is/image/samsung/p6pim/de/mz-v9p1t0bw/gallery/de-990pro-nvme-m2-ssd-mz-v9p1t0bw-533582557?$684_547_PNG$')
    # embed.add_field(name='', value='Für Bens Empfehlungen zu 4TB-SSDs klicke auf den Titel.\nWeitere Kompenten findest du in den <#942543468851499068>')
    # await message.reply(embed=embed)
    await message.reply(f'Hier findet Ihr die aktuell besten 4TB-SSDs: https://gh.de/g/qW\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')


async def aio(message):
    await message.reply(f'Hier findet Ihr die aktuell besten AiO-Wasserkühlungen: https://gh.de/g/Xg\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')


async def case(message):
    await message.reply(f'Hier findet Ihr die aktuell besten Gehäuse für guten Airflow: https://gh.de/g/XY\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')


async def cpukuehler(message):
    await message.reply(f'Hier findet Ihr die aktuell besten CPU-Luftkühler: https://gh.de/g/Xn\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')


async def fans(message):
    await message.reply(f'Hier findet Ihr die aktuell besten Gehäuselüfter ohne RGB: https://gh.de/g/q6\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')


async def netzteil(message):
    await message.reply(f'Hier findet Ihr die aktuell besten Netzteile: https://gh.de/g/1H\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')


async def ram(message):
    await message.reply(f'Hier findet Ihr den aktuell besten RAM: https://gh.de/g/qC\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')


async def rgbluefter(message):
    await message.reply(f'Hier findet Ihr die aktuell besten RGB-Gehäuselüfter: https://gh.de/g/XQ\nWeitere Empfehlungen für Komponenten -> <#942543468851499068>')


# TODO: add rt
def find_image_gpu(resolution: str) -> str:
    # TODO: use non-blocking requests
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


async def gpu_ranking(message, resolution: str):
    match resolution:
        case '1080p' | '1080' | 'fhd' | 'fullhd' | 'FHD' | '2k':
            cdn = find_image_gpu('1080p-ult')
        case '1440p' | '1440' | 'qhd' | 'QHD' | 'wqhd' | 'WQHD' | '2.5k' | '2,5k':
            cdn = find_image_gpu('1440p-ult')
        case '2160p' | '2160' | 'uhd' | 'UHD' | '4k':
            cdn = find_image_gpu('2160p-ult')
        case _:
            m = await message.reply(f'Unbekannte Auflösung: {resolution}')
            await m.delete(delay=10)
            return
    
    # save file if not already cached
    filename = cdn[cdn.rfind('/')+1:]
    filepath = '.cache/' + filename
    if not os.path.exists(filepath):
        with open(filepath, 'wb') as f:
            f.write(requests.get(cdn).content)

    embed = discord.Embed(title=f'GPU-Ranking für {resolution}', url='https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html', color=discord.Color.brand_red())
    file = discord.File(filepath, filename=filename)
    embed.set_image(url=f'attachment://{filename}')
    await message.reply(embed=embed, file=file)

# TODO: cpu ranking links thw

@bot.slash_command(name='ping', description='Überprüft Vitalfunktionen des Bots')
@commands.has_permissions(administrator=True)
async def ping(ctx):
    await ctx.respond(f'Pong! {bot.latency * 1000:.0f}ms')


@bot.slash_command(name='reload', description='Startet den Bot neu')
@commands.has_permissions(administrator=True)
async def reload(ctx):
    embed = discord.Embed(title=f'{bot.user.name} wird neu gestartet...', color=0x00ff00)
    await ctx.respond(embed=embed, ephemeral=True)
    print('Restarting.')
    os.execv(sys.executable, ['python'] + sys.argv)


@bot.slash_command(name='update', description='Aktualisiert und startet den Bot neu')
@commands.has_permissions(administrator=True)
async def update(ctx):
    embed = discord.Embed(title=f'{bot.user.name} wird aktualisiert...', color=0xffff00)
    await ctx.respond(embed=embed, ephemeral=True)
    print('Updating.')
    retval = os.system('git pull')
    if retval != 0:
        await ctx.edit(embed=discord.Embed(title=f'{bot.user.name} konnte nicht aktualisiert werden.', color=0xff0000))
        await send_msg_to_dev(f'{bot.user.name} konnte nicht aktualisiert werden. Returncode: {retval}')
        return
    await ctx.edit(embed=discord.Embed(title=f'{bot.user.name} wurde aktualisiert, starte neu...', color=0x00ff00))
    os.execv(sys.executable, ['python'] + sys.argv)


bot.run(TOKEN)
