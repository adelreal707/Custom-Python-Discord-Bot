import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import random
import aiohttp
import asyncpraw
from typing import Optional
from typing import Dict, List

load_dotenv()

TOKEN = os.gentenv("DISCORD_TOKEN")

client = discord.Client()

client.run

# prefix is "!" to do commands on a discord server
intents = discord.Intents.default()
intents.message_content = True #Required to read messages
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- DATA STORAGE ---
warnings = {}  # store warnings in memory here

# ---- EVENTS ----
@bot.event
async def on_ready():
    print(f'All systems are a go.. Logged in as {bot.user}')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check if "crazy" is in the message (case-insenstive)
    if "crazy" in message.content.lower():
        # Get the part after "crazy"
        msg_lower = message.content.lower()
        index = msg_lower.find("crazy") + len("crazy")
        rest_of_message = message.content[index:].strip()
        reply = f"Crazy? I was crazy once... {rest_of_message}"
        await message.channel.send(reply)

        # Ensure commands still work
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.text_channels, name="general")
    if welcome_channel:
        await welcome_channel.send(f"Welcome to the server, {member.mention}! Feel free to introduce yourself.")

@bot.event
async def on_member_remove(member):
    farewell_channel = discord.utils.get(member.guild.text_channels, name="general")
    if farewell_channel:
        await farewell_channel.send(f"{member.mention} has left the server. We'll miss you!")

@bot.event
async def level_up(member, new_level):
    level_channel = discord.utils.get(member.guild.text_channels, name="general")
    if level_channel:
        await level_channel.send(f"🎉 Congratulations {member.mention} on reaching level {new_level}!")

@bot.event
async def xp_gain(member, xp_amount):
    xp_channel = discord.utils.get(member.guild.text_channels, name="general")
    if xp_channel:
        await xp_channel.send(f"✨ {member.mention} has gained {xp_amount} XP!")

# ----  COMMANDS ----

# ---- HELP ----

@bot.command()
async def help(ctx):
 page = 0  # Start at page 0
 embed = discord.Embed(title=help_pages[page]["title"], description=help_pages[page]["description"], color=0x00ff00)
 message = await ctx.send(embed=embed)

    # Add navigation reactions
 await message.add_reaction("◀️")
 await message.add_reaction("▶️")

 def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

 while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            if str(reaction.emoji) == "▶️":
                page = (page + 1) % len(help_pages)
            elif str(reaction.emoji) == "◀️":
                page = (page - 1) % len(help_pages)

            new_embed = discord.Embed(title=help_pages[page]["title"], description=help_pages[page]["description"], color=0x00ff00)
            await message.edit(embed=new_embed)
            await message.remove_reaction(reaction, user)
        except:
            break  # Timeout after 60 seconds
help_pages = [
    {
                "title": "Fun & XP Commands",
        "description": """
**!meme** - Get a meme  
**!hello** - Say hello
**!joke** - Get a joke
**!profile [@User]** - Check your profile
**!level [@User]** - Check your level  
**!balance [@User]** - Check your coins  
**!rank [@User]** - Check someone else's level
"""
    },
    {
        "title": "Moderation Commands",
        "description": """
**!ban @User [reason]** - Ban a user
**!mute @User [reason]** - Mute a user
**!unmute @User [reason]** - Unmute a user
**!purge [amount]** - Delete messages
**!kick @User [reason]** - Kick a user  
**!warn @User [reason]** - Warn a user  
**!viewwarnings @User** - Check warnings  
**!clearwarns @User** - Clear warnings  
**!slowmode [seconds]** - Set slowmode in channel
"""
    }
]

# ---- ENTERTAINMENT ----

@bot.command() # Simple hello command
async def hello(ctx):
    await ctx.send(f'Greetings {ctx.author.mention}!')

@bot.command() # Fetch a random meme from Reddit
async def meme(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://reddit.com/r/memes/hot.json?limit=50",
                               headers={"User-agent": "MemeBot"}) as resp:
            if resp.status == 200:
                data = await resp.json()
                posts = data["data"]["children"]
                image_posts = [p for p in posts if p["data"]["url"].endswith((".jpg", ".png", ".gif"))]

                if image_posts:
                    meme = random.choice(image_posts)["data"]["url"]
                    await ctx.send(meme)
                else:
                    await ctx.send("⚠️ No memes found at the moment. Please try again later!")
            else:
                await ctx.send(f"⚠️ API error {resp.status}")

@bot.command() # Fetch a random joke from Reddit
async def joke(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://reddit.com/r/jokes/hot.json?limit=50",
                               headers={"User-agent": "JokeBot"}) as resp:
            if resp.status == 200:
                data = await resp.json()
                posts = data["data"]["children"]
                text_posts = [p for p in posts if not p["data"]["url"].endswith((".jpg", ".png", ".gif"))]

                if text_posts:
                    joke_post = random.choice(text_posts)["data"]
                    joke = f"**{joke_post['title']}**\n\n{joke_post['selftext']}"
                    await ctx.send(joke)
                else:
                    await ctx.send("⚠️ No jokes found at the moment. Please try again later!")
            else:
                await ctx.send(f"⚠️ API error {resp.status}")

