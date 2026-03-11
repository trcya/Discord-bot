import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rps", description="Main Batu Gunting Kertas (Rock Paper Scissors)")
    @app_commands.choices(pilihan=[
        app_commands.Choice(name="Batu 🪨", value="batu"),
        app_commands.Choice(name="Gunting ✂️", value="gunting"),
        app_commands.Choice(name="Kertas 📄", value="kertas"),
    ])
    async def rps(self, interaction: discord.Interaction, pilihan: app_commands.Choice[str]):
        bot_choice = random.choice(["batu", "gunting", "kertas"])
        user_choice = pilihan.value
        
        # Emoji mapping
        emojis = {"batu": "🪨", "gunting": "✂️", "kertas": "📄"}
        
        # Menentukan pemenang
        if user_choice == bot_choice:
            result = "Seri! 🤝"
            color = discord.Color.gold()
        elif (user_choice == "batu" and bot_choice == "gunting") or \
             (user_choice == "gunting" and bot_choice == "kertas") or \
             (user_choice == "kertas" and bot_choice == "batu"):
            result = "Kamu Menang! 🎉"
            color = discord.Color.green()
        else:
            result = "Kamu Kalah! 😢"
            color = discord.Color.red()
            
        embed = discord.Embed(title="Batu Gunting Kertas", color=color)
        embed.add_field(name="Pilihanmu", value=f"{pilihan.name}", inline=True)
        embed.add_field(name="Pilihan Bot", value=f"{bot_choice.capitalize()} {emojis[bot_choice]}", inline=True)
        embed.add_field(name="Hasil", value=result, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Lempar koin (Muka/Belakang)")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Kepala 👦", "Ekor 🦅"])
        
        embed = discord.Embed(title="Lempar Koin", description=f"Koin mendarat di: **{result}**", color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tebakangka", description="Main tebak angka (1-100)")
    async def tebakangka(self, interaction: discord.Interaction):
        number = random.randint(1, 100)
        
        await interaction.response.send_message("Saya telah memikirkan sebuah angka dari 1 sampai 100. Coba tebak!\nKetik angka tebakanmu di chat. Kamu punya 5 kesempatan dan waktu 30 detik.")
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel and m.content.isdigit()
            
        attempts = 0
        max_attempts = 5
        
        while attempts < max_attempts:
            try:
                msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await interaction.followup.send(f"Waktu habis! ⏰ Angka yang benar adalah **{number}**.")
                return
                
            guess = int(msg.content)
            attempts += 1
            
            if guess == number:
                await msg.reply(f"🎉 TEPAT SEKALI! Kamu menebak angka **{number}** dalam {attempts} cobaan!")
                return
            elif guess < number:
                await msg.reply(f"Terlalu kecil! 📉 Kamu masih punya {max_attempts - attempts} kesempatan.")
            else:
                await msg.reply(f"Terlalu besar! 📈 Kamu masih punya {max_attempts - attempts} kesempatan.")
                
        await interaction.followup.send(f"Game over! 😢 Kamu kehabisan kesempatan. Angka yang benar adalah **{number}**.")

async def setup(bot):
    await bot.add_cog(Games(bot))
