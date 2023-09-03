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
import random

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
    jojo = await bot.fetch_user(226054688368361474) # @jojodicus, bot dev
    await jojo.send(msg)

function_name_map = {}
function_alias_map = {}
def register_command(name, aliases, function):
    function_name_map[name] = function
    function_alias_map[name] = aliases

def is_recommendation_command(name):
    return name in cfg_commands["recommendations"].keys()

# TODO: switch to fuzzywuzzy, move to module
def closest_match_key(phrase, options_dict):
    # returns key of closest match
    mindist = float('inf')
    minkey = None

    for key, values_list in options_dict.items():
        if phrase in values_list:
            return key

        for value in values_list:
            dist = distance(phrase, value, score_cutoff=2)
            if dist < mindist and dist <= 2:
                mindist = dist
                minkey = key

    return minkey


async def error_reply(message, reply_text):
    m = await message.reply(reply_text)
    if config["ephemeral_errors"]:
        await m.delete(delay=10)


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

    if bot.user in message.mentions:
        await mention_handler(message)

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
        # page = requests.get(page, headers={'cookie': API_COOKIE}) # TODO: aiohttp
        async with aiohttp.ClientSession(headers={"cookie": API_COOKIE}) as session:
            async with session.get(page) as r:
                status = r.status
                data = await r.text()
        if status == 400 or 'private wishlist' in data:
            cfg_gh_private = cfg_geizhals["private"]
            embed = discord.Embed(title=cfg_gh_private["title"], color=discord.Color.blurple())
            embed.add_field(name='', value=cfg_gh_private["message"])
            await message.reply(embed=embed)
            return
        if r'{"code":403,"error":"Authentication failed"}' in data:
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

async def mention_handler(message):
    if not message.guild.emojis:
        return

    # react with random emote
    emoji = random.choice(message.guild.emojis)
    await message.add_reaction(emoji)

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
        await error_reply(message, f'Du musst mindestens {minRole} sein, um Befehle zu nutzen')
        return

    preproccessed = message.content.replace('(', ' ').replace(')', ' ')
    cmd = shlex.split(preproccessed[len(prefix):])

    identifier = cmd[0].lower()

    best_match = closest_match_key(identifier, function_alias_map)

    if not best_match:
        return

    if is_recommendation_command(best_match):
        callback = recommendations_factory(best_match)
    else:
        callback = function_name_map[best_match]

    await callback(message, cmd)


# TODO: switch to returning embeds instead of reply-functions?
def recommendations_factory(key):
    cfg_cmd_reco = cfg_commands["recommendations"][key]
    async def reply(message, cmd=None):
        embed = discord.Embed(title=cfg_cmd_reco["title"], color=0x008380, url=cfg_cmd_reco["title_url"])
        embed.set_thumbnail(url=cfg_cmd_reco["thumbnail_url"])
        embed.add_field(name='', value=cfg_cmd_reco["message"])
        await message.reply(embed=embed)
    return reply

# register recommendation commands
# TODO: clean this up a little
recommendation_commands = ["1tb_ssd", "2tb_ssd", "4tb_ssd", "aio", "case", "cpukühler", "lüfter", "netzteil", "ram", "rgblüfter"]
for command in recommendation_commands:
    register_command(command, cfg_commands["recommendations"][command]["aliases"], None)


cfg_cmd_help = cfg_commands["help"]
async def help(message, cmd=None):
    embed = discord.Embed(title=cfg_cmd_help["title"], color=discord.Color.blurple(), url=cfg_cmd_help["title_url"])
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name='', value=cfg_cmd_help["message"])
    await message.reply(embed=embed)
register_command("help", cfg_cmd_help["aliases"], help)


cfg_cmd_meta = cfg_commands["meta"]
async def metafrage(message, cmd=None):
    embed = discord.Embed(title=cfg_cmd_meta["title"], color=discord.Color.blurple(), url=cfg_cmd_meta["title_url"])
    embed.add_field(name='', value=cfg_cmd_meta["message"])

    if message.reference:
        await message.channel.send(embed=embed, reference=message.reference)
    else:
        await message.reply(embed=embed)
register_command("meta", cfg_cmd_meta["aliases"], metafrage)


