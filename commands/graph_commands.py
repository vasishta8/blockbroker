import discord
from functions.graph_functions import *


def setup_graph_commands(tree: discord.app_commands.CommandTree, guild_id: int):
    @tree.command(name="candlestick_graph", description="Shows the trends of the requested coin in a candlestick graph.", guild=discord.Object(guild_id))
    async def graph_command(interaction: discord.Interaction, coin: str, period: str = "1M"):
        await interaction.response.defer()
        coin = coin.upper()
        period = period.upper()

        valid_periods = ["24H", "1M", "3M", "1Y", "YTD"]
        if period not in valid_periods:
            await interaction.followup.send(f"Invalid period. Choose one of: {', '.join(valid_periods)}")
            return

        status, verdict, graph = await create_candlestick_graph(coin, period)

        print(status, verdict)
        if (status == 200):
            file = discord.File(fp=graph, filename='chart.png')
            embed = discord.Embed(
                title=f"{coin}/USDT Candlestick Chart",
                # description=f"Recent data:\n"
                color=discord.Color.dark_embed()
            )
            embed.set_image(url="attachment://chart.png")
            await interaction.followup.send(embed=embed, file=file)
        elif (status == 404):
            await interaction.followup.send(f"no data found for {coin}.")
