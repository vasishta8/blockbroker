import discord
from crypto_functions import *

def setup_commands(tree: discord.app_commands.CommandTree, guild_id: int):

    @tree.command(name="login", description="Lets you sign in to your Coinbase account.", guild=discord.Object(guild_id))
    async def login_command(interaction: discord.Interaction, usr: str, pwd: str):
        await interaction.response.send_message(f'Successfully logged in to Coinbase account {usr}!')

    @tree.command(name="price", description="Shows you the latest price for the requested coin.", guild=discord.Object(guild_id))
    async def price_command(interaction: discord.Interaction, coin: str):
        status, coin_price = get_price(coin)
        if (status == 200):
            await interaction.response.send_message(f'Current price of {coin} is: ${coin_price}')
        if (status == 404):
            await interaction.response.send_message(f'The coin {coin} was not found.')