@bot.command(aliases=["pfp", "avatar"])
async def profile(ctx, member: discord.Member | None = None):
    member = member or ctx.author  # If no member is mentioned, show the author's avatar

    embed = discord.Embed(
        title=f"{member.name}'s Avatar",
        color=discord.Color.blurple()
    )
    embed.set_image(url=member.display_avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# FIRST ATTEMPT AT LEVELING SYSTEM FAILED, RETRYING LATER

# ---- MODERATION ----

@bot.command() # Purge messages
@commands.has_permissions(manage_messages=True) # Only allows mods/admins
async def purge(ctx, amount: int):
    if amount <= 0:
        await ctx.send("⚠️ Please provide a number greater than 0.", delete_after=5) # Auto-delete
        return
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {len(deleted)} message(s).", delete_after=5) # Auto-delete confirmation

@bot.command() # Ban a user
@commands.has_permissions(ban_members=True) # Only allows mods/admins
async def ban(ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned. Reason: {reason if reason else 'No reason provided.'}")
    except discord.Forbidden:
        await ctx.send("⚠️ I do not have permission to ban this user.")
    except discord.HTTPException:
        await ctx.send("⚠️ Failed to ban the user due to an API error.")

@bot.command() # Kick a user
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    try:
        if member == ctx.author:
            await ctx.send("❌ You can’t kick yourself!")
            return
        if member.bot:
            await ctx.send("🤖 You can’t kick another bot.")
            return

        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} has been kicked. Reason: {reason}")
        await member.send(f"👢 You were kicked from **{ctx.guild.name}**. Reason: {reason}")
    except discord.Forbidden:
        await ctx.send("⚠️ I don’t have permission to kick this user.")
    except discord.HTTPException:
        await ctx.send("⚠️ Something went wrong while trying to kick this user.")   

@bot.command() # Warn a user
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    global warnings
    if member.bot:
        await ctx.send("🤖 You can’t warn a bot.")
        return
    
    # Add warning
    if member.id not in warnings:
        warnings[member.id] = []
    warnings[member.id].append(reason)

    await ctx.send(f"⚠️ {member.mention} has been warned. Reason: {reason}")
    await member.send(f"⚠️ You were warned in **{ctx.guild.name}**. Reason: {reason}")

@bot.command() # See your own warnings
@commands.has_permissions(manage_messages=True)
async def viewwarnings(ctx, member: discord.Member):
    global warnings
    if member.id not in warnings or len(warnings[member.id]) == 0:
        await ctx.send(f"✅ {member.mention} has no warnings.")
    else:
        reasons = '\n'.join([f"{i+1}. {r}" for i, r in enumerate(warnings[member.id])])
        await ctx.send(f"⚠️ Warnings for {member.mention}:\n{reasons}")
warnings: Dict[int, List[str]] = {}

@bot.command() # Mute a user
@commands.has_permissions(mute_members=True) # Only allows mods/admins
async def mute(ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
    try:
        await member.edit(mute=True, reason=reason)
        await ctx.send(f"{member.mention} has been muted. Reason: {reason if reason else 'No reason provided.'}")
    except discord.Forbidden:
        await ctx.send("⚠️ I do not have permission to mute this user.")
    except discord.HTTPException:
        await ctx.send("⚠️ Failed to mute the user due to an API error.")

@bot.command() # Slowmode a chat channel
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int = 0):
    """Set slowmode in the current channel"""
    try:
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.send("✅ Slowmode disabled.")
        else:
            await ctx.send(f"⏱ Slowmode set to {seconds} seconds.")
    except discord.Forbidden:
        await ctx.send("❌ I don’t have permission to manage this channel.")
    except discord.HTTPException:
        await ctx.send("⚠️ Something went wrong while setting slowmode.")

@bot.command() # Unmute a user
@commands.has_permissions(mute_members=True) # Only allows mods/admins
async def unmute(ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
    try:
        await member.edit(mute=False, reason=reason)
        await ctx.send(f"{member.mention} has been unmuted. Reason: {reason if reason else 'No reason provided.'}")
    except discord.Forbidden:
        await ctx.send("⚠️ I do not have permission to unmute this user.")
    except discord.HTTPException:
        await ctx.send("⚠️ Failed to unmute the user due to an API error.")

@bot.command() # Clear warnings for a user
@commands.has_permissions(manage_messages=True)
async def clearwarns(ctx, member: discord.Member):
    global warnings
    if member.id in warnings:
        warnings[member.id] = []
        await ctx.send(f"✅ All warnings for {member.mention} have been cleared.")
    else:
        await ctx.send(f"✅ {member.mention} has no warnings to clear.")

# ---- ERROR HANDLER ----
@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⚠️ You do not have permission to use this command.", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Please specify the number of messages to purge.", delete_after=5)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Please provide a valid number.", delete_after=5)

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You must mention a user to kick. Example: `!kick @User reason`")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You must mention a user to ban. Example: `!ban @User reason`")

@warn.error
async def warn_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You must mention a user to warn. Example: `!warn @User reason`")

@viewwarnings.error
async def viewwarnings_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You must mention a user to view warnings. Example: `!warnings @User`")

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You must mention a user to mute. Example: `!mute @User reason`")

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You must mention a user to unmute. Example: `!unmute @User reason`")

@slowmode.error
async def slowmode_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Please provide a valid number of seconds for slowmode. Example: `!slowmode 10`")

@clearwarns.error
async def clearwarns_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You must mention a user to clear warnings. Example: `!clearwarns @User`")


    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You must mention a user to check XP. Example: `!xp @User`")



