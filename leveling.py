import discord
from discord.ext import commands
import aiosqlite
import random
import time
class LevelingAndAFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.command(name="afk")
    async def afk(self, ctx, *, reason: str = "AFK"):
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute(
                "INSERT OR REPLACE INTO afk (guild_id, user_id, reason) VALUES (?, ?, ?)",
                (ctx.guild.id, ctx.author.id, reason)
            )
            await db.commit()
        await ctx.send(f"**{ctx.author.display_name}** is now AFK: {reason}")

    @commands.command(name="level", aliases=["rank", "lvl"])
    async def level(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        async with aiosqlite.connect("bot_database.db") as db:
            cursor = await db.execute(
                "SELECT xp, level FROM levels WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, member.id)
            )
            row = await cursor.fetchone()

        if not row:
            return await ctx.send(f"**{member.display_name}** is Level 0 (0 XP).")

        xp, lvl = row
        needed_xp = (lvl + 1) * 100
        await ctx.send(f"**{member.display_name}** | Level: **{lvl}** | XP: `{xp}/{needed_xp}`")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        async with aiosqlite.connect("bot_database.db") as db:
            cursor = await db.execute(
                "SELECT reason FROM afk WHERE guild_id = ? AND user_id = ?",
                (message.guild.id, message.author.id)
            )
            if await cursor.fetchone():
                await db.execute(
                    "DELETE FROM afk WHERE guild_id = ? AND user_id = ?",
                    (message.guild.id, message.author.id)
                )
                await db.commit()
                await message.channel.send(f"Welcome back **{message.author.display_name}**, I removed your AFK.", delete_after=5)

            for mention in message.mentions:
                cursor = await db.execute(
                    "SELECT reason FROM afk WHERE guild_id = ? AND user_id = ?",
                    (message.guild.id, mention.id)
                )
                row = await cursor.fetchone()
                if row:
                    await message.channel.send(f"**{mention.display_name}** is currently AFK: {row[0]}", delete_after=8)

            user_key = (message.guild.id, message.author.id)
            now = time.time()
            if now - self.cooldowns.get(user_key, 0) < 60:
                return
            self.cooldowns[user_key] = now

            cursor = await db.execute(
                "SELECT xp, level FROM levels WHERE guild_id = ? AND user_id = ?",
                (message.guild.id, message.author.id)
            )
            row = await cursor.fetchone()
            xp, lvl = row if row else (0, 0)

            xp += random.randint(15, 25)
            needed_xp = (lvl + 1) * 100

            if xp >= needed_xp:
                lvl += 1
                xp = 0
                await message.channel.send(f"GG {message.author.mention}! You reached **Level {lvl}**!")

                if lvl == 10:
                    gif_role = message.guild.get_role(self.bot.gif_role_id)
                    if gif_role:
                        await message.author.add_roles(gif_role)
                        await message.channel.send(f"{message.author.mention} unlocked **GIF Permissions**!")

                if lvl == 35:
                    special_role = message.guild.get_role(self.bot.special_role_id)
                    if special_role:
                        await message.author.add_roles(special_role)
                        await message.channel.send(f"{message.author.mention} unlocked the **Level 35 Special Role**!")

            await db.execute(
                "INSERT OR REPLACE INTO levels (guild_id, user_id, xp, level) VALUES (?, ?, ?, ?)",
                (message.guild.id, message.author.id, xp, lvl)
            )
            await db.commit()
async def setup(bot):
    await bot.add_cog(LevelingAndAFK(bot))
