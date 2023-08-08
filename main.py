#! /usr/bin/env python3

# TODO: sort imports
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
from Levenshtein import distance
import json
from serpapi import GoogleSearch

load_dotenv()
TOKEN = os.getenv('BHW_TOKEN')
API_COOKIE = os.getenv('GH_API_COOKIE')
SERPAPI = os.getenv('SERPAPI_KEY')

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
cfg_commands = config["commands"]

intents = discord.Intents.default()
intents.message_content = True

prefix = '%'
bot = discord.Bot(intents=intents)

# minimum role to use commands
minRole = cfg_commands["min_role"]

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
    if message.author.bot:
        return

    # makeshift prefix commands
    if message.content.startswith(prefix):
        await command_handler(message)
        return

    # Ben pings
    cfg_ben_pings = config["ben_pings"]
    if f'<@{cfg_ben_pings["ben_id"]}>' in message.content:
        embed = discord.Embed(title=cfg_ben_pings["title"], color=discord.Color.blurple())
        embed.add_field(name='', value=cfg_ben_pings["message"])
        await message.reply(embed=embed)

    # TODO: more efficient link searching

    cfg_geizhals = config["geizhals_links"]

    # local lists
    locals = re.findall(r'https?://geizhals..?.?/wishlists/local-[0-9]+', message.content)
    if locals:
        cfg_gh_local = cfg_geizhals["local"]
        embed = discord.Embed(title=cfg_gh_local["title"], color=discord.Color.blurple())
        embed.add_field(name='', value=cfg_gh_local["message"])
        await message.reply(embed=embed)
        return

    # private lists
    private = re.findall(r'https?://geizhals..?.?/wishlists/[0-9]+', message.content)
    for link in private:
        page = re.sub(r'https?://geizhals..?.?/wishlists/', 'https://geizhals.de/api/usercontent/v0/wishlist/', link)
        page = requests.get(page, headers={'cookie': API_COOKIE}) # TODO: aiohttp
        if r'{"response":null}' in page.text:
            cfg_gh_private = cfg_geizhals["private"]
            embed = discord.Embed(title=cfg_gh_private["title"], color=discord.Color.blurple())
            embed.add_field(name='', value=cfg_gh_private["message"])
            await message.reply(embed=embed)
            return
        if r'{"code":403,"error":"Authentication failed"}' in page.text:
            await send_msg_to_dev(f'API Cookie für Geizhals ist abgelaufen, bitte erneuern: {API_COOKIE}')
            # TODO: DM to bot sets new api cookie

    # only overview to lists
    overview = re.findall(r'https?://geizhals..?.?/wishlists(?!/[0-9]+)', message.content)
    if overview:
        cfg_gh_overview = cfg_geizhals["overview"]
        embed = discord.Embed(title=cfg_gh_overview["title"], color=discord.Color.blurple())
        embed.add_field(name='', value=cfg_gh_overview["message"])
        await message.reply(embed=embed)
        return


def has_role_or_higher(user, rolename, guild):
    rns = list(map(lambda x: x.name, guild.roles))

    if rolename not in rns:
            return True

    highest = user.roles[-1].name
    return rns.index(highest) >= rns.index(rolename)


def is_atleast(rolename):
    async def predicate(ctx):
        return has_role_or_higher(ctx.author, rolename, ctx.guild)
    return commands.check(predicate)

def matches_roughly(command, options):
    for option in options:
        if distance(command, option, score_cutoff=2) <= 2:
            return True
    return False

async def command_handler(message):
    if not has_role_or_higher(message.author, minRole, message.guild):
        m = await message.reply(f'Du musst mindestens {minRole} sein, um Befehle zu nutzen')
        await m.delete(delay=10)
        return

    preproccessed = message.content.replace('(', ' ').replace(')', ' ')
    cmd = shlex.split(preproccessed[len(prefix):])

    identifier = cmd[0].lower()

    options = [
        ['help', 'hilfe', 'command', 'befehl', 'commandlist'],
        ['meta', 'metafrage'],
        ['psu'],
        ['ssd', '1tbssd', 'ssd1tb'],
        ['2tbssd', 'ssd2tb'],
        ['4tbssd', 'ssd4tb'],
        ['aio', 'wasserkühlung', 'wasserkühler', 'allinone'],
        ['case', 'gehäuse'],
        ['cpukühler', 'cpu-kühler', 'cpu-cooler'],
        ['lüfter', 'fan'],
        ['netzteil', 'nt'],
        ['ram'],
        ['rgblüfter', 'rgb-fan'],
        ['gpu-ranking', 'gpu-rank', 'gpu-benchmark', 'gpu'],
        ['gidf', 'lmgtfy']
    ]
    options_func = [help, metafrage, psu, ssd_1tb, ssd_2tb, ssd_4tb, aio, case, cpukuehler, fans, netzteil, ram, rgbluefter, gpu_ranking, gidf]

    best_match = closest_match_index(identifier, options)

    if best_match == -1:
        return

    await options_func[best_match](message, cmd)


