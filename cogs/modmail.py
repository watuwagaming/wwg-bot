"""DM modmail forwarding and staff reply logic."""

import discord
from discord.ext import commands

import bot as shared
from helpers import get_channel_by_key


class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # --- DM Modmail: Forward user DMs to staff channel as an embed ---
        if isinstance(message.channel, discord.DMChannel):
            modmail_channel = get_channel_by_key("channels.modmail_id")
            if not modmail_channel:
                return
            embed = discord.Embed(
                description=message.content or "*No text*",
                color=discord.Color.blue(),
                timestamp=message.created_at,
            )
            embed.set_author(
                name=str(message.author),
                icon_url=message.author.display_avatar.url,
            )
            embed.set_footer(text=f"User ID: {message.author.id}")

            await modmail_channel.send(embed=embed)

            if message.attachments:
                for file in message.attachments:
                    await modmail_channel.send(file.url)

            await message.channel.send(
                f"Hey you \U0001f44b\U0001f3fe, {message.author.mention} The Staff will get back to you when they get to see your message"
            )
            try:
                await shared.logger.log_activity("modmail", f"Forwarded DM from {message.author}", user=message.author)
                await shared.logger.increment_stat("modmail_received")
            except Exception:
                pass
            return

        # --- Staff reply: Reply to an embed in the modmail channel to DM the user ---
        modmail_id = shared.config.get("channels.modmail_id", "")
        if modmail_id and message.channel.id == int(modmail_id) and message.reference:
            try:
                ref_msg = await message.channel.fetch_message(message.reference.message_id)
            except discord.NotFound:
                return

            if not ref_msg.embeds:
                return
            footer_text = ref_msg.embeds[0].footer.text or ""
            if not footer_text.startswith("User ID: "):
                return

            user_id = int(footer_text.replace("User ID: ", ""))
            target_user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)

            try:
                if message.content:
                    await target_user.send(message.content)
                if message.attachments:
                    for file in message.attachments:
                        await target_user.send(file.url)
                await message.add_reaction("\u2705")
                try:
                    await shared.logger.log_activity("modmail_reply", f"Staff replied to {target_user}", user=target_user)
                    await shared.logger.increment_stat("modmail_replied")
                except Exception:
                    pass
            except discord.Forbidden:
                await message.channel.send("Could not DM that user \u2014 they may have DMs disabled.")


async def setup(bot):
    await bot.add_cog(Modmail(bot))
