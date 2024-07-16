import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

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

        options = discord.ui.TextInput(
            label = "Preset Randomizer Options",
            placeholder = "These are the options the randomizer will choose from. Add a comma in between each option.",
            required = True,
            min_length = 3
        )

        weights = discord.ui.TextInput(
            label = "Option Weights",
            required = False,
            placeholder = "Add the weights in the same order as the options and separate each by a comma."
        )

        waitTime = discord.ui.TextInput(
            label = "Randomizer Wait Time",
            required = True,
            placeholder = "This is how long the randomizer will run for. Add s, m, or h for seconds, minutes, and hours."
        )

        async def on_submit(self, interaction: discord.Interaction):
            if self.description == None:
                self.description = "No Description Provided"

            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()

            cursor.execute("CREATE TABLE IF NOT EXISTS presets(name TEXT, description TEXT, options TEXT, weights TEXT, waitTime TEXT, userID INT)")
            db.commit()

            cursor.execute("INSERT INTO presets(name, description, options, weights, waitTime, userID) VALUES (?, ?, ?, ?, ?)", (self.name, self.description, self.options, self.weights, self.waitTime, interaction.user.id))
            db.commit()

            await interaction.response.send_message(embed = discord.Embed(title = f"Your Preset __{self.name}__ was created", color = discord.Colour.green()))
        

    @preset.command(name = "create", description = "Create a randomizer preset and save it to use later")
    async def create(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.CreateModal())
        print(0)
    
async def setup(client):
    await client.add_cog(Preset(client))