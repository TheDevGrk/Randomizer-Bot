from typing import Any
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import asyncio
import random

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
        
    class PresetRandomizerButtons(discord.ui.View):
        def __init__(self, *, timeout: float = None, optionsList: list, weightsList: list):
            super().__init__(timeout=timeout)
            self.optionsList = optionsList
            self.weightsList = weightsList

        @discord.ui.button(label = "View Randomizer Options", style = discord.ButtonStyle.green)
        async def viewOptions(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed = discord.Embed(title = "Preset Randomizer Options", description = "Below are the options that were inputted for this randomizer and their weights.", color = discord.Colour.green())
            fieldValue = ""
            for i in range(len(self.optionsList)):
                fieldValue = fieldValue + f"Option: {self.optionsList[i]} - Weight: {self.weightsList[i]}\n"
            embed.add_field(name = "------------------------", value = fieldValue)

            await interaction.response.send_message(embed = embed, ephemeral = True)

    class PresetSelect(discord.ui.Select):
        def __init__(self, userID: int, cmd):
            self.userID = userID
            self.cmd = cmd
            options = []

            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()

            cursor.execute(f"SELECT * FROM presets WHERE userID = {userID}")
            results = cursor.fetchall()

            resultsDict = {}
            for i in results:
                options.append(discord.SelectOption(label = i[0], description = i[1]))
                resultsDict[i[0]] = list(i)

            super().__init__(placeholder = "Select The Preset", max_values = 1, min_values = 1, options = options)

        async def callback(self, interaction: discord.Interaction):
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()

            cursor.execute(f"SELECT * FROM presets WHERE userID = {interaction.user.id}")
            resultsUnformatted = cursor.fetchall()
            
            if self.cmd == "edit":
                embed = discord.Embed(title = self.values[0], color = discord.Colour.blue())

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

                        await interaction.response.edit_message(embed = embed, view = Preset.EditTypeSelectView(name = i[0]))
                        break
            
            elif self.cmd == "run":
                for i in resultsUnformatted:
                    if i[0] == self.values[0]:
                        loadEmoji = "<a:loading:1261772710539952149>"
                        
                        wait = i[4]
                        options = i[2]
                        weights = i[3]

                        try:
                            waitTime = float(wait)
                        except:
                            for n in wait:
                                if n not in "1234567890.smh":
                                    wait = wait[:wait.index(n)] + wait[wait.index(n) + 1:]
                            for n in wait:
                                if n.lower() == "s":
                                    waitTime = float(wait[:wait.lower().index("s")])
                                elif n.lower() == "m":
                                    waitTime = float(wait[:wait.lower().index("m")]) * 60
                                elif n.lower() == "h":
                                    waitTime = float(wait[:wait.lower().index("h")]) * 3600

                        optionsList = []
                        options = options.replace(", ", ",").replace(" ,", ",") + ","
                        for n in options:
                            if n == ",":
                                optionsList.append(options[:options.index(",")])
                                options = options[options.index(",")+1:]

                        weightsList = []
                        weights = weights.replace(", ", ",").replace(" ,", ",") + ","
                        for n in weights:
                            if n == ",":
                                try:
                                    weightsList.append(int(weights[:weights.index(",")]))
                                    weights = weights[weights.index(",")+1:]
                                except:
                                    weightsList.append(1)
                                    weights = weights[weights.index(",")+1:]

                        for n in range(len(optionsList)):
                            try:
                                emptyVar = weightsList[n]
                            except:
                                weightsList.append(1)

                        weightedOptions = []
                        for n in range(len(optionsList)):
                            for x in range(weightsList[n]):
                                weightedOptions.append(optionsList[n])

                        buttonClass = Preset.PresetRandomizerButtons(optionsList = optionsList, weightsList = weightsList)
                        await interaction.response.send_message(embed = discord.Embed(title = "Thinking " + loadEmoji, color = discord.Colour.blue()), view = buttonClass)

                        await asyncio.sleep(waitTime)

                        await interaction.edit_original_response(embed = discord.Embed(title = f"The winner is... __**{weightedOptions[random.randint(0, (len(optionsList) - 1))]}**__", color = discord.Colour.blue()))

    class PresetSelectView(discord.ui.View):
        def __init__(self, *, timeout = 180, userID, cmd):
            super().__init__(timeout = timeout)
            self.add_item(Preset.PresetSelect(userID = userID, cmd = cmd))

    class EditNameModal(discord.ui.Modal):
        edit = discord.ui.TextInput(
            label = "New Edited Name",
            placeholder = "Enter the new edited name",
            max_length = 32,
            min_length = 1,
            required = True
        )

        def __init__(self, name):
            self.name = name
            
            super().__init__(title = "Edit Your Preset Name")

        async def on_submit(self, interaction: discord.Interaction):
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"UPDATE presets SET name = ? WHERE userID = ? AND name = ?", (str(self.edit), interaction.user.id, self.name))
            db.commit()
            cursor.close()
            db.close()

            await interaction.response.send_message(embed = discord.Embed(title = "Edited your preset name successfully!", color = discord.Colour.green()))

    class EditDescriptionModal(discord.ui.Modal):
        edit = discord.ui.TextInput(
            label = "New Edited Description",
            placeholder = "Enter the new edited description",
            required = True,
            style = discord.TextStyle.paragraph,
            max_length = 512
        )

        def __init__(self, name):
            self.name = name
            
            super().__init__(title = "Edit Your Preset Description")

        async def on_submit(self, interaction: discord.Interaction):
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"UPDATE presets SET description = ? WHERE userID = ? AND name = ?", (str(self.edit), interaction.user.id, self.name))
            db.commit()
            cursor.close()
            db.close()

            await interaction.response.send_message(embed = discord.Embed(title = "Edited your preset description successfully!", color = discord.Colour.green()))
        
    class EditOptionsModal(discord.ui.Modal):
        edit = discord.ui.TextInput(
            label = "New Edited Options",
            placeholder = "Enter the new edited options. Add a comma in between each option.",
            required = True,
            min_length = 3
        )

        def __init__(self, name):
            self.name = name
            
            super().__init__(title = "Edit Your Preset Options")

        async def on_submit(self, interaction: discord.Interaction):
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"UPDATE presets SET options = ? WHERE userID = ? AND name = ?", (str(self.edit), interaction.user.id, self.name))
            db.commit()
            cursor.close()
            db.close()

            await interaction.response.send_message(embed = discord.Embed(title = "Edited your preset options successfully!", color = discord.Colour.green()))
    
    class EditWeightsModal(discord.ui.Modal):
        edit = discord.ui.TextInput(
            label = "New Edited Weights",
            placeholder = "Add the weights in the same order as the options and separate each by a comma.",
            required = True
        )

        def __init__(self, name):
            self.name = name
            
            super().__init__(title = "Edit Your Preset Weights")

        async def on_submit(self, interaction: discord.Interaction):
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"UPDATE presets SET weights = ? WHERE userID = ? AND name = ?", (str(self.edit), interaction.user.id, self.name))
            db.commit()
            cursor.close()
            db.close()

            await interaction.response.send_message(embed = discord.Embed(title = "Edited your preset weights successfully!", color = discord.Colour.green()))

    class EditWaitTimeModal(discord.ui.Modal):
        edit = discord.ui.TextInput(
            label = "New Edited Name",
            placeholder = "This is how long the randomizer will run for. Add s, m, or h for seconds, minutes, and hours.",
            required = True
        )

        def __init__(self, name):
            self.name = name
            super().__init__(title = "Edit Your Preset Wait Time")

        async def on_submit(self, interaction: discord.Interaction):
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"UPDATE presets SET waitTime = ? WHERE userID = ? AND name = ?", (str(self.edit), interaction.user.id, self.name))
            db.commit()
            cursor.close()
            db.close()

            await interaction.response.send_message(embed = discord.Embed(title = "Edited your preset wait time successfully!", color = discord.Colour.green()))

    class EditTypeSelect(discord.ui.Select):
        def __init__(self, name):
            options = [discord.SelectOption(label = "Edit Name", description = "Edit the Preset Name"), 
                       discord.SelectOption(label = "Edit Description", description = "Edit the Preset Description"),
                       discord.SelectOption(label = "Edit Options", description = "Edit the Preset Randomizer Options"),
                       discord.SelectOption(label = "Edit Weights", description = "Edit the Preset Randomizer Option Weights"),
                       discord.SelectOption(label = "Edit Wait Time", description = "Edit the Preset Randomizer Wait Time")]
            self.name = name
            
            super().__init__(placeholder = "Select The Property To Edit", max_values = 1, min_values = 1, options = options)

        async def callback(self, interaction: discord.Interaction):
            if self.values[0] == "Edit Name":
                await interaction.response.send_modal(Preset.EditNameModal(name = self.name))
            elif self.values[0] == "Edit Description":
                await interaction.response.send_modal(Preset.EditDescriptionModal(name = self.name))
            elif self.values[0] == "Edit Options":
                await interaction.response.send_modal(Preset.EditOptionsModal(name = self.name))
            elif self.values[0] == "Edit Weights":
                await interaction.response.send_modal(Preset.EditWeightsModal(name = self.name))
            elif self.values[0] == "Edit Wait Time":
                await interaction.response.send_modal(Preset.EditWaitTimeModal(name = self.name))

    class EditTypeSelectView(discord.ui.View):
        def __init__(self, *, timeout = 180, name):
            super().__init__(timeout = timeout)
            self.add_item(Preset.EditTypeSelect(name = name))

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
        await interaction.response.send_message(view = self.PresetSelectView(userID = interaction.user.id, cmd = "edit"))

    @preset.command(name = "run", description = "Run one of your randomizer presets")
    async def run(self, interaction: discord.Interaction):
        await interaction.response.send_message(view = self.PresetSelectView(userID = interaction.user.id, cmd = "run"))
    
async def setup(client):
    await client.add_cog(Preset(client))