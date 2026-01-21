from discord.ext.commands import Bot, Cog, command, Context
from discord import Embed, Color, File
from cogs.utils import has_permissions, message_dev
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import json
import os
from Levenshtein import distance

RESOLUTIONS = {
    "1080p": ["1080", "1080p", "fhd", "fullhd", "2k", "1920x1080"],
    "1440p": ["1440", "1440p", "qhd", "wqhd", "2.5k", "quadhd", "2560x1440"],
    "2160p": ["2160", "2160p", "uhd", "4k", "ultrahd", "3840x2160"],
}

FUZZY_DIST = 1


def closest_resolution_key(arg: str):
    mindist = float("inf")
    minkey = None

    for key, values_list in RESOLUTIONS.items():
        if arg in values_list:
            return key

        for value in values_list:
            dist = distance(arg, value, score_cutoff=FUZZY_DIST)
            if dist < mindist and dist <= FUZZY_DIST:
                mindist = dist
                minkey = key

    return minkey


class Benchmark(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.session = ClientSession()

    async def download_and_file(self, src: str) -> File:
        filepath = ".cache/" + src[src.rfind("/") + 1 :]
        if not os.path.exists(filepath):
            async with self.session.get(src) as resp:
                with open(filepath, "wb") as fd:
                    async for chunk in resp.content.iter_chunked(512):
                        fd.write(chunk)
        return File(filepath)

    async def find_gpu_image(self, specifier: str) -> File:
        async with self.session.get(
            "https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html"
        ) as r:
            if r.status != 200:
                raise Exception(
                    f"Could not reach toms hardware! Status code: {r.status}"
                )
            data = await r.text()

        soup = BeautifulSoup(data, "html.parser")
        for s in soup.find_all("script", type="text/javascript"):
            if "galleryData" not in s.text:
                continue
            for line in s.text.split("\n"):
                if "JSON.stringify(" not in line:
                    continue
                line = line.split("JSON.stringify(")[1]
                last_comma = line.rfind(",")
                line = line[: last_comma - 1]

                data = json.loads(line)
                for row in data["galleryData"]:
                    img = row["image"]
                    resolution = f"{specifier}-ult"
                    if (
                        img["name"]
                        == f"gpu-benchmarks-rasterization-performance-chart-{resolution}"
                    ):
                        return await self.download_and_file(img["src"])

        raise Exception(f"Could not find image for resolution {specifier}!")

    @command()
    async def gpu(self, ctx: Context, *resolutions: str) -> None:
        if not await has_permissions(ctx):
            return

        if len(resolutions) < 1:
            embed = Embed(
                title=f"Bitte gib eine Auflösung an. Beispiel: `{self.bot.command_prefix}gpu 1080p`",
                color=Color.red(),
            )
            await ctx.reply(embed=embed)
            return

        parsed_resolutions = list(map(closest_resolution_key, resolutions))

        unknown = list(
            map(
                lambda x: x[0],
                filter(lambda x: x[1] is None, zip(resolutions, parsed_resolutions)),
            )
        )
        if len(unknown) > 0:
            embed = Embed(
                title=f"Unbekannte Auflösung{'en' if len(unknown) > 1 else ''}: {', '.join(unknown)}",
                color=Color.red(),
            )
            await ctx.reply(embed=embed)
            return

        for resolution in parsed_resolutions:
            assert resolution is not None

            try:
                file = await self.find_gpu_image(resolution)
                embed = Embed(
                    title=f"GPU-Ranking {resolution}",
                    url="https://www.tomshardware.com/reviews/cpu-hierarchy,4312.html",
                    color=Color.blurple(),
                )
                embed.set_image(url=file.uri)
                await ctx.reply(embed=embed, file=file)
            except Exception as e:
                embed = Embed(
                    title="Etwas ist schiefgelaufen, der Botentwickler ist informiert",
                    color=Color.red(),
                )
                await message_dev(self.bot, str(e))
                await ctx.reply(embed=embed)
                return


async def setup(bot: Bot) -> None:
    await bot.add_cog(Benchmark(bot))
