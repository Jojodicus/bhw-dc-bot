import os
import random
from asyncio import sleep
from io import BytesIO

import aiohttp
from cogs.utils import has_permissions
from discord import Color, Embed, Message
from discord.ext.commands import Bot, Cog, Context, command
from google import genai
from google.genai import errors, types
from PIL import Image

TITLE = "BHW AI"
SYSTEM_PROMPT = """Du bist BHW-Bot, ein Helfer in einem Discord-Server von Bens-Hardware.
Deine Aufgabe ist es, Leuten zu helfen und für eine positive Stimmung zu sorgen.
Deine Antworten sind auf Deutsch, leicht verständlich formuliert.
Fasse dich kurz in deinen Antworten, niemand möchte eine "Wall of Text" als Antwort!
Du hast keinen Zugriff auf Tools oder MCPs (auch nicht zum Erstellen von Bildern/Videos), antworte nur mit reinem Text!
"""
WORKING = "Generiere Antwort"
TOO_MANY_ATTACHMENTS = "Bitte hänge höchstens ein Bild zu deiner Nachricht an."
RATE_LIMIT = (
    "Meine Kapazität für heute ist leider aufgebraucht, versuch es morgen nochmal."
)
GENERIC_ERROR = "Etwas ist schief gelaufen, probier es eventuell später nochmal."

MAX_TRIES = 3

ALLOWED_ROLE = "Gold"


class AI(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.client = genai.Client()

    @command()
    async def ai(self, ctx: Context) -> None:
        if not await has_permissions(ctx, ALLOWED_ROLE):
            return

        arg = (
            f"Von {ctx.author.display_name} an BHW-Bot: "
            + ctx.message.content.removeprefix(r"%ai").lstrip()
        )
        prompt = []

        # reference other messages
        # TODO: build real chat
        referencedMessage = None
        if reference := ctx.message.reference:
            message = reference.resolved
            if isinstance(message, Message):
                name = message.author.display_name
                content = message.content
                if len(message.embeds) == 1 and message.author == self.bot.user:
                    name = "BHW-Bot"
                    content = message.embeds[0].description

                prompt.append(f"Referenzierte Nachricht von {name}: {content}")
                referencedMessage = message

        # image attachments
        referencedAttachments = []
        if referencedMessage:
            referencedAttachments = referencedMessage.attachments
        if attachments := ctx.message.attachments + referencedAttachments:
            if len(attachments) > 1:
                embed = Embed(
                    title=TITLE, description=TOO_MANY_ATTACHMENTS, color=Color.red()
                )
                await ctx.reply(embed=embed)
                return
            attachment = attachments[0]
            if "image" in (attachment.content_type or ""):
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as response:
                        buffer = BytesIO(await response.read())
                        img = Image.open(buffer)
                        prompt.append(img)

        # user prompt
        prompt.append(arg)

        embed = Embed(title=TITLE, description=WORKING, color=Color.ash_embed())
        reply = await ctx.reply(embed=embed)

        # ask Gemini
        tries = 0
        while tries < MAX_TRIES:
            tries += 1
            try:
                response = self.client.models.generate_content(
                    model="gemini-3-flash-preview",
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    ),
                    contents=prompt,
                )
                break
            except errors.ClientError as e:
                print(f"AI call (try {tries}): {e}")
                if e.code == 429:
                    embed = Embed(
                        title=TITLE, description=RATE_LIMIT, color=Color.red()
                    )
                    await reply.edit(embed=embed)
                    return

            await sleep(random.uniform(5, 10))
            embed = Embed(
                title=TITLE,
                description=WORKING + "." * tries,
                color=Color.ash_embed(),
            )
            await reply.edit(embed=embed)

        if tries >= MAX_TRIES:
            embed = Embed(title=TITLE, description=GENERIC_ERROR, color=Color.red())
            await reply.edit(embed=embed)
            return

        text = response.text  # type: ignore
        # imagefile = None

        # multi-part (with images) - broken for now
        # if response.parts:
        #     for part in response.parts:
        #         if part.text is not None:
        #             text = part.text
        #         elif part.inline_data is not None:
        #             image = part.as_image()
        #             if image:
        #                 imagepath = f"./cache/ai_{ctx.message.id}"
        #                 image.save(imagepath)
        #                 imagefile = File(imagepath)

        # reply
        embed = Embed(title=TITLE, description=text, color=Color.blurple())
        # if imagefile:
        #     embed.set_image(url=imagefile.uri)
        await reply.edit(embed=embed)


async def setup(bot: Bot) -> None:
    token = os.getenv("GEMINI_API_KEY")
    if not token:
        print("You need to set GEMINI_API_KEY to use AI")
    await bot.add_cog(AI(bot))
