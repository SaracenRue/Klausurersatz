from random import choice, randint
from typing import Optional
from datetime import datetime

from aiohttp import request
from discord import Member, Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='hello', aliases=['hi'], brief="Begrüßung")
    async def say_hello(self, ctx):
        """Mit diesem Command begrüßt dich der Bot."""
        await ctx.send(f'{choice(("Hallo", "Hi", "Hey", "Servus"))} {ctx.author.mention}!')

    @command(name='dice', aliases=['roll'], brief="Würfeln")
    async def roll_dice(self, ctx, dice_string: str):
        """Dieser Command summiert die Summe von Würfeln, die in den Parametern spezifiziert werden, das Format sieht
        dabei folgendermaßen aus: ANZAHLdMAXIMALWERT Die erste Zahl gibt die Anzahl der Würfel an (max. 25) und die
        zweite Zahl gibt den Maximalwert an, der gewürfelt werden kann. Beide Zahlen werden mit einem 'd' getrennt.
        Beispiel: 8d6 Acht Würfel mit dem Maximalwert 6 werden geworfen."""
        dice, value = (int(term) for term in dice_string.split('d'))

        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]

            await ctx.send(' + '.join([str(r) for r in rolls]) + f' = {sum(rolls)}')

        else:
            await ctx.send("Ich kann nicht so viele Würfel werfen. Bitte wähle eine geringere Anzahl.")

    @command(name='echo', aliases=['say'], brief="Echo")
    async def echo_message(self, ctx, *, message):
        """Gibt die Nachricht, die du als Parameter angegeben hast, erneut aus und löscht deine Nachricht."""
        await ctx.message.delete()
        await ctx.send(message)

    @command(name='fact', brief="Tierfakt")
    async def animal_fact(self, ctx, animal: str):
        """Dieser Command gibt dir zufällige Fakten zu bestimmten Tierarten aus. Mögliche Tierarten sind: dog, cat,
        panda, fox, bird, koala Gib eine dieser Tierarten als Parameter an, um zu ihr Fakten zu erhalten. Beachte:
        Die Fakten sind auf Englisch."""
        if (animal := animal.lower()) in ('dog',  'cat', 'panda', 'fox', 'bird', 'koala'):
            fact_url = f'https://some-random-api.ml/facts/{animal}'
            image_url = f'https://some-random-api.ml/img/{"birb" if animal == "bird" else animal}'

            async with request('GET', image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data['link']

                else:
                    image_link = None

            async with request('GET', fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(title=f'{animal.title()} Fact',
                                  description=data['fact'],
                                  colour=ctx.author.colour)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)

                else:
                    await ctx.send(f'Die API gab einen {response.status} Status zurück.')

        else:
            await ctx.send('Zu diesem Tier sind keine Fakten verfügbar.')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('fun')

def setup(bot):
    bot.add_cog((Fun(bot)))
