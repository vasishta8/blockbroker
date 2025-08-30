import discord, os
from dotenv import load_dotenv
from commands import setup_commands
from crypto_functions import *

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
    print('AngoBot is ready and logged in as', client.user)

@client.event
async def on_message(message):
    print(f"Received message: {message.content} from {message.author}")
    if (message.author == client.user):
        return

setup_commands(tree, DISCORD_GUILD_ID)

client.run(DISCORD_TOKEN)