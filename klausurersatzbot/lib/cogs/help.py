from typing import Optional

from discord import Embed
from discord.utils import get
from discord.ext.menus import MenuPages, ListPageSource
from discord.ext.commands import Cog
from discord.ext.commands import command


def syntax(command):
    cmd_and_aliases = '|'.join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ('self', 'ctx'):
            params.append(f"[{key}]" if 'NoneType' in str(value) else f"<{key}>")

    params = ' '.join(params)

    return f"```{cmd_and_aliases} {params}```"

class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        
        super().__init__(data, per_page=5)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title='Hilfe',
                      description='Willkommen zum PyBot Hilfs-Menu!',
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(text=f'{offset:,} - {min(len_data, offset+self.per_page-1):,} von {len_data:,} Commands.')

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []

        for entry in entries:
            fields.append((entry.brief or 'Keine Beschreibung', syntax(entry)))

        return await self.write_page(menu, fields)


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    async def cmd_help(self, ctx, command):
        embed = Embed(title=f'Hilfe für `{command}`',
                      description=syntax(command),
                      colour=ctx.author.colour)
        embed.add_field(name='Command Beschreibung', value=command.help)
        await ctx.send(embed=embed)

    @command(name='help', brief="Hilfe zu Commands")
    async def show_help(self, ctx, cmd: Optional[str]):
        """Dieser Command gibt bei Angabe eines Commands ohne Prefix Informationen und Hilfestellung zu diesen.
        Bei fehlender Angabe wird eine vollständige Liste aller Commands und einer kurzen Beschreibung dieser ausgegeben."""
        if cmd is None:
            menu = MenuPages(source=HelpMenu(ctx, list(self.bot.commands)),
                             # clear_reactions_after=False, # Default = False
                             delete_message_after=True,
                             timeout=60.0)
            await menu.start(ctx)

        else:
            if (command := get(self.bot.commands, name=cmd)):
                await self.cmd_help(ctx, command)

            else:
                await ctx.send('Dieser Command existiert nicht.')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('help')

def setup(bot):
    bot.add_cog(Help(bot))