from asyncio import sleep
from datetime import datetime
from glob import glob

from discord import Embed, File, Intents, DMChannel
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
                                  CommandOnCooldown)
from discord.ext.commands import when_mentioned_or, command, has_permissions

from ..data import db

###LOG###
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
###LOG-ENDE###

OWNER_IDS = [385078547774963713]
COGS = [path.split('\\')[-1][:-3] for path in glob('./lib/cogs/*.py')]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

def get_prefix(bot, message):
    prefix = db.myroot[0].text
    return when_mentioned_or(prefix)(bot, message)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f' {cog} cog bereit')

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None

        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS, intents=Intents.all())

    def setup(self):
        for cog in COGS:
            self.load_extension(f'lib.cogs.{cog}')
            print(f' {cog} cog wird geladen')

        print('setup fertig')

    def run(self, version):
        self.VERSION = version

        print('setup wird gestartet...')
        self.setup()

        with open('./lib/bot/token.txt', 'r', encoding='utf-8') as tf:
            self.TOKEN = tf.read()

        print('bot wird gestartet...')
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("Ich kann noch keine Commands entgegennehmen. Warte bitte ein paar Sekunden.")

    async def on_connect(self):
        print('bot verbunden')

    async def on_disconnect(self):
        print('bot getrennt')

    async def on_error(self, err, *args, **kwargs):
        if err == 'on_command_error':
            await args[0].send('Ein Command-Fehler ist aufgetreten.')

        await self.stdout.send('Ein ERROR ist aufgetreten.')
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("Ein oder mehr benötigte Angaben fehlen.")

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f'Dieser Command ist auf {str(exc.cooldown.type).split(".")[-1]} Cooldown. Versuch es nochmal in {exc.retry_after:,.2f} Sekunden.')

        elif hasattr(exc, 'original'):
            if isinstance(exc.original, HTTPException):
                await ctx.send('Nicht in der Lage, die Nachricht zu senden.')

            if isinstance(exc.original, Forbidden):
                await ctx.send('Ich habe dazu nicht die Befugnis.')

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(792783542635200534)
            self.stdout = self.get_channel(792784323819339796)

            embed = Embed(title='Online!',
                          description='Der PyBot ist jetzt online.',
                          colour=0xFF0000,
                          timestamp=datetime.utcnow())
            embed.add_field(name='Prefix', value=db.myroot[0].text)
            embed.set_author(name='Klausurersatz-Bot', icon_url=self.guild.me.avatar_url)
            embed.set_thumbnail(url=self.guild.me.avatar_url)
            await self.stdout.send(embed=embed)
            # await self.stdout.send("Jetzt Online!")
            # await self.stdout.send(db.myroot[0].tag + ": " + db.myroot[0].text)

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print('bot bereit')

        else:
            print('bot wieder verbunden')


bot = Bot()
