import discord
from discord.ext import commands
import os

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.guild_members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store user-channel mappings (Use a database for production)
user_channels = {}

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} is ready!")

@bot.command()
async def register(ctx):
    """Command to register a user and create their private channel."""
    guild = ctx.guild
    user = ctx.author

    # Check if the user already has a channel
    if user.id in user_channels:
        await ctx.send("You already have a private channel!")
        return

    # Create a private text channel for the user
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    private_channel = await guild.create_text_channel(
        name=f"{user.name}-files",
        overwrites=overwrites,
        topic="Your private file storage channel"
    )

    # Store the mapping
    user_channels[user.id] = private_channel.id
    await ctx.send(f"Private channel created: {private_channel.mention}")

@bot.command()
async def getcdn(ctx):
    """Command to provide the CDN links of files in the user's private channel."""
    user = ctx.author

    # Check if the user has a private channel
    if user.id not in user_channels:
        await ctx.send("You don't have a private channel. Use `!register` first!")
        return

    channel_id = user_channels[user.id]
    private_channel = bot.get_channel(channel_id)

    # Fetch the last 50 messages and collect file links
    messages = await private_channel.history(limit=50).flatten()
    file_links = [
        attachment.url
        for message in messages
        for attachment in message.attachments
    ]

    if file_links:
        response = "\n".join(file_links)
        await ctx.send(f"Here are your uploaded files:\n{response}")
    else:
        await ctx.send("No files found in your private channel.")

@bot.event
async def on_message(message):
    """Automatically reply with the CDN link when a file is uploaded."""
    if message.author.bot:
        return

    # Check if the message has attachments and is in a user-specific channel
    if message.attachments:
        if message.channel.id in user_channels.values():
            # Respond with the CDN links
            file_links = [attachment.url for attachment in message.attachments]
            response = "\n".join(file_links)
            await message.channel.send(f"Your files are uploaded:\n{response}")

    await bot.process_commands(message)

# Insert your Discord bot token here
bot.run("MTMyNTM5NTM2NDE0ODI4NTQ5Mg.GHZPK4.-KzrfY27VBGjFyrGqhLXcblxWEFFbOO9zilB1M")
