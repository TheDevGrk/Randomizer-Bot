import discord
import random
from discord.ext import commands
from discord import app_commands
import time

class Randomizer(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Randomizer Cog is online")
    
    @app_commands.command(name = "randomizer", description = "Pick a random option! Lots of setting available!")
    async def randomizer(self, interaction: discord.Interaction, options: str, wait: int):
        loadEmoji = "<a:loading:1261772710539952149>"
        optionsList = []
        options = options.replace(", ", ",").replace(" ,", ",") + ","

        for i in options:
            if i == ",":
                optionsList.append(options[:options.index(",")])
                options = options[options.index(",")+1:]
        msg = ""
        for i in optionsList:
            msg = msg + i + "\n"
        msg = msg + "\nThinking " + loadEmoji
        await interaction.response.send_message(msg)

        time.sleep(wait)

        await interaction.edit_original_response(content = f"The Winner is... {optionsList[random.randint(0, (len(optionsList) - 1))]}")

async def setup(client):
    await client.add_cog(Randomizer(client))