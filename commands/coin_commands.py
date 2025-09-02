import discord
from functions.coin_functions import *


def setup_coin_commands(tree: discord.app_commands.CommandTree, guild_id: int):

    @tree.command(name="login", description="Lets you sign in to your Coinbase account.", guild=discord.Object(guild_id))
    async def login_command(interaction: discord.Interaction, usr: str, pwd: str):
        await interaction.response.send_message(f'Successfully logged in to Coinbase account {usr}!')

    @tree.command(name="spot_price", description="Shows you the spot price for the requested coin.", guild=discord.Object(guild_id))
    async def price_command(interaction: discord.Interaction, coin: str, currency: str = 'USD'):
        status, amount, base, currency = get_spot_price(coin, currency)
        if (status == 200):
            await interaction.response.send_message(f'Spot price of {base} is: {currency} {amount}')
        if (status == 404):
            await interaction.response.send_message(f'Unable to fetch the price of {coin} in {currency}.')

    @tree.command(name="buy_price", description="Shows you the buy price for the requested coin.", guild=discord.Object(guild_id))
    async def price_command(interaction: discord.Interaction, coin: str, currency: str = 'USD'):
        status, amount, base, currency = get_buy_price(coin, currency)
        if (status == 200):
            await interaction.response.send_message(f'Buy price of {base} is: {currency} {amount}')
        if (status == 404):
            await interaction.response.send_message(f'Unable to fetch the price of {coin} in {currency}.')

    @tree.command(name="sell_price", description="Shows you the sell price for the requested coin.", guild=discord.Object(guild_id))
    async def price_command(interaction: discord.Interaction, coin: str, currency: str = 'USD'):
        status, amount, base, currency = get_sell_price(coin, currency)
        if (status == 200):
            await interaction.response.send_message(f'Sell price of {coin} is: {currency} {amount}')
        if (status == 404):
            await interaction.response.send_message(f'Unable to fetch the price of {coin} in {currency}.')
