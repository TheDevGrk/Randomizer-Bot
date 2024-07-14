import discord
from discord.ext import commands
from discord import app_commands

class Preset(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Preset Cog is online")

    preset = app_commands.Group(name = "preset", description = "Preset Command Group")

    class CreateModal(discord.ui.Modal, title = "Create a Preset"):
        name = discord.ui.TextInput(
            label = "Preset Name",
            placeholder = "What would you like the preset to be called?",
            max_length = 32,
            min_length = 1,
            required = True
        )

        description = discord.ui.TextInput(
            label = "Preset Description (Optional)",
            required = False,
            style = discord.TextStyle.paragraph,
            max_length = 512
        )

        

    @preset.command(name = "create ", description = "Create a randomizer preset and save it to use later")
    async def create(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.CreateModal())
    
async def setup(client):
    await client.add_cog(Preset(client))