async def help(message, cmd=None):
    embed = discord.Embed(title='Hilfe', color=discord.Color.blurple(), url='https://github.com/Jojodicus/bhw-dc-bot')
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name='', value='Eine Übersicht über alle Features und Befehle findest du auf der GitHub-Seite des Bots (Link im Titel).')
    await message.reply(embed=embed)


async def metafrage(message, cmd=None):
    cfg_cmd_meta = cfg_commands["meta"]

    embed = discord.Embed(title=cfg_cmd_meta["title"], color=discord.Color.blurple(), url=cfg_cmd_meta["title_url"])
    embed.add_field(name='', value=cfg_cmd_meta["message"])

    if message.reference:
        await message.channel.send(embed=embed, reference=message.reference)
    else:
        await message.reply(embed=embed)


async def psu(message, cmd=None):
    cfg_cmd_psu = cfg_commands["psu"]

    embed = discord.Embed(title=cfg_cmd_psu["title"], color=discord.Color.brand_red(), url=cfg_cmd_psu["title_url"])
    for field in cfg_cmd_psu["fields"]:
        embed.add_field(name=field["title"], value=field["message"])

    await message.reply(embed=embed)

# TODO: switch to returning embeds instead of reply-functions?
def recommendations_factory(title, title_url, thumbnail_url, content):
    async def reply(message, cmd=None):
        embed = discord.Embed(title=title, color=0x008380, url=title_url)
        embed.set_thumbnail(url=thumbnail_url)
        embed.add_field(name='', value=content)
        await message.reply(embed=embed)
    return reply

async def ssd_1tb(message, cmd=None):
    embed = discord.Embed(title='1TB-SSDs', color=0x008380, url='https://gh.de/g/q0')
    embed.set_thumbnail(url='https://images.samsung.com/is/image/samsung/p6pim/de/mz-v9p1t0bw/gallery/de-990pro-nvme-m2-ssd-mz-v9p1t0bw-533582557?$684_547_PNG$')
    embed.add_field(name='', value='Für Bens Empfehlungen zu 1TB-SSDs klicke auf den Titel.')
    await message.reply(embed=embed)


async def ssd_2tb(message, cmd=None):
    embed = discord.Embed(title='2TB-SSDs', color=0x008380, url='https://gh.de/g/qP')
    embed.set_thumbnail(url='https://images.samsung.com/is/image/samsung/p6pim/de/mz-v9p1t0bw/gallery/de-990pro-nvme-m2-ssd-mz-v9p1t0bw-533582557?$684_547_PNG$')
    embed.add_field(name='', value='Für Bens Empfehlungen zu 2TB-SSDs klicke auf den Titel.')
    await message.reply(embed=embed)


async def ssd_4tb(message, cmd=None):
    embed = discord.Embed(title='4TB-SSDs', color=0x008380, url='https://gh.de/g/qW')
    embed.set_thumbnail(url='https://images.samsung.com/is/image/samsung/p6pim/de/mz-v9p1t0bw/gallery/de-990pro-nvme-m2-ssd-mz-v9p1t0bw-533582557?$684_547_PNG$')
    embed.add_field(name='', value='Für Bens Empfehlungen zu 4TB-SSDs klicke auf den Titel.')
    await message.reply(embed=embed)


async def aio(message, cmd=None):
    embed = discord.Embed(title='AiO Wasserkühlungen', color=0x008380, url='https://gh.de/g/Xg')
    embed.set_thumbnail(url='https://www.arctic.de/media/0b/7f/f3/1632824378/liquid-freezer-ii-280-argb-g00.png')
    embed.add_field(name='', value='Für Bens Empfehlungen zu AiO Wasserkühlungen klicke auf den Titel.')
    await message.reply(embed=embed)


async def case(message, cmd=None):
    embed = discord.Embed(title='Gehäuse', color=0x008380, url='https://gh.de/g/XY')
    embed.set_thumbnail(url='https://endorfy.com/wp-content/products/EY2A006_Signum-300-ARGB/Media%20(pictures)/WebP/EY2A006-endorfy-signum-300-argb-01a-webp95.d20221216-u095934.webp')
    embed.add_field(name='', value='Für Bens Empfehlungen zu Gehäusen klicke auf den Titel.')
    await message.reply(embed=embed)


async def cpukuehler(message, cmd=None):
    embed = discord.Embed(title='CPU-Luftkühler', color=0x008380, url='https://gh.de/g/Xn')
    embed.set_thumbnail(url='https://www.arctic.de/media/3c/68/58/1635319800/freezer_i35_argb_g00.png')
    embed.add_field(name='', value='Für Bens Empfehlungen zu CPU-Luftkühlern klicke auf den Titel.')
    await message.reply(embed=embed)


