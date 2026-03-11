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

    @app_commands.command(name="8ball", description="Tanyakan pertanyaan pada kerang ajaib")
    async def eight_ball(self, interaction: discord.Interaction, pertanyaan: str):
        responses = [
            "Tentu saja! 🔮",
            "Mungkin saja, tapinya entahlah. 🤷",
            "Sangat meragukan... 🙅",
            "Ya, pastinya! ✨",
            "Tidak, jangan berharap. ❌",
            "Tanya lagi nanti... ⏳",
            "Menurut ramalan, iya. 🌟",
            "Jawaban saya adalah tidak. 🛑",
            "Bisa jadi! 🤔"
        ]
        
        jawaban = random.choice(responses)
        embed = discord.Embed(title="🎱 Magic 8-Ball", color=discord.Color.purple())
        embed.add_field(name="Pertanyaan", value=pertanyaan, inline=False)
        embed.add_field(name="Jawaban", value=jawaban, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roll", description="Lempar dadu (contoh: 1d6, 2d20, d100)")
    async def roll(self, interaction: discord.Interaction, dice: str = "1d6"):
        try:
            if 'd' not in dice.lower():
                await interaction.response.send_message("Format salah! Gunakan format seperti `1d6` (1 dadu 6 sisi)", ephemeral=True)
                return
                
            parts = dice.lower().split('d')
            num_dice = int(parts[0]) if parts[0] else 1
            num_sides = int(parts[1])
            
            if num_dice > 20 or num_sides > 100 or num_dice < 1 or num_sides < 2:
                await interaction.response.send_message("Batas maksimum: 20 dadu dan 100 sisi. Minimum 1 dadu dan 2 sisi.", ephemeral=True)
                return
                
            rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
            total = sum(rolls)
            
            embed = discord.Embed(title="🎲 Hasil Lemparan Dadu", color=discord.Color.teal())
            embed.add_field(name="Format Dadu", value=f"`{num_dice}d{num_sides}`", inline=True)
            embed.add_field(name="Total", value=f"**{total}**", inline=True)
            embed.add_field(name="Hasil Detail", value=", ".join(str(r) for r in rolls), inline=False)
            
            await interaction.response.send_message(embed=embed)
        except ValueError:
            await interaction.response.send_message("Format angka tidak valid. Gunakan format seperti `1d6`", ephemeral=True)

    @app_commands.command(name="suit", description="Main Suit Khas Indonesia (Gajah, Semut, Orang)")
    @app_commands.choices(pilihan=[
        app_commands.Choice(name="Gajah (Jempol) 👍", value="gajah"),
        app_commands.Choice(name="Semut (Kelingking) 🤙", value="semut"),
        app_commands.Choice(name="Orang (Telunjuk) ☝️", value="orang"),
    ])
    async def suit(self, interaction: discord.Interaction, pilihan: app_commands.Choice[str]):
        bot_choice = random.choice(["gajah", "semut", "orang"])
        user_choice = pilihan.value
        
        emojis = {"gajah": "👍", "semut": "🤙", "orang": "☝️"}
        
        # Aturan Suit:
        # Gajah menang lwn Orang, Gajah kalah lwn Semut
        # Orang menang lwn Semut, Orang kalah lwn Gajah
        # Semut menang lwn Gajah, Semut kalah lwn Orang
        
        if user_choice == bot_choice:
            result = "Seri! Kita sama kuatnya. 🤝"
            color = discord.Color.gold()
        elif (user_choice == "gajah" and bot_choice == "orang") or \
             (user_choice == "orang" and bot_choice == "semut") or \
             (user_choice == "semut" and bot_choice == "gajah"):
            result = "Kamu Menang! Hebat! 🎉"
            color = discord.Color.green()
        else:
            result = "Kamu Kalah! Coba lagi! 😢"
            color = discord.Color.red()
            
        embed = discord.Embed(title="Pertandingan Suit", color=color)
        embed.add_field(name="Pilihanmu", value=f"{pilihan.name.split(' ')[0]} {emojis[user_choice]}", inline=True)
        embed.add_field(name="Pilihan Bot", value=f"{bot_choice.capitalize()} {emojis[bot_choice]}", inline=True)
        embed.add_field(name="Hasil", value=result, inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))
