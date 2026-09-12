import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import init_db

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

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

bot.setup_hook = setup_hook

bot.run(TOKEN)
