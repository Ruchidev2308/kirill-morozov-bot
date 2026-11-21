import discord
from discord.ext import commands
from datetime import timedelta
import aiosqlite
import re
def parse_duration(duration_str: str):
    match = re.match(r"^(\d+)([smhd])$", duration_str.lower())
    if not match:
        return None
    amount, unit = int(match.group(1)), match.group(2)
    if unit == "s": return timedelta(seconds=amount)
    if unit == "m": return timedelta(minutes=amount)
    if unit == "h": return timedelta(hours=amount)
    if unit == "d": return timedelta(days=amount)
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def log_action(self, guild_id: int, user_id: int, mod_id: int, action: str, reason: str):
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute(
                "INSERT INTO modlogs (guild_id, user_id, mod_id, action, reason) VALUES (?, ?, ?, ?, ?)",
                (guild_id, user_id, mod_id, action, reason)
            )
            await db.commit()
    @commands.command(name="to", aliases=["mute", "timeout"])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        delta = parse_duration(duration)
        if not delta:
            return await ctx.send("Invalid duration. Use `10s`, `10m`, `2h`, or `1d`.")
        
        await member.timeout(delta, reason=reason)
        await self.log_action(ctx.guild.id, member.id, ctx.author.id, f"TIMEOUT ({duration})", reason)
        await ctx.send(f"Timed out **{member}** for `{duration}` | Reason: {reason}")

    @commands.command(name="rto", aliases=["unmute", "removetimeout"])
    @commands.has_permissions(moderate_members=True)
    async def remove_timeout(self, ctx, member: discord.Member, *, reason: str = "Timeout removed"):
        await member.timeout(None, reason=reason)
        await self.log_action(ctx.guild.id, member.id, ctx.author.id, "REMOVE TIMEOUT", reason)
        await ctx.send(f"Removed timeout for **{member}**.")

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await self.log_action(ctx.guild.id, member.id, ctx.author.id, "WARN", reason)
        await ctx.send(f"Warned **{member}** | Reason: {reason}")
        try:
            await member.send(f"You were warned in **{ctx.guild.name}** for: {reason}")
        except discord.Forbidden:
            pass
    @commands.command(name="modlogs", aliases=["logs", "warnings"])
    @commands.has_permissions(moderate_members=True)
    async def modlogs(self, ctx, member: discord.Member):
        async with aiosqlite.connect("bot_database.db") as db:
            cursor = await db.execute(
                "SELECT id, action, reason, mod_id, timestamp FROM modlogs WHERE guild_id = ? AND user_id = ? ORDER BY id DESC LIMIT 10",
                (ctx.guild.id, member.id)
            )
            rows = await cursor.fetchall()
        if not rows:
            return await ctx.send(f"**{member}** has a clean record.")
        embed = discord.Embed(title=f"Modlogs for {member}", color=discord.Color.orange())
        for row in rows:
            log_id, action, reason, mod_id, timestamp = row
            embed.add_field(
                name=f"Case #{log_id} | {action} ({timestamp[:10]})",
                value=f"**Reason:** {reason} | **Mod:** <@{mod_id}>",
                inline=False
            )
        await ctx.send(embed=embed)
    @commands.command(name="purge", aliases=["clear"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            return await ctx.send("Provide a number between 1 and 100.")
        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"Deleted `{len(deleted) - 1}` messages.")
        await msg.delete(delay=3)
    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("Channel locked.")
    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("Channel unlocked.")
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await self.log_action(ctx.guild.id, member.id, ctx.author.id, "KICK", reason)
        await member.kick(reason=reason)
        await ctx.send(f"Kicked **{member}** | Reason: {reason}")
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await self.log_action(ctx.guild.id, member.id, ctx.author.id, "BAN", reason)
        await member.ban(reason=reason)
        await ctx.send(f"Banned **{member}** | Reason: {reason}")
async def setup(bot):
    await bot.add_cog(Moderation(bot))
