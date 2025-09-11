import discord
from functions.trading_functions import set_binance_api_keys, create_market_buy_order, create_limit_buy_order

def setup_trading_commands(tree: discord.app_commands.CommandTree, guild_id: int):

    @tree.command(name="set_api_keys", description="Set your Binance API and Secret Key for trading.", guild=discord.Object(guild_id))
    async def set_keys_command(interaction: discord.Interaction, api_key: str, secret_key: str):
        """Command to set and store user's Binance API keys."""
        user_id = str(interaction.user.id)
        await set_binance_api_keys(user_id, api_key, secret_key)
        # Use ephemeral=True to make the response visible only to the user for security
        await interaction.response.send_message("Your Binance API keys have been set securely.", ephemeral=True)

    @tree.command(name="market_buy", description="Place a market buy order.", guild=discord.Object(guild_id))
    async def market_buy_command(interaction: discord.Interaction, coin: str, amount: float):
        """Command to place a market buy order."""
        user_id = str(interaction.user.id)
        coin = coin.upper()
        
        # Defer the response as order creation can take time
        await interaction.response.defer(ephemeral=True)

        status, result = await create_market_buy_order(user_id, coin, amount)

        if status == 200:
            # The result is the order object from ccxt
            await interaction.followup.send(f"Successfully placed market buy order for {amount} of {coin}. Order ID: {result['id']}")
        else:
            # status 404 or 500
            await interaction.followup.send(f"Error: {result}")

    @tree.command(name="limit_buy", description="Place a limit buy order.", guild=discord.Object(guild_id))
    async def limit_buy_command(interaction: discord.Interaction, coin: str, amount: float, price: float):
        """Command to place a limit buy order."""
        user_id = str(interaction.user.id)
        coin = coin.upper()

        await interaction.response.defer(ephemeral=True)

        status, result = await create_limit_buy_order(user_id, coin, amount, price)

        if status == 200:
            await interaction.followup.send(f"Successfully placed limit buy order for {amount} of {coin} at ${price}. Order ID: {result['id']}")
        else:
            await interaction.followup.send(f"Error: {result}")
