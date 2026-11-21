import os
from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
import aiosqlite
import asyncio
# make sure your gif and special roles are below the bot role in server settings
TOKEN = os.getenv("DISCORD_TOKEN") #paste ur token in quotations
GIF_ROLE_ID = 1573239218044538880 #u get ts by right clicking on role  and copying id 
SPECIAL_ROLE_ID = 1573239859055960105


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class ModBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?", intents=intents)
        self.gif_role_id = GIF_ROLE_ID
        self.special_role_id = SPECIAL_ROLE_ID

    async def setup_hook(self):
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS modlogs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    mod_id INTEGER,
                    action TEXT,
                    reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS levels (
                    guild_id INTEGER,
                    user_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS afk (
                    guild_id INTEGER,
                    user_id INTEGER,
                    reason TEXT,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await db.commit()

        await self.load_extension("moderation")
        await self.load_extension("leveling")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

bot = ModBot()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Could not find that user.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing argument. Check command format.")
    else:
        print(f"Error: {error}")
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.strip() in (f"<@{bot.user.id}>", f"<@!{bot.user.id}>"):
        embed = discord.Embed(
            title="Kirill Morozov",
            description=(
                "*You called? Be careful whose attention you ask for.*\n\n"
                "I keep order in this server—and I don't forgive twice. "
                "Step out of line, and you'll answer to me."
            ),
            color=discord.Color.from_rgb(15, 15, 20)
        )
        embed.add_field(
            name="Commands (`?`)",
            value="`?warn` • `?to` • `?rto` • `?purge` • `?lock` • `?modlogs` • `?level` • `?afk`",
            inline=False
        )
        embed.set_footer(text="Kirill Morozov • Server Enforcement")
        await message.channel.send(embed=embed)

    await bot.process_commands(message)
bot.run(TOKEN)
