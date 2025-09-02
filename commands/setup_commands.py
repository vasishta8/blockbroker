import discord
from .analysis_commands import setup_analysis_commands
from .coin_commands import setup_coin_commands
from .graph_commands import setup_graph_commands


def setup_commands(tree: discord.app_commands.CommandTree, guild_id: int):
    setup_coin_commands(tree=tree, guild_id=guild_id)
    setup_analysis_commands(tree=tree, guild_id=guild_id)
    setup_graph_commands(tree=tree, guild_id=guild_id)
