import discord
from discord.ext import commands


bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())


@bot.listen("on_connect")
async def on_ready(payload: discord.RawAppCommandPermissionsUpdateEvent):
    print(f'Logged in as {bot.user}')