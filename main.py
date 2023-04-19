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
import aiohttp
import datetime
import subprocess

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
    global start_time
    start_time = datetime.datetime.utcnow()
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

    preproccessed = message.content.replace('(', ' ').replace(')', ' ')
    cmd = shlex.split(preproccessed[len(prefix):])

    match cmd:
        case ['help' | 'commands' | 'hilfe' | 'befehle' | 'command' | 'befehl' | 'commandlist']:
            await help(message)
        case ['meta' | 'metafrage' | 'meta-frage' | 'Meta' | 'Metafrage' | 'Meta-Frage' | 'META']:
            await metafrage(message)
        case ['psu' | 'PSU']:  # cultists
            await psu(message)
        case ['ssd' | 'ssds' | '1tbssd' | '1tb-ssd' | 'ssd1tb' | 'ssd-1tb' | 'SSD' | 'SSDs' | '1TBSSD' | '1TB-SSD' | 'SSD1TB' | 'SSD-1TB']:
            await ssd_1tb(message)
        case ['2tbssd' | '2tb-ssd' | 'ssd2tb' | 'ssd-2tb' | '2TBSSD' | '2TB-SSD' | 'SSD2TB' | 'SSD-2TB']:
            await ssd_2tb(message)
        case ['4tbssd' | '4tb-ssd' | 'ssd4tb' | 'ssd-4tb' | '4TBSSD' | '4TB-SSD' | 'SSD4TB' | 'SSD-4TB']:
            await ssd_4tb(message)
        case ['aio' | 'wasserkühlung' | 'wasserkühler' | 'AiO' | 'AIO' | 'allinone']:
            await aio(message)
        case ['case' | 'gehäuse' | 'Gehäuse']:
            await case(message)
        case ['cpukühler' | 'cpu-kühler' | 'cpu-cooler' | 'CPU-Kühler']:
            await cpukuehler(message)
        case ['lüfter' | 'fan' | 'fans' | 'Lüfter' | 'Fan' | 'Fans']:
            await fans(message)
        case ['netzteil' | 'nt' | 'Netzteil' | 'NT']:
            await netzteil(message)
        case ['ram' | 'RAM']:
            await ram(message)
        case ['rgblüfter' | 'rgb-lüfter' | 'rgb-fan' | 'rgb-fans' | 'RGB-Lüfter' | 'RGB-Lüfter' | 'RGB-Fan' | 'RGB-Fans']:
            await rgbluefter(message)
        case ['gpu-ranking' | 'gpu-rank' | 'gpu-benchmark', *resolution]:
            if not resolution:
                await message.reply(f'Bitte gib eine Auflösung an. Beispiel: `{prefix}gpu-ranking 1080p`')
            else:
                await gpu_ranking(message, resolution)


async def help(message):
    embed = discord.Embed(title='Hilfe', color=discord.Color.blurple(), url='https://github.com/Jojodicus/bhw-dc-bot')
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name='', value='Eine Übersicht über alle Features und Befehle findest du auf der GitHub-Seite des Bots (Link im Titel).')
    await message.reply(embed=embed)


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
    embed = discord.Embed(title='Tier A Netzteile (nach cultists.network rev. 17.0g)', color=discord.Color.brand_red(), url='https://cultists.network/140/psu-tier-list/')
    embed.add_field(name='1000+W', value='https://geizhals.de/?cat=WL-2652571')
    embed.add_field(name='800+W', value='https://geizhals.de/?cat=WL-2652570')
    embed.add_field(name='700+W', value='https://geizhals.de/?cat=WL-2652569')
    embed.add_field(name='600+W', value='https://geizhals.de/?cat=WL-2652568')
    embed.add_field(name='500+W', value='https://geizhals.de/?cat=WL-2652566')
    embed.add_field(name='Disclaimer:', value='Keine Garantie für Vollständigkeit und Aktualität!')
    # embed.add_field(name='Seasonic', value='https://geizhals.de/?cat=WL-2678896')
    await message.reply(embed=embed)


async def ssd_1tb(message):
    embed = discord.Embed(title='1TB-SSDs', color=0x008380, url='https://gh.de/g/q0')
    embed.set_thumbnail(url='https://images.samsung.com/is/image/samsung/p6pim/de/mz-v9p1t0bw/gallery/de-990pro-nvme-m2-ssd-mz-v9p1t0bw-533582557?$684_547_PNG$')
    embed.add_field(name='', value='Für Bens Empfehlungen zu 1TB-SSDs klicke auf den Titel.')
    await message.reply(embed=embed)


