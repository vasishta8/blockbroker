import discord
from discord import ui
from functions.trading_functions import set_binance_api_keys, create_market_buy_order, create_limit_buy_order


class APIKeyModal(ui.Modal, title='Set Your Binance API Keys'):
    """A Modal for securely collecting Binance API and Secret Keys."""
    api_key = ui.TextInput(label='API Key', style=discord.TextStyle.short,
                           placeholder='Enter your Binance API Key', required=True)
    secret_key = ui.TextInput(label='Secret Key', style=discord.TextStyle.short,
                              placeholder='Enter your Binance Secret Key', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        """Callback for when the user submits the modal."""
        user_id = str(interaction.user.id)

        # Defer the response to let the user know we're processing
        await interaction.response.defer(ephemeral=True, thinking=True)

        # Securely store the keys
        await set_binance_api_keys(user_id, self.api_key.value, self.secret_key.value)

        # Send a private confirmation
        await interaction.followup.send("Your Binance API keys have been set securely.", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.followup.send(f'An error occurred: {error}', ephemeral=True)


def setup_trading_commands(tree: discord.app_commands.CommandTree, guild_id: int):

    @tree.command(name="set_api_keys", description="Set your Binance API and Secret Key for trading.", guild=discord.Object(guild_id))
    async def set_keys_command(interaction: discord.Interaction):
        """Sends a modal to the user to securely set their API keys."""
        modal = APIKeyModal()
        await interaction.response.send_modal(modal)

    @tree.command(name="market_buy", description="Place a market buy order.", guild=discord.Object(guild_id))
    @discord.app_commands.describe(
        coin="The ticker symbol of the coin to buy (e.g., BTC, ETH).",
        amount="The quantity of the coin to purchase, not the value in USDT."
    )
    async def market_buy_command(interaction: discord.Interaction, coin: str, amount: float):
        """Command to place a market buy order."""
        user_id = str(interaction.user.id)
        coin = coin.upper()

        # Defer the response as order creation can take time
        await interaction.response.defer(ephemeral=True)

        status, result = await create_market_buy_order(user_id, coin, amount)

        if status == 200:
            # The result is the order object from ccxt
            await interaction.followup.send(f"Successfully placed market buy order for {amount} of {coin}. Order ID: {result['id']}", ephemeral=True)
        else:
            # status 404 or 500
            await interaction.followup.send(f"Error: {result}", ephemeral=True)

    @tree.command(name="limit_buy", description="Place a limit buy order.", guild=discord.Object(guild_id))
    @discord.app_commands.describe(
        coin="The ticker symbol of the coin to buy (e.g., BTC, ETH).",
        amount="The quantity of the coin to purchase, not the value in USDT.",
        price="The price per coin in USDT at which to place the buy order."
    )
    async def limit_buy_command(interaction: discord.Interaction, coin: str, amount: float, price: float):
        """Command to place a limit buy order."""
        user_id = str(interaction.user.id)
        coin = coin.upper()

        await interaction.response.defer(ephemeral=True)

        status, result = await create_limit_buy_order(user_id, coin, amount, price)

        if status == 200:
            await interaction.followup.send(f"Successfully placed limit buy order for {amount} of {coin} at ${price}. Order ID: {result['id']}", ephemeral=True)
        else:
            await interaction.followup.send(f"Error: {result}", ephemeral=True)
