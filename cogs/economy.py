import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import random
import time
import datetime

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "economy.db"
        # Setup DB when cog is loaded
        self.bot.loop.create_task(self.setup_db())

    async def setup_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 0,
                    last_daily REAL DEFAULT 0,
                    last_work REAL DEFAULT 0
                )
            ''')
            await db.commit()
            print("Database economy siap.")

    # --- Helper Functions ---
    async def get_balance(self, user_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                return 0

    async def add_money(self, user_id: int, amount: int):
        async with aiosqlite.connect(self.db_path) as db:
            # Pura-pura insert ignore / on conflict update
            await db.execute('''
                INSERT INTO users (user_id, balance) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?
            ''', (user_id, amount, amount))
            await db.commit()

    async def remove_money(self, user_id: int, amount: int) -> bool:
        current_balance = await self.get_balance(user_id)
        if current_balance < amount:
            return False
            
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
            await db.commit()
        return True

    # --- Commands ---

    @app_commands.command(name="dompet", description="Cek saldo Koin Anda atau orang lain")
    async def dompet(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        if target.bot:
            await interaction.response.send_message("Bot tidak punya dompet! 🤖", ephemeral=True)
            return

        balance = await self.get_balance(target.id)
        
        embed = discord.Embed(title="💳 Dompet", color=discord.Color.gold())
        embed.set_author(name=target.display_name, icon_url=target.display_avatar.url if target.display_avatar else None)
        embed.add_field(name="Saldo", value=f"**{balance:,}** Koin 🪙")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kerja", description="Kerja untuk mendapatkan uang (Cooldown 1 jam)")
    async def kerja(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Ambil data last_work
            async with db.execute("SELECT last_work FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                
            last_work = row[0] if row else 0
            
            # Cek cooldown (3600 detik = 1 jam)
            cooldown = 3600
            time_passed = current_time - last_work
            
            if time_passed < cooldown:
                remaining_time = int(cooldown - time_passed)
                minutes, seconds = divmod(remaining_time, 60)
                await interaction.response.send_message(f"Anda masih capek! Istirahat dulu selama **{minutes} menit {seconds} detik** lagi. 😴", ephemeral=True)
                return
                
            # Berhasil kerja
            reward = random.randint(50, 200)
            
            # Update DB (Set last_work & add money)
            await db.execute('''
                INSERT INTO users (user_id, balance, last_work) VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?, last_work = ?
            ''', (user_id, reward, current_time, reward, current_time))
            await db.commit()
            
        jobs = ["Nge-grab", "Jualan Nasi Goreng", "Ngelontong", "Mining Crypto", "Nge-bug bounty", "Jadi kuli bangunan"]
        job = random.choice(jobs)
        
        await interaction.response.send_message(f"💼 Anda pergi **{job}** dan langsung meraup gaji sebesar **{reward} Koin**! 🪙")

    @app_commands.command(name="harian", description="Klaim bonus Koin gratis setiap 24 jam!")
    async def harian(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                
            last_daily = row[0] if row else 0
            
            # Cooldown 24 jam (86400 detik)
            cooldown = 86400
            time_passed = current_time - last_daily
            
            if time_passed < cooldown:
                remaining_time = int(cooldown - time_passed)
                hours, remainder = divmod(remaining_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                await interaction.response.send_message(f"Anda sudah merampok bank hari ini! Tunggu **{hours} jam {minutes} menit** lagi. ⏳", ephemeral=True)
                return
                
            # Klaim berhasil
            reward = 500
            
            await db.execute('''
                INSERT INTO users (user_id, balance, last_daily) VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?, last_daily = ?
            ''', (user_id, reward, current_time, reward, current_time))
            await db.commit()
            
        await interaction.response.send_message(f"🎁 Selamat! Anda mengklaim bonus harian sebesar **{reward} Koin**! 🪙")

    @app_commands.command(name="transfer", description="Kirim Koin ke teman Anda")
    async def transfer(self, interaction: discord.Interaction, target: discord.Member, jumlah: int):
        if jumlah <= 0:
            await interaction.response.send_message("Jumlah transfer tidak valid!", ephemeral=True)
            return
            
        if target.id == interaction.user.id:
            await interaction.response.send_message("Buat apa transfer ke diri sendiri? 🤔", ephemeral=True)
            return
            
        if target.bot:
            await interaction.response.send_message("Bot tidak menerima sedekah! 🤖", ephemeral=True)
            return

        sender_id = interaction.user.id
        receiver_id = target.id
        
        # Coba tarik uang dari sender
        success = await self.remove_money(sender_id, jumlah)
        
        if not success:
            await interaction.response.send_message(f"❌ Transfer Gagal! Saldo Anda tidak cukup. (Butuh {jumlah} Koin)", ephemeral=True)
            return
            
        # Jika berhasil narik, tambahkan ke receiver
        await self.add_money(receiver_id, jumlah)
        
        embed = discord.Embed(title="💸 Transfer Berhasil!", color=discord.Color.green())
        embed.description = f"**{interaction.user.display_name}** mengirim uang ke **{target.display_name}**"
        embed.add_field(name="Jumlah", value=f"{jumlah} Koin 🪙")
        
        await interaction.response.send_message(f"{target.mention}", embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
