import discord
import random
from discord.ext import commands
from discord import app_commands

class Randomizer(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Randomizer Cog is online")
    
    @app_commands.command(name = "randomizer", description = "Pick a random option! Lots of setting available!")
    async def randomizer(self, interaction:discord.Interaction, options: str):
        await interaction.response.send_message("This command isn't ready yet, come back later!")

async def setup(client):
    await client.add_cog(Randomizer(client))