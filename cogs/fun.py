import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Perintah fun lama telah dihapus dan diganti dengan sistem RPG yang lebih nyata.
    # Gunakan /start untuk memulai petualangan Anda!

async def setup(bot):
    await bot.add_cog(Fun(bot))
