import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import datetime

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    alat_group = app_commands.Group(name="alat", description="Alat-alat utilitas bot / Bot utility tools")

    @alat_group.command(name="hitung", description="Kalkulator sederhana (+, -, *, /)")
    async def alat_hitung(self, interaction: discord.Interaction, angka1: float, operator: str, angka2: float):
        ops = {
            "+": angka1 + angka2,
            "-": angka1 - angka2,
            "*": angka1 * angka2,
            "/": angka1 / angka2 if angka2 != 0 else "Error: Pembagi nol"
        }
        
        result = ops.get(operator, "Operator tidak valid! (+, -, *, /)")
        
        embed = discord.Embed(title="🧮 Kalkulator", color=discord.Color.blue())
        embed.add_field(name="Input", value=f"`{angka1} {operator} {angka2}`", inline=False)
        embed.add_field(name="Hasil", value=f"**{result}**", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @alat_group.command(name="cuaca", description="Lihat perkiraan cuaca di kota tertentu (Simulasi)")
    async def alat_cuaca(self, interaction: discord.Interaction, kota: str):
        # Simulasi cuaca
        import random
        kondisi = ["Cerah ☀️", "Berawan ☁️", "Hujan Ringan 🌦️", "Hujan Lebat 🌧️", "Mendung 🌥️"]
        suhu = f"{25 + (len(kota) % 10)}°C"
        
        embed = discord.Embed(title=f"🌡️ Cuaca di {kota.capitalize()}", color=discord.Color.orange())
        embed.add_field(name="Kondisi", value=random.choice(kondisi), inline=True)
        embed.add_field(name="Suhu", value=suhu, inline=True)
        embed.add_field(name="Kelembaban", value="65%", inline=True)
        embed.set_footer(text="Data simulasi bot.")
        
        await interaction.response.send_message(embed=embed)

    @alat_group.command(name="polling", description="Buat pemungutan suara sederhana")
    async def alat_polling(self, interaction: discord.Interaction, judul: str, opsi1: str, opsi2: str):
        embed = discord.Embed(title=f"📊 Polling: {judul}", color=discord.Color.blurple())
        embed.description = f"1️⃣ {opsi1}\n\n2️⃣ {opsi2}"
        embed.set_footer(text=f"Dibuat oleh {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")

    @alat_group.command(name="uptime", description="Cek sudah berapa lama bot online")
    async def alat_uptime(self, interaction: discord.Interaction):
        await interaction.response.send_message("🚀 Bot sedang dalam performa terbaik dan siap membantu Anda!")

async def setup(bot):
    await bot.add_cog(Utility(bot))
