import discord
from functions.analysis_functions import *


def setup_analysis_commands(tree: discord.app_commands.CommandTree, guild_id: int):

    @tree.command(name="quantitative_analysis", description="Suggests you whether to buy, sell or hold the requested coin using quantitative factors.", guild=discord.Object(guild_id))
    async def analysis_command(interaction: discord.Interaction, coin: str):
        await interaction.response.defer()
        coin = coin.upper()
        status, verdict = await quantitative_analysis(coin)
        print(status, verdict)
        if (status == 200):
            recommendation = verdict["recommendation"]
            justification = verdict["justification"]
            await interaction.followup.send(f'The technical analysis suggests you to {recommendation} on {coin}. Justication: {justification}')
        if (status == 404):
            await interaction.followup.send(f'{verdict} {coin}.')

    @tree.command(name="qualitative_analysis", description="Suggests whether to buy, sell or hold the requested coin using qualitative factors.", guild=discord.Object(guild_id))
    async def analysis_command(interaction: discord.Interaction, coin: str):
        await interaction.response.defer()
        coin = coin.upper()
        status, verdict = await qualitative_analysis(coin)
        print(status, verdict)
        if (status == 200):
            recommendation = verdict["recommendation"]
            justification = verdict["justification"]
            await interaction.followup.send(f'The technical analysis suggests you to {recommendation} on {coin}. Justication: {justification}')
        if (status == 404):
            await interaction.followup.send(f'{verdict} {coin}.')

    @tree.command(name="integrated_analysis", description="Suggests whether to buy, sell or hold the requested coin using quantitative and qualitative factors.", guild=discord.Object(guild_id))
    async def analysis_command(interaction: discord.Interaction, coin: str):
        await interaction.response.defer()
        coin = coin.upper()
        status, verdict = await integrated_analysis(coin)
        print(status, verdict)
        if (status == 200):
            recommendation = verdict["recommendation"]
            justification = verdict["justification"]
            await interaction.followup.send(f'The technical analysis suggests you to {recommendation} on {coin}. Justication: {justification}')
        if (status == 404):
            await interaction.followup.send(f'{verdict} {coin}.')
