# https://discord.com/oauth2/authorize?client_id=1261753157835558933&permissions=8&scope=bot%20applications.commands

import os
import asyncio
import discord
from discord.ext import commands
from discordToken import token 

client = commands.Bot(command_prefix = "r-", intents = discord.Intents.all())

@client.event
async def on_ready():
    await client.tree.sync()
    print("Bot Online")

@client.event
async def on_guild_join(guild):
    print(f"Joined {guild}")

async def load():
    for i in os.listdir("./cogs"):
        if i.endswith(".py"):
            await client.load_extension(f"cogs.{i[:-3]}")

async def main():
    async with client:
        await load()
        await client.start(token)

asyncio.run(main())