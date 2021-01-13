from datetime import datetime
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog
from discord.ext.commands import command


class Info(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='userinfo', aliases=['memberinfo', 'ui', 'mi'], brief="Benutzerinformationen")
    async def user_info(self, ctx, target: Optional[Member]):
        """Dieser Command gibt nähere Daten zu einem Benutzer aus."""
        target = target or ctx.author

        embed = Embed(title='Benutzerinformation',
                      colour=target.colour,
                      timestamp=datetime.utcnow())

        embed.set_thumbnail(url=target.avatar_url)

        fields = [('Name', str(target), True),
                  ('ID', target.id, True),
                  ('Bot?', target.bot, True),
                  ('Oberste Rolle', target.top_role.mention, True),
                  ('Status', str(target.status).title(), True),
                  ('Aktivität', f'{str(target.activity.type).split(".")[-1].title() if target.activity else "N/A"} '
                               f'{target.activity.name if target.activity else ""}', True),
                  ('Erstellt', target.created_at.strftime('%d/%m/%Y %H:%M:%S'), True),
                  ('Beigetreten', target.joined_at.strftime('%d/%m/%Y %H:%M:%S'), True),
                  ('Geboostet', bool(target.premium_since), True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @command(name='serverinfo', aliases=['guildinfo', 'si', 'gi'], brief="Serverinformationen")
    async def server_info(self, ctx):
        """Dieser Command gibt nägere Informationen zum Server aus."""
        embed = Embed(title='Serverinformation',
                      colour=ctx.guild.owner.colour,
                      timestamp=datetime.utcnow())

        embed.set_thumbnail(url=ctx.guild.icon_url)

        statuses = [len(list(filter(lambda m: str(m.status) == 'online', ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == 'idle', ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == 'dnd', ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == 'offline', ctx.guild.members)))]

        fields = [('ID', ctx.guild.id, True),
                  ('Besitzer', ctx.guild.owner, True),
                  ('Region', ctx.guild.region, True),
                  ('Erstellt', ctx.guild.created_at.strftime('%d/%m/%Y %H:%M:%S'), True),
                  ('Mitglieder', len(ctx.guild.members), True),
                  ('Menschen', len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
                  ('Bots', len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
                  ('Gebannte Mitglieder', len(await ctx.guild.bans()), True),
                  ('Status', f'🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}', True),
                  ('Textkanäle', len(ctx.guild.text_channels), True),
                  ('Sprachkanäle', len(ctx.guild.voice_channels), True),
                  ('Kategorien', len(ctx.guild.categories), True),
                  ('Rollen', len(ctx.guild.roles), True),
                  ('Einladungen', len(await ctx.guild.invites()), True),
                  ('\u200b', '\u200b', True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('info')

def setup(bot):
    bot.add_cog(Info(bot))
