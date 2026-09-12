import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import init_db

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

logging.getLogger("discord.ext.commands.bot").setLevel(logging.CRITICAL)

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    init_db()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


async def setup_hook():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
    guild = discord.Object(id=1157664458370465813)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    print(f"Synced {len(synced)} slash commands to guild {guild.id}")

bot.setup_hook = setup_hook

bot.run(TOKEN)
