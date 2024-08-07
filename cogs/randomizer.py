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

    class RandomizerButtons(discord.ui.View):
        def __init__(self, *, timeout: float = None, optionsList: list, weightsList: list):
            super().__init__(timeout=timeout)
            self.optionsList = optionsList
            self.weightsList = weightsList

        @discord.ui.button(label = "View Randomizer Options", style = discord.ButtonStyle.green)
        async def viewOptions(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed = discord.Embed(title = "Randomizer Options", description = "Below are the options that were inputted for this randomizer and their weights.", color = discord.Colour.green())
            fieldValue = ""
            for i in range(len(self.optionsList)):
                fieldValue = fieldValue + f"Option: {self.optionsList[i]} - Weight: {self.weightsList[i]}\n"
            embed.add_field(name = "------------------------", value = fieldValue)

            await interaction.response.send_message(embed = embed, ephemeral = True)

    randomizer = app_commands.Group(name = "randomizer", description = "Randomizer Command Group")

    @randomizer.command(name = "weighted", description = "Pick a random option! Lots of settings available!")
    @app_commands.describe(options = "Do `/randomizer help command: weighted` for more info")
    @app_commands.describe(wait = "Do `/randomizer help command: weighted` for more info")
    @app_commands.describe(weights = "Do `/randomizer help command: weighted` for more info")
    async def weighted(self, interaction: discord.Interaction, options: str, wait: str, weights: str):
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

        buttonClass = self.RandomizerButtons(optionsList = optionsList, weightsList = weightsList)
        await interaction.response.send_message(embed = discord.Embed(title = "Thinking " + loadEmoji, color = discord.Colour.blue()), view = buttonClass)

        await asyncio.sleep(waitTime)

        await interaction.edit_original_response(embed = discord.Embed(title = f"The winner is... __**{weightedOptions[random.randint(0, (len(weightedOptions) - 1))]}**__", color = discord.Colour.blue()))

    @randomizer.command(name = "help", description = "Find out how to use randomizer commands!")
    async def help(self, interaction: discord.Interaction, command: str = "all"):
        if command == "weighted":
            embed = discord.Embed(title = "Randomizer Weighted Command", description = "This command allows you to input as many options to be randomly chosen from as you want, assign a time until the random option is chosem. and assign weights to each option to give each option a better or worse chance at being chosen!",color = discord.Colour.gold())
            embed.add_field(name = "Options Parameter", value = "These are the options the randomizer will choose from. They can include any character except for commas (,). Add a comma in between each option.")
            embed.add_field(name = "Wait Parameter", value = "This is the time the randomizer will wait before choosing a winner. By default the number input will be seconds, but can you add m or h for minutes and hours respectively instead.")
            embed.add_field(name = "Weights Parameter", value = "This allows you to assign certain weights to each option. Add the weights in the same order as the options that you want to assign them to and separate each weight by a comma (,). Default weight is 1.")
            embed.add_field(name = "Example", value = "```/randomizer weighted options: TestA,TestB,TestC,TestD,TestE wait: 1m weights: 1,2,3,4,5```\nThis will add the options TestA, TestB, TestC, TestD, and TestE to the randomizer and wait 1 minute to choose the winner. TestA is assigned a weight of 1, TestB is assigned a weight of 2, and so on and so forth.")

            await interaction.response.send_message(embed = embed)
        elif command == "all":
            embed = discord.Embed(title = "Randomizer Commands", color = discord.Colour.gold())
            embed.add_field(name = "Randomizer Weighted", value = "This command allows you to input a list of different options to be randomly picked from and assign weights to each option.  You can also adjust the amount of time before the winner is chosen. Do `/randomizer help command: weighted` for more information.")
            
            await interaction.response.send_message(embed = embed)
        else:
            await interaction.response.send_message(embed = discord.Embed(title = "Sorry, I don't know that command!", description = "Try `/randomizer help` to get the fuller list of randomizer commands!", color = discord.Colour.red()))

async def setup(client):
    await client.add_cog(Randomizer(client))