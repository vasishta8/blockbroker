import discord
from functions.coin_functions import *


def setup_coin_commands(tree: discord.app_commands.CommandTree, guild_id: int):

    @tree.command(name="last_price", description="Fetches the last price for the requested coin.", guild=discord.Object(guild_id))
    async def price_command(interaction: discord.Interaction, coin: str, currency: str = 'USD'):
        coin = coin.upper()
        status, amount = await get_last_price(coin, currency)
        if (status == 200):
            await interaction.response.send_message(f'Last price of {coin} is: USD {amount}')
        if (status == 404):
            await interaction.response.send_message(f'Unable to fetch the last price of {coin}.')

    @tree.command(name="bid_price", description="Fetches the bid price for the requested coin.", guild=discord.Object(guild_id))
    async def price_command(interaction: discord.Interaction, coin: str, currency: str = 'USD'):
        coin = coin.upper()
        status, amount = await get_bid_price(coin, currency)
        if (status == 200):
            await interaction.response.send_message(f'Bid price of {coin} is: USD {amount}')
        if (status == 404):
            await interaction.response.send_message(f'Unable to fetch the bid price of {coin}.')

    @tree.command(name="ask_price", description="Fetches you the ask price for the requested coin.", guild=discord.Object(guild_id))
    async def price_command(interaction: discord.Interaction, coin: str, currency: str = 'USD'):
        coin = coin.upper()
        status, amount = await get_ask_price(coin, currency)
        if (status == 200):
            await interaction.response.send_message(f'Ask price of {coin} is: USD {amount}')
        if (status == 404):
            await interaction.response.send_message(f'Unable to fetch the ask price of {coin}.')