cfg_cmd_psu = cfg_commands["psu"]
async def psu(message, cmd=None):
    if len(cmd) < 2:
        embed = discord.Embed(title=cfg_cmd_psu["title"], color=discord.Color.brand_red(), url=cfg_cmd_psu["title_url"])
        embed.set_thumbnail(url=cfg_cmd_psu["thumbnail_url"])
        for field in cfg_cmd_psu["fields"]:
            embed.add_field(name=field["title"], value=field["message"], inline=True)

        await message.reply(embed=embed)
        return

    # get cheapest
    fetch_count = cfg_cmd_psu["fetch_count"]

    try:
        selection = int(cmd[1])
    except ValueError:
        await error_reply(message, f'Unbekannte Zahl: {cmd[1]}')
        return

    wishlist_url = ''
    wishlist_title = ''
    for field in cfg_cmd_psu["fields"][:5]:
        if selection >= field["wattage"]:
            wishlist_url = field["message"]
            wishlist_title = field["title"]
            break
    else:
        await error_reply(message, f'Nicht unterstützte Wattanzahl: {selection}')
        return

    # make api call
    api_url = re.sub(r'https?://geizhals..?.?/wishlists/', 'https://geizhals.de/api/usercontent/v0/wishlist/', wishlist_url)
    api_url += "&limit=9999"
    # note: in config.json, the ?sort=p at the end of the url is important, i think? i mean we will sort manually as well
    async with aiohttp.ClientSession(headers={"cookie": API_COOKIE}) as session:
            async with session.get(api_url) as r:
                data = await r.text()
    if r'{"code":403,"error":"Authentication failed"}' in data:
            await send_msg_to_dev(f'API Cookie für Geizhals ist abgelaufen, bitte erneuern: {API_COOKIE}')

    data_j = json.loads(data)

    found_units = [] # (price, name, link, image)
    for product in data_j["response"]["products"]:
        if "best_price" not in product:
            continue

        product_price = product["best_price"]
        product_name = product["product"]
        product_link = f'https://geizhals.de{product["urls"]["overview"]}'
        if "images" in product and len(product["images"]) > 0:
            product_image = product["images"][0]
        else:
            product_image = cfg_cmd_psu["thumbnail_url"]
        found_units.append((product_price, product_name, product_link, product_image))

    # sort by price
    found_units.sort(key=lambda x: x[0])

    # respond to message
    embed = discord.Embed(title=f'Die {min(len(found_units), fetch_count)} günstigsten Tier A Netzteile mit {wishlist_title}', url=wishlist_url, color=discord.Color.brand_red())
    embed.set_thumbnail(url=found_units[0][3])
    for unit in found_units[:fetch_count]:
        embed.add_field(name=f'{unit[0]}€', value=f'[{unit[1]}]({unit[2]})', inline=False)
    await message.reply(embed=embed)
register_command("psu", cfg_cmd_psu["aliases"], psu)


# TODO: add rt, move to module
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


cfg_cmd_gpu = cfg_commands["gpu-ranking"]
async def gpu_ranking(message, cmd):
    if len(cmd) < 2:
        await error_reply(message, f'Bitte gib eine Auflösung an. Beispiel: `{prefix}gpu-ranking 1080p`')
        return

    resolution = cmd[1:]

    for res in resolution:
        res = res.lower()

        key = closest_match_key(res, cfg_cmd_gpu["resolutions"])

        if not key:
            await error_reply(message, f'Unbekannte Auflösung: {res}')
            return

        cdn = await find_image_gpu(f'{key}-ult')

        # save file if not already cached
        filename = cdn[cdn.rfind('/')+1:]
        filepath = '.cache/' + filename
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                f.write(requests.get(cdn).content) # TODO: aiohttp

        embed = discord.Embed(title=f'GPU-Ranking für {res}', url=cfg_cmd_gpu["title_url"], color=discord.Color.brand_red())
        file = discord.File(filepath, filename=filename)
        embed.set_image(url=f'attachment://{filename}')
        await message.reply(embed=embed, file=file)
register_command("gpu-ranking", cfg_cmd_gpu["aliases"], gpu_ranking)


# TODO: cpu ranking links thw


cfg_cmd_gidf = cfg_commands["gidf"]
async def gidf(message, cmd):
    if len(cmd) < 2:
        # TODO: extract function
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://serpapi.com/account?api_key={SERPAPI}') as r:
                if r.status != 200:
                    send_msg_to_dev('Could not reach serpapi.com')
                    raise Exception('Could not reach serpapi.com')
                data = await r.text()
        data = json.loads(data)

        embed = discord.Embed(title='GIDF', color=discord.Color.dark_gold())
        embed.add_field(name='', value=f'Der Bot hat diesen Monat noch **{data["total_searches_left"]}** von {data["searches_per_month"]} Anfragen frei.')
        await message.reply(embed=embed)
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
    embed.set_thumbnail(url=cfg_cmd_gidf["thumbnail_url"])
    embed.add_field(name='', value=cfg_cmd_gidf["message"])

    txt = ''
    for i, e in enumerate(results):
        txt += f'**{i+1}**. {e}\n'

    embed.add_field(name='Suchergebnisse', value=txt)
    await message.reply(embed=embed)
register_command("gidf", cfg_cmd_gidf["aliases"], gidf)


cfg_slashcommands = config["slash_commands"]

@bot.slash_command(name='ping', description=cfg_slashcommands["ping"]["description"])
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


@bot.slash_command(name='reload', description=cfg_slashcommands["reload"]["description"])
@commands.has_permissions(administrator=True)
async def reload(ctx):
    embed = discord.Embed(title=f'{bot.user.name} wird neu gestartet...', color=0x00ff00)
    await ctx.respond(embed=embed, ephemeral=True)
    print('Restarting.')
    os.execv(sys.executable, ['python3'] + sys.argv)


@bot.slash_command(name='update', description=cfg_slashcommands["update"]["description"])
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