async def ssd_2tb(message):
    embed = discord.Embed(title='2TB-SSDs', color=0x008380, url='https://gh.de/g/qP')
    embed.set_thumbnail(url='https://images.samsung.com/is/image/samsung/p6pim/de/mz-v9p1t0bw/gallery/de-990pro-nvme-m2-ssd-mz-v9p1t0bw-533582557?$684_547_PNG$')
    embed.add_field(name='', value='Für Bens Empfehlungen zu 2TB-SSDs klicke auf den Titel.')
    await message.reply(embed=embed)


async def ssd_4tb(message):
    embed = discord.Embed(title='4TB-SSDs', color=0x008380, url='https://gh.de/g/qW')
    embed.set_thumbnail(url='https://images.samsung.com/is/image/samsung/p6pim/de/mz-v9p1t0bw/gallery/de-990pro-nvme-m2-ssd-mz-v9p1t0bw-533582557?$684_547_PNG$')
    embed.add_field(name='', value='Für Bens Empfehlungen zu 4TB-SSDs klicke auf den Titel.')
    await message.reply(embed=embed)


async def aio(message):
    embed = discord.Embed(title='AiO Wasserkühlungen', color=0x008380, url='https://gh.de/g/Xg')
    embed.set_thumbnail(url='https://www.arctic.de/media/0b/7f/f3/1632824378/liquid-freezer-ii-280-argb-g00.png')
    embed.add_field(name='', value='Für Bens Empfehlungen zu AiO Wasserkühlungen klicke auf den Titel.')
    await message.reply(embed=embed)


async def case(message):
    embed = discord.Embed(title='Gehäuse', color=0x008380, url='https://gh.de/g/XY')
    embed.set_thumbnail(url='https://endorfy.com/wp-content/products/EY2A006_Signum-300-ARGB/Media%20(pictures)/WebP/EY2A006-endorfy-signum-300-argb-01a-webp95.d20221216-u095934.webp')
    embed.add_field(name='', value='Für Bens Empfehlungen zu Gehäusen klicke auf den Titel.')
    await message.reply(embed=embed)


async def cpukuehler(message):
    embed = discord.Embed(title='CPU-Luftkühler', color=0x008380, url='https://gh.de/g/Xn')
    embed.set_thumbnail(url='https://www.arctic.de/media/3c/68/58/1635319800/freezer_i35_argb_g00.png')
    embed.add_field(name='', value='Für Bens Empfehlungen zu CPU-Luftkühlern klicke auf den Titel.')
    await message.reply(embed=embed)


async def fans(message):
    embed = discord.Embed(title='Gehäuselüfter', color=0x008380, url='https://gh.de/g/q6')
    embed.set_thumbnail(url='https://www.arctic.de/media/7b/fd/aa/1670325590/P12_MAX_G00.png')
    embed.add_field(name='', value='Für Bens Empfehlungen zu Gehäuselüftern ohne RGB klicke auf den Titel.')
    await message.reply(embed=embed)


async def netzteil(message):
    embed = discord.Embed(title='Netzteile', color=0x008380, url='https://gh.de/g/1H')
    embed.set_thumbnail(url='https://www.corsair.com/medias/sys_master/images/images/h7b/hbc/9760776028190/base-rmx-2021-config/Gallery/RM850x_01/-base-rmx-2021-config-Gallery-RM850x-01.png_1200Wx1200H')
    embed.add_field(name='', value='Für Bens Empfehlungen zu Netzteilen klicke auf den Titel.')
    await message.reply(embed=embed)


async def ram(message):
    embed = discord.Embed(title='RAM', color=0x008380, url='https://gh.de/g/qC')
    embed.set_thumbnail(url='https://www.gskill.com/_upload/images/156274365910.png')
    embed.add_field(name='', value='Für Bens Empfehlungen zu RAM klicke auf den Titel.')
    await message.reply(embed=embed)


async def rgbluefter(message):
    embed = discord.Embed(title='RGB-Gehäuselüfter', color=0x008380, url='https://gh.de/g/XQ')
    embed.set_thumbnail(url='https://www.silentiumpc.com/wp-content/uploads/2021/03/spc235-spc-stella-hp-argb-120-pwm-rev11-01-png-www.png')
    embed.add_field(name='', value='Für Bens Empfehlungen zu RGB-Gehäuselüftern klicke auf den Titel.')
    await message.reply(embed=embed)


