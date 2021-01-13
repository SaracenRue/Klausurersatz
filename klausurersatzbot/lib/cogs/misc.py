from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from ..data import db

class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='prefix', brief="Veränderung des Prefixes")
    @has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, new: str):
        """Bei Angabe eines neuen Prefix als Parameter wird dieser als neuer Prefix gesetzt."""
        if len(new) > 5:
            await ctx.send('Der Prefix darf nicht länger als 5 Zeichen sein.')

        else:
            db.myroot[0].text = new
            db.write()
            await ctx.send(f'Prefix gesetzt zu {new}')

    @change_prefix.error
    async def change_prefix_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send('Du benötigst mehr Berechtigungen, um dies zu tun.')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('misc')

def setup(bot):
    bot.add_cog(Misc(bot))
