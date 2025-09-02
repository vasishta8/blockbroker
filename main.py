import discord
import os
from dotenv import load_dotenv
from commands.setup_commands import setup_commands

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=DISCORD_GUILD_ID))
    print('BlockBroker is ready and logged in as', client.user)

setup_commands(tree, DISCORD_GUILD_ID)

client.run(DISCORD_TOKEN)