# TODO: add rt
async def find_image_gpu(resolution: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html') as r:
            if r.status != 200:
                await send_msg_to_dev(f'Could not reach toms hardware! Status code: {r.status}')
                raise Exception('Could not reach toms hardware!')
            data = await r.text()

    soup = BeautifulSoup(data, 'html.parser')
    for s in soup.find_all('script', type='text/javascript'):
        if not 'galleryData' in s.text:
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
    
    await send_msg_to_dev(f'Could not find image for resolution {resolution}!')
    raise Exception('Could not find image')


async def gpu_ranking(message, resolution: str):
    for res in resolution:
        # TODO: fuzzy match
        match res:
            case '1080p' | '1080' | 'fhd' | 'fullhd' | 'FHD' | '2k' | 'full-hd' | 'full-HD' | 'Full-HD' | 'FullHD' | 'Full-HD' | '1920x1080' | '1920x1080p':
                cdn = await find_image_gpu('1080p-ult')
            case '1440p' | '1440' | 'qhd' | 'QHD' | 'wqhd' | 'WQHD' | '2.5k' | '2,5k' | 'quad-hd' | 'quad-HD' | 'Quad-HD' | 'QuadHD' | '2560x1440' | '2560x1440p':
                cdn = await find_image_gpu('1440p-ult')
            case '2160p' | '2160' | 'uhd' | 'UHD' | '4k' | 'ultra-hd' | 'ultra-HD' | 'Ultra-HD' | 'UltraHD' | '3840x2160' | '3840x2160p':
                cdn = await find_image_gpu('2160p-ult')
            case _:
                m = await message.reply(f'Unbekannte Auflösung: {res}')
                await m.delete(delay=10)
                return
        
        # save file if not already cached
        filename = cdn[cdn.rfind('/')+1:]
        filepath = '.cache/' + filename
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                f.write(requests.get(cdn).content)

        embed = discord.Embed(title=f'GPU-Ranking für {res}', url='https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html', color=discord.Color.brand_red())
        file = discord.File(filepath, filename=filename)
        embed.set_image(url=f'attachment://{filename}')
        await message.reply(embed=embed, file=file)

# TODO: cpu ranking links thw

@bot.slash_command(name='ping', description='Überprüft Vitalfunktionen des Bots')
@commands.has_permissions(administrator=True)
async def ping(ctx):
    embed = discord.Embed(title=f'{bot.user.name} ist online', color=discord.Color.fuchsia())
    embed.add_field(name='Latenz', value=f'{bot.latency * 1000:.0f} ms')
    timedelta = datetime.datetime.utcnow() - start_time
    embed.add_field(name='Server', value=f'{len(bot.guilds)}')
    embed.add_field(name='Benutzer', value=f'{ctx.guild.member_count}/{sum([g.member_count for g in bot.guilds])}')
    embed.add_field(name='Uptime', value=f'{timedelta.days} Tage, {timedelta.seconds // 3600} Stunden, {(timedelta.seconds // 60) % 60} Minuten')
    embed.set_footer(text=f'{bot.user.name} {bot.user.id}', icon_url=bot.user.display_avatar.url)
    await ctx.respond(embed=embed, delete_after=30)


@bot.slash_command(name='reload', description='Startet den Bot neu')
@commands.has_permissions(administrator=True)
async def reload(ctx):
    embed = discord.Embed(title=f'{bot.user.name} wird neu gestartet...', color=0x00ff00)
    await ctx.respond(embed=embed, ephemeral=True)
    print('Restarting.')
    os.execv(sys.executable, ['python3'] + sys.argv)


@bot.slash_command(name='update', description='Aktualisiert und startet den Bot neu')
@commands.has_permissions(administrator=True)
async def update(ctx):
    embed = discord.Embed(title=f'{bot.user.name} wird aktualisiert...', color=0xffff00)
    await ctx.respond(embed=embed, ephemeral=True)
    print('Updating.')

    try:
        out = subprocess.check_output(['git', 'pull'])
        if out == b'Already up to date.\n':
            await ctx.edit(embed=discord.Embed(title=f'{bot.user.name} ist bereits auf dem neuesten Stand.', color=0x00ff00))
            return
    except subprocess.CalledProcessError as e:
        await ctx.edit(embed=discord.Embed(title=f'{bot.user.name} konnte nicht aktualisiert werden.', color=0xff0000))
        await send_msg_to_dev(f'{bot.user.name} konnte nicht aktualisiert werden. Returncode: {e.returncode} - {e.output}')
        return

    await ctx.edit(embed=discord.Embed(title=f'{bot.user.name} wurde aktualisiert, starte neu...', color=0x00ff00))
    os.execv(sys.executable, ['python3'] + sys.argv)


bot.run(TOKEN)
