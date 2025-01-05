import os
import discord
from discord.ext import commands

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store user-channel mappings
user_channels = {}

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} is ready!")

@bot.command()
async def register(ctx):
    """Creates a private channel for file uploads"""
    guild = ctx.guild
    user = ctx.author

    if user.id in user_channels:
        await ctx.send("You already have a private channel!")
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }
    
    channel = await guild.create_text_channel(
        f"{user.name}-files",
        overwrites=overwrites,
        topic="Private file storage channel"
    )
    
    user_channels[user.id] = channel.id
    await ctx.send(f"Created your private channel: {channel.mention}")

@bot.command()
async def getcdn(ctx):
    """Lists CDN links for files in user's private channel"""
    if ctx.author.id not in user_channels:
        await ctx.send("You don't have a private channel. Use `!register` first!")
        return

    channel = bot.get_channel(user_channels[ctx.author.id])
    messages = await channel.history(limit=50).flatten()
    
    files = [attach.url for msg in messages for attach in msg.attachments]
    
    if files:
        await ctx.send("Your files:\n" + "\n".join(files))
    else:
        await ctx.send("No files found in your channel.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id in user_channels.values() and message.attachments:
        links = [attach.url for attach in message.attachments]
        await message.channel.send("File URLs:\n" + "\n".join(links))

    await bot.process_commands(message)

# Load token from environment variable
load_dotenv()
TOKEN = "MTMyNTM5NTM2NDE0ODI4NTQ5Mg.GHZPK4.-KzrfY27VBGjFyrGqhLXcblxWEFFbOO9zilB1M"
if not TOKEN:
    raise ValueError("No Discord token found. Set the DISCORD_TOKEN environment variable.")

bot.run(TOKEN)