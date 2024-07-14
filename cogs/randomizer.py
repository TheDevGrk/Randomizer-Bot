import discord
import random
from discord.ext import commands
from discord import app_commands
import time
import asyncio

class Randomizer(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Randomizer Cog is online")
    
    @app_commands.command(name = "randomizer", description = "Pick a random option! Lots of setting available!")
    @app_commands.describe(options = "These are the options you want the randomizer to choose from.  Separate each option with a comma (,).")
    @app_commands.describe(wait = "The time you want the randomizer to RaNdOmIzE before it gives you an answer! Add S, M, or H to indicate seconds, minutes or hours, respectively.")
    @app_commands.describe(weights = "These are the weights added to each option, the higher the weight, the more likely that option will be chosen. Separate each weight with a comma (,) and the position of the weights should correspond to the position of the options. Default weight is 1.")
    async def randomizer(self, interaction: discord.Interaction, options: str, wait: str, weights: str):
        loadEmoji = "<a:loading:1261772710539952149>"
        try:
            waitTime = float(wait)
        except:
            for i in wait:
                if i not in "1234567890.smh":
                    wait = wait[:wait.index(i)] + wait[wait.index(i) + 1:]
            for i in wait:
                if i.lower() == "s":
                    waitTime = float(wait[:wait.lower().index("s")])
                elif i.lower() == "m":
                    waitTime = float(wait[:wait.lower().index("m")]) * 60
                elif i.lower() == "h":
                    waitTime = float(wait[:wait.lower().index("h")]) * 3600

        optionsList = []
        options = options.replace(", ", ",").replace(" ,", ",") + ","
        for i in options:
            if i == ",":
                optionsList.append(options[:options.index(",")])
                options = options[options.index(",")+1:]

        weightsList = []
        weights = weights.replace(", ", ",").replace(" ,", ",") + ","
        for i in weights:
            if i == ",":
                try:
                    weightsList.append(int(weights[:weights.index(",")]))
                    weights = weights[weights.index(",")+1:]
                except:
                    weightsList.append(1)
                    weights = weights[weights.index(",")+1:]

        for i in range(len(optionsList)):
            try:
                emptyVar = weightsList[i]
            except:
                weightsList.append(1)

        weightedOptions = []
        for n in range(len(optionsList)):
            for i in range(weightsList[n]):
                weightedOptions.append(optionsList[n])

        msg = ""
        for i in optionsList:
            msg = msg + i + "\n"
        msg = msg + "\nThinking " + loadEmoji
        await interaction.response.send_message(msg)

        await asyncio.sleep(waitTime)

        await interaction.edit_original_response(content = f"The Winner is... {weightedOptions[random.randint(0, (len(optionsList) - 1))]}")

async def setup(client):
    await client.add_cog(Randomizer(client))