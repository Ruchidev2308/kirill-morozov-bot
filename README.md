Discord moderation and leveling bot
Inspired by Kirill Morozov from Rina Kent's Monster Trilogy

Moderation: Kick, ban, unban, timeout, untimeout, purge messages, lock/unlock channels and view user moderation history.
Persistent warning system:automatically applies a timeout after reaching 3 warnings.
Leveling role rewards: awards xp per message with cooldowns, tracks member ranks and leaderboards,automatically assigns special roles upon reaching specific level milestones
Character into: responds with an character introduction when pinged in chat

While working on this project, I came across these new concepts:
asynchronous py (asyncio)
discord.ext.commands: separating moderation and leveling logic into extensions
aiosqlite: designing SQL and writing queries for warnings xp and levels
systemd service so the bot runs in the background even after closing the terminal

Setup & Installation -
1. Prerequisites:
   Python 3.10 or higher
   A Discord Bot Token from the [Discord Developer Portal](https://discord.com) with **Server Members Intent** and **Message Content Intent** enabled.

2. Installation
```bash
git clone https://github.com
cd kirill-morozov-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configuration
Create a `.env` file in the root directory and add your bot token:
```env
DISCORD_TOKEN=your_bot_token_here
```

Update the role IDs `GIF_ROLE_ID` and `SPECIAL_ROLE_ID` in `main.py` and `leveling.py` to match your server roles

4. Inviting & Running
a. In the Discord Developer Portal under OAuth2. select the `bot` scope and `Administrator` (or required moderation/role permissions)
b. Open the generated URL to invite the bot to your server.
c. Start the bot:
```bash
python main.py
```
 ps - i also got introduced to git 
