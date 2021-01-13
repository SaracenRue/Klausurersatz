from asyncio import sleep
from datetime import datetime, timedelta
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, bot_has_permissions

from ..data import db


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='kick', brief="Kick-Command")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = 'Kein Grund angegeben.'):
        """Bei Erwähnung eines Users als ersten Parameter und Angabe eines Grundes als optionalen zweiten
        Parameter kickt der Bot den erwähnten User vom Server."""
        if not len(targets):
            await ctx.send('Ein oder mehr benötigte Angaben fehlen.')

        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position
                        and not target.guild_permissions.administrator):
                    await target.kick(reason=reason)

                    embed = Embed(title='Mitglied gekickt',
                                  colour=0xDD2222,
                                  timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [('Mitglied', f'{target.name} a.k.a. {target.display_name}', False),
                              ('Ausgeführt von', ctx.author.display_name, False),
                              ('Grund', reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)

                else:
                    await ctx.send(f'{target.display_name} konnte nicht gekickt werden.')

            await ctx.send('Aktion ausgeführt.')

    @kick_command.error
    async def kick_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send('Keine ausreichenden Berechtigungen um dies auszuführen.')

    @command(name='ban', brief="Ban-Command")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = 'Kein Grund angegeben.'):
        """Bei Erwähnung eines Users als ersten Parameter und Angabe eines Grundes als optionalen zweiten
        Parameter bannt der Bot den erwähnten User vom Server."""
        if not len(targets):
            await ctx.send('Ein oder mehr benötigte Angaben fehlen.')

        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position
                        and not target.guild_permissions.administrator):
                    await target.ban(reason=reason)

                    embed = Embed(title='Mitglied gebannt',
                                  colour=0xDD2222,
                                  timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [('Mitglied', f'{target.name} a.k.a. {target.display_name}', False),
                              ('Ausgeführt von', ctx.author.display_name, False),
                              ('Grund', reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)

                else:
                    await ctx.send(f'{target.display_name} konnte nicht gebannt werden.')

            await ctx.send('Aktion ausgeführt.')

    @ban_command.error
    async def ban_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send('Keine ausreichenden Berechtigungen um dies auszuführen.')

    @command(name='clear', aliases=['purge'], brief="Nachrichten Löschen")
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_message(self, ctx, targets: Greedy[Member], limit: Optional[int] = 1):
        """Dieser Command löscht Nachrichten aus dem Channel, in dem der Command gesendet wurde (Standardmenge = 1
        Nachricht). Optional kann man eine Zahl als Parameter angeben, die die Menge an gelöschten Nachrichten
        erhöht (max. 100). Als weiteren optionalen Parameter kann man ein Mitglied erwähnen, dessen Nachrichten
        spezifisch gelöscht werden sollen."""
        def _check(message):
            return not len(targets) or message.author in targets

        if 0 < limit <= 100:
            with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit,
                                                  check=_check)

                await ctx.send(f'{len(deleted):,} Nachrichten gelöscht.', delete_after=5)
        else:
            await ctx.send('Das angegebene limit ist nicht im ausführbaren Bereich.')

    @command(name="addprofanity", aliases=["addswears", "addcurses"], brief="Verbotene Phrasen hinzufügen")
    @has_permissions(manage_guild=True)
    async def add_profanity(self, ctx, *words):
        """Mit diesem Command kann man Phrasen hinzufügen, die vom Bot gefiltert und gelöscht werden sollen."""
        words = [word.lower() for word in words]
        curses = [w.text for w in db.myroot[1]]
        for word in words:
            if word in curses:
                await ctx.send(word + " ist bereits in der Liste enthalten:", curses)
                continue

            else:
                db.ET.SubElement(db.myroot[1], "wort")
                for wort in db.myroot.iter("wort"):
                    if wort.text == None:
                        wort.text = word
                        break
        db.write()

        embed = Embed(title='Verbotene Phrasen',
                      description='Die folgenden Phrasen sind verboten.',
                      colour=0xFF0000,
                      timestamp=datetime.utcnow())
        fields = []
        for w in db.myroot.iter("wort"):
            fields.append(("Phrase", w.text, False))
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

        await ctx.send("Aktion ausgeführt.")

    @command(name="delprofanity", aliases=["delswears", "delcurses"], brief="Verbotene Phrasen entfernen")
    @has_permissions(manage_guild=True)
    async def remove_profanity(self, ctx, *words):
        """Mit diesem Command können verbotene Phrasen aus der Liste der Phrasen entfernt werden, die der Bot filtert
        und entfernt."""
        words = [word.lower() for word in words]
        curses = [w.text for w in db.myroot[1]]
        for word in words:
            if word in curses:
                for wort in db.myroot.iter("wort"):
                    if word == wort.text:
                        db.myroot[1].remove(wort)
            else:
                await ctx.send("Die Phrase " + word + " ist nicht in der Liste enthalten.")
        db.write()

        embed = Embed(title='Verbotene Phrasen',
                      description='Die folgenden Phrasen sind verboten.',
                      colour=0xFF0000,
                      timestamp=datetime.utcnow())
        fields = []
        for w in db.myroot.iter("wort"):
            fields.append(("Phrase", w.text, False))
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

        await ctx.send("Aktion ausgeführt.")

    @command(name="showprofanity", aliases=["showswears", "showcurses"], brief="Zeigt verbotene Phrasen")
    async def show_profanity(self, ctx):
        """Dieser Command gibt alle aktuell verbotenen Phrasen aus."""
        embed = Embed(title='Verbotene Phrasen',
                      description='Die folgenden Phrasen sind verboten.',
                      colour=0xFF0000,
                      timestamp=datetime.utcnow())
        fields = []
        for w in db.myroot.iter("wort"):
            fields.append(("Phrase", w.text, False))
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

        await ctx.send("Aktion ausgeführt.")

    @command(name="antispam", aliases=["as", "setspam"], brief="Konfiguration des Anti-Spam")
    @has_permissions(manage_messages=True)
    async def setantispam_command(self, ctx, messages, time: Optional[int] = 10):
        """Dieser Command ermöglicht eine Konfiguration der Anti-Spam-Funktion, wobei der erste erforderliche Parameter
        die Anzahl an Nachrichten ist, die in einer bestimmten Zeit als Spam gelten, und der zweite optionale
        Parameter die Zeit in Sekunden angibt, in der die besagte Nachrichtenanzahl geschrieben werden muss, um
        gefiltert zu werden."""
        try:
            int(messages)
        except:
            raise Exception(f"{messages} ist keine Zahl.")

        db.myroot[2][0].text = str(time)
        db.myroot[2][1].text = str(messages)
        db.write()

        embed = Embed(title='Spameinstellung',
                      description=f"{db.myroot[2][1].text} Nachrichten innerhalb von "
                                  f"{db.myroot[2][0].text} Sekunden gilt als Spamming.",
                      colour=0xFF0000,
                      timestamp=datetime.utcnow())
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

        await ctx.send("Aktion ausgeführt.")

    @command(name="spamsettings", aliases=["spamsetting", "sps"], brief="Anti-Spam Einstellungen")
    async def spamsetting_command(self, ctx):
        """Dieser Command gibt die aktuellen Anti-Spam-Einstellungen aus."""
        embed = Embed(title='Spameinstellung',
                      description=f"{db.myroot[2][1].text} Nachrichten innerhalb von "
                                  f"{db.myroot[2][0].text} Sekunden gilt als Spamming.",
                      colour=0xFF0000,
                      timestamp=datetime.utcnow())
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)
        await ctx.send("Aktion ausgeführt.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(792793895926628382)
            # self.mute_role = self.bot.guild.get_role(769882821199134760)
            self.bot.cogs_ready.ready_up('mod')

    @Cog.listener()
    async def on_message(self, message):
        def _check(m):
            return (m.author == message.author
                    and (datetime.utcnow()-m.created_at).seconds < int(db.myroot[2][0].text))

        if not message.author.bot:
            if len(list(filter(lambda m: _check(m), self.bot.cached_messages))) >= int(db.myroot[2][1].text):
                await message.channel.send("Nicht spammen!", delete_after=10)
                await message.delete()

            for w in db.myroot[1]:
                if w.text.lower() in message.content.lower():
                    await message.delete()
                    await message.channel.send("Du darfst dieses Wort hier nicht verwenden.")
                    break

def setup(bot):
    bot.add_cog(Mod(bot))