async def fans(message, cmd=None):
    embed = discord.Embed(title='Gehäuselüfter', color=0x008380, url='https://gh.de/g/q6')
    embed.set_thumbnail(url='https://www.arctic.de/media/7b/fd/aa/1670325590/P12_MAX_G00.png')
    embed.add_field(name='', value='Für Bens Empfehlungen zu Gehäuselüftern ohne RGB klicke auf den Titel.')
    await message.reply(embed=embed)


async def netzteil(message, cmd=None):
    embed = discord.Embed(title='Netzteile', color=0x008380, url='https://gh.de/g/1H')
    embed.set_thumbnail(url='https://www.corsair.com/medias/sys_master/images/images/h7b/hbc/9760776028190/base-rmx-2021-config/Gallery/RM850x_01/-base-rmx-2021-config-Gallery-RM850x-01.png_1200Wx1200H')
    embed.add_field(name='', value='Für Bens Empfehlungen zu Netzteilen klicke auf den Titel.')
    await message.reply(embed=embed)


async def ram(message, cmd=None):
    embed = discord.Embed(title='RAM', color=0x008380, url='https://gh.de/g/qC')
    embed.set_thumbnail(url='https://www.gskill.com/_upload/images/156274365910.png')
    embed.add_field(name='', value='Für Bens Empfehlungen zu RAM klicke auf den Titel.')
    await message.reply(embed=embed)


async def rgbluefter(message, cmd=None):
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

# TODO: switch to fuzzywuzzy
# TODO: maybe use a dict
def closest_match_index(phrase, options):
    mindist = float('inf')
    minindex = -1

    for i, option in enumerate(options):
        if phrase in option:
            return i

        for part in option:
            dist = distance(phrase, part, score_cutoff=2)
            if dist < mindist and dist <= 2:
                mindist = dist
                minindex = i

    return minindex


async def gpu_ranking(message, cmd):
    if len(cmd) < 2:
        m = await message.reply(f'Bitte gib eine Auflösung an. Beispiel: `{prefix}gpu-ranking 1080p`')
        await m.delete(delay=10)
        return

    resolution = cmd[1:]

    for res in resolution:
        res = res.lower()

        fhd = ['1080', 'fhd', 'fullhd', '2k', '1920x1080']
        wqhd = ['1440', 'qhd', 'wqhd', '2.5k', 'quadhd', '2560x1440']
        uhd = ['2160', 'uhd', '4k', 'ultrahd', '3840x2160']
        options = [fhd, wqhd, uhd]
        idx = closest_match_index(res, options)

        match idx:
            case 0:
                res = '1080p'
            case 1:
                res = '1440p'
            case 2:
                res = '2160p'
            case _:
                m = await message.reply(f'Unbekannte Auflösung: {res}')
                await m.delete(delay=10)
                return
        cdn = await find_image_gpu(f'{res}-ult')

        # save file if not already cached
        filename = cdn[cdn.rfind('/')+1:]
        filepath = '.cache/' + filename
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                f.write(requests.get(cdn).content) # TODO: aiohttp

        embed = discord.Embed(title=f'GPU-Ranking für {res}', url='https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html', color=discord.Color.brand_red())
        file = discord.File(filepath, filename=filename)
        embed.set_image(url=f'attachment://{filename}')
        await message.reply(embed=embed, file=file)

# TODO: cpu ranking links thw

async def gidf(message, cmd):
    if len(cmd) < 2:
        m = await message.reply(f'Bitte gib einen Suchbegriff an. Beispiel: `{prefix}gidf wie funktioniert google`')
        await m.delete(delay=10)
        return

    searchterm = ' '.join(cmd[1:])

    params = {
        'engine': 'google',
        'q': f'"{searchterm}"',
        'google_domain': 'google.de',
        'hl': 'de',
        'gl': 'de',
        'safe': 'active',
        'num': 6, # request more than 3 results cuz google is weird (or ads get counted, idk)
        'api_key': SERPAPI
    }

    # TODO: async
    search = GoogleSearch(params)
    results = search.get_dict()['organic_results'][:3] # reduce to 3 results here

    results = [f'[{r["title"]}]({r["link"]}) ({r["source"]})' for r in results]

    searchurl = f'https://www.google.com/search?q={searchterm}'.replace(' ', '+')
    embed = discord.Embed(title=f'GIDF: "{searchterm}"', url=searchurl, color=discord.Color.blurple())
    embed.set_thumbnail(url='https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png')
    embed.add_field(name='', value=f'Google ist dein Freund. Eine Suchmaschine zu benutzen ist kein Verbrechen. Hier eine Schnellübersicht der ersten paar Ergebnisse, die ganze Suche findest du im Link im Titel.')

    txt = ''
    for i, e in enumerate(results):
        txt += f'**{i+1}**. {e}\n'

    embed.add_field(name='Suchergebnisse', value=txt)
    await message.reply(embed=embed)


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
