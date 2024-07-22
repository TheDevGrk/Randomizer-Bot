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
            self.weights = str(self.weights)
            self.name = str(self.name)
            self.description = str(self.description)
            self.options = str(self.options)
            self.waitTime = str(self.waitTime)

            if self.description == "":
                self.description = "No Description Provided"

            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()

            cursor.execute("CREATE TABLE IF NOT EXISTS presets(name TEXT, description TEXT, options TEXT, weights TEXT, waitTime TEXT, userID INT)")
            db.commit()

            cursor.execute("INSERT INTO presets(name, description, options, weights, waitTime, userID) VALUES (?, ?, ?, ?, ?, ?)", (self.name, self.description, self.options, self.weights, self.waitTime, interaction.user.id))
            db.commit()
            cursor.close()
            db.close()

            await interaction.response.send_message(embed = discord.Embed(title = f"Your Preset __{self.name}__ was created", color = discord.Colour.green()))
        
    class EditSelect(discord.ui.Select):
        def __init__(self, userID: int):
            self.userID = userID
            options = []

            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()

            cursor.execute(f"SELECT * FROM presets WHERE userID = {userID}")
            results = cursor.fetchall()

            resultsDict = {}
            for i in results:
                options.append(discord.SelectOption(label = i[0], description = i[1]))
                resultsDict[i[0]] = list(i)

            super().__init__(placeholder = "Select The Preset To Edit", max_values = 1, min_values = 1, options = options)

        async def callback(self, interaction: discord.Interaction):
            embed = discord.Embed(title = self.values[0], color = discord.Colour.blue())

            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()

            cursor.execute(f"SELECT * FROM presets WHERE userID = {interaction.user.id}")
            resultsUnformatted = cursor.fetchall()

            for i in resultsUnformatted:
                if i[0] == self.values[0]:
                    i = list(i)
                    optionsList = []
                    i[2] = i[2].replace(", ", ",").replace(" ,", ",") + ","
                    for n in i[2]:
                        if n == ",":
                            optionsList.append(i[2][:i[2].index(",")])
                            i[2] = i[2][i[2].index(",")+1:]

                    i[2] = optionsList

                    weightsList = []
                    i[3] = i[3].replace(", ", ",").replace(" ,", ",") + ","
                    for n in i[3]:
                        if n == ",":
                            try:
                                weightsList.append(int(i[3][:i[3].index(",")]))
                                i[3] = i[3][i[3].index(",")+1:]
                            except:
                                weightsList.append(1)
                                i[3] = i[3][i[3].index(",")+1:]

                    for n in range(len(optionsList)):
                        try:
                            emptyVar = weightsList[n]
                        except:
                            weightsList.append(1)

                    i[3] = weightsList

                    fieldValue = f"Description:\n{i[1]}\n\nWait Time: {i[4]}\n\n"
                    for n in range(len(i[2])):
                        fieldValue = fieldValue + f"Option: {i[2][n]} - Weight: {i[3][n]}\n"
                    embed.add_field(name = "Information:", value = fieldValue, inline = False)

                    await interaction.response.edit_message(embed = embed)
                    break

    class EditSelectView(discord.ui.View):
        def __init__(self, *, timeout = 180, userID):
            super().__init__(timeout = timeout)
            self.add_item(Preset.EditSelect(userID = userID))

    @preset.command(name = "create", description = "Create a randomizer preset and save it to use later")
    async def create(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.CreateModal())

    @preset.command(name = "list", description = "Lists the randomizer presets you have created")
    async def list(self, interaction: discord.Interaction):
        embed =  discord.Embed(title = f"{interaction.user.name}'s Randomizer Presets", color = discord.Colour.blue())
        
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM presets WHERE userID = {interaction.user.id}")
        resultsUnformatted = cursor.fetchall()
        
        results = []
        for i in resultsUnformatted:
            i = list(i)
            optionsList = []
            i[2] = i[2].replace(", ", ",").replace(" ,", ",") + ","
            for n in i[2]:
                if n == ",":
                    optionsList.append(i[2][:i[2].index(",")])
                    i[2] = i[2][i[2].index(",")+1:]

            i[2] = optionsList

            weightsList = []
            i[3] = i[3].replace(", ", ",").replace(" ,", ",") + ","
            for n in i[3]:
                if n == ",":
                    try:
                        weightsList.append(int(i[3][:i[3].index(",")]))
                        i[3] = i[3][i[3].index(",")+1:]
                    except:
                        weightsList.append(1)
                        i[3] = i[3][i[3].index(",")+1:]

            for n in range(len(optionsList)):
                try:
                    emptyVar = weightsList[n]
                except:
                    weightsList.append(1)

            i[3] = weightsList

            results.append(i)
            
        for i in results:
            fieldValue = f"Description:\n{i[1]}\n\nWait Time: {i[4]}\n\n"
            for n in range(len(i[2])):
                fieldValue = fieldValue + f"Option: {i[2][n]} - Weight: {i[3][n]}\n"
            embed.add_field(name = i[0], value = fieldValue, inline = False)

        await interaction.response.send_message(embed = embed, ephemeral = True)

    @preset.command(name = "edit", description = "Edit your randomizer presets")
    async def edit(self, interaction: discord.Interaction):
        await interaction.response.send_message(view = self.EditSelectView(userID = interaction.user.id))
    
async def setup(client):
    await client.add_cog(Preset(client))