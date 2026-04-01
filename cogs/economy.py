import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import sqlite3
import random
import time
import datetime

class Economy(commands.Cog):
    # Definisi Item dalam game
    ITEMS = {
        "nasi": {"name": "Nasi Putih 🍚", "type": "ingredient", "price": 5},
        "telur": {"name": "Telur Mentah 🥚", "type": "ingredient", "price": 7},
        "kopi_bubuk": {"name": "Biji Kopi 🫘", "type": "ingredient", "price": 5},
        "nasi_goreng": {"name": "Nasi Goreng 🍛", "type": "food", "price": 25, "hunger": 40, "thirst": -5, "health": 5},
        "air_mineral": {"name": "Air Mineral 💧", "type": "drink", "price": 10, "hunger": 0, "thirst": 50, "health": 0},
        "kopi": {"name": "Kopi Hitam ☕", "type": "drink", "price": 15, "hunger": 0, "thirst": 30, "stress": -10},
        "obat": {"name": "Obat Sakit Kepala 💊", "type": "medical", "price": 50, "health": 20, "stress": -20},
        "pancingan": {"name": "Alat Pancing 🎣", "type": "tool", "price": 500},
        "beliung": {"name": "Beliung ⛏️", "type": "tool", "price": 1000},
        "laptop": {"name": "Laptop Gaming 💻", "type": "tool", "price": 15000},
        "senapan": {"name": "Senapan Angin 🔫", "type": "tool", "price": 5000},
        "umpan": {"name": "Umpan Cacing 🪱", "type": "tool", "price": 25},
        "ikan_lele": {"name": "Ikan Lele Segar 🐟", "type": "ingredient", "price": 100},
        "daging_rusa": {"name": "Daging Rusa Mentah 🥩", "type": "ingredient", "price": 300},
        "ikan_bakar": {"name": "Ikan Bakar 🐟🔥", "type": "food", "price": 150, "hunger": 40, "thirst": -5, "health": 20},
        "steak_rusa": {"name": "Steak Rusa 🥩", "type": "food", "price": 400, "hunger": 80, "thirst": -10, "health": 40}
    }

    JOBS = {
        "pengangguran": {"name": "Pengangguran", "gaji_min": 10, "gaji_max": 50, "hunger": 5, "thirst": 5, "stress": 2, "req_asset": None, "req_item": None},
        "kuli_bangunan": {"name": "Kuli Bangunan 🏗️", "gaji_min": 100, "gaji_max": 200, "hunger": 30, "thirst": 40, "stress": 15, "req_asset": None, "req_item": None},
        "supir_taksi": {"name": "Supir Taksi 🚕", "gaji_min": 250, "gaji_max": 450, "hunger": 15, "thirst": 15, "stress": 20, "req_asset": "mobil", "req_item": None},
        "programmer": {"name": "Programmer 💻", "gaji_min": 500, "gaji_max": 900, "hunger": 10, "thirst": 10, "stress": 35, "req_asset": None, "req_item": "laptop"},
        "dokter": {"name": "Dokter Spesialis 🏥", "gaji_min": 1200, "gaji_max": 2500, "hunger": 20, "thirst": 15, "stress": 40, "req_asset": "mobil", "req_item": None},
        "ceo": {"name": "CEO Perusahaan 👔", "gaji_min": 5000, "gaji_max": 12000, "hunger": 5, "thirst": 10, "stress": 50, "req_asset": "rumah_mewah", "req_item": None},
    }

    VEHICLES = {
        "sepeda": {"name": "Sepeda Gunung 🚲", "price": 2500},
        "motor": {"name": "Motor Supra 🏍️", "price": 15000},
        "mobil": {"name": "Mobil Sedan 🚗", "price": 75000},
        "sport": {"name": "Mobil Sport 🏎️", "price": 500000}
    }

    PROPERTIES = {
        "kosan": {"name": "Kamar Kos 🛏️", "price": 25000},
        "kontrakan": {"name": "Rumah Kontrakan 🏚️", "price": 60000},
        "rumah": {"name": "Rumah Minimalis 🏠", "price": 150000},
        "apartemen": {"name": "Apartemen VIP 🏢", "price": 750000},
        "rumah_mewah": {"name": "Rumah Mewah Megah 🏰", "price": 1500000},
        "mansion": {"name": "Mansion Eksklusif 🏛️", "price": 5000000}
    }

    BUSINESSES = {
        "warteg": {"name": "Warteg Barokah 🍛", "price": 100000, "income": 5000, "cooldown": 86400},
        "cafe": {"name": "Cafe Kekinian ☕", "price": 500000, "income": 30000, "cooldown": 86400},
        "startup": {"name": "Tech Startup 🚀", "price": 2500000, "income": 200000, "cooldown": 86400}
    }

    RECIPES = {
        "nasi_goreng": {
            "name": "Nasi Goreng Spesial 🍛",
            "ingredients": {"nasi": 1, "telur": 1},
            "cost": 5
        },
        "kopi": {
            "name": "Kopi Hitam Mantap ☕",
            "ingredients": {"kopi_bubuk": 1, "air_mineral": 1},
            "cost": 2
        },
        "ikan_bakar": {
            "name": "Ikan Bakar Spesial 🐟🔥",
            "ingredients": {"ikan_lele": 1},
            "cost": 10
        },
        "steak_rusa": {
            "name": "Steak Rusa Premium 🥩",
            "ingredients": {"daging_rusa": 1},
            "cost": 25
        }
    }

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
                    bank INTEGER DEFAULT 0,
                    health INTEGER DEFAULT 100,
                    hunger INTEGER DEFAULT 100,
                    thirst INTEGER DEFAULT 100,
                    stress INTEGER DEFAULT 0,
                    job_id TEXT DEFAULT 'pengangguran',
                    business_id TEXT DEFAULT NULL,
                    last_daily REAL DEFAULT 0,
                    last_work REAL DEFAULT 0
                )
            ''')
            # Migrasi data lama kalau perlu
            columns = [
                ("bank", "INTEGER DEFAULT 0"),
                ("health", "INTEGER DEFAULT 100"),
                ("hunger", "INTEGER DEFAULT 100"),
                ("thirst", "INTEGER DEFAULT 100"),
                ("stress", "INTEGER DEFAULT 0"),
                ("job_id", "TEXT DEFAULT 'pengangguran'"),
                ("business_id", "TEXT DEFAULT NULL")
            ]
            for col_name, col_type in columns:
                try:
                    await db.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    pass

            await db.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    user_id INTEGER,
                    item_id TEXT,
                    quantity INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, item_id)
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    user_id INTEGER,
                    asset_type TEXT,
                    asset_id TEXT,
                    PRIMARY KEY (user_id, asset_type, asset_id)
                )
            ''')
            await db.commit()
            print("Database economy & life simulation siap.")

    # --- Helper Functions ---
    async def get_user_data(self, user_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                
                # Auto-insert default data if not exists
                await db.execute('''
                    INSERT INTO users (user_id) VALUES (?)
                ''', (user_id,))
                await db.commit()
                async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor2:
                    new_row = await cursor2.fetchone()
                    return dict(new_row)

    async def update_user_stat(self, user_id: int, stat: str, amount: int) -> int:
        """Memperbarui stat user (balance, bank, health, hunger, thirst, stress) dan mengembalikan nilai baru."""
        # Pastikan tidak ada SQL injection dengan memeriksa nama stat
        valid_stats = ['balance', 'bank', 'health', 'hunger', 'thirst', 'stress']
        if stat not in valid_stats:
            raise ValueError(f"Stat {stat} tidak valid.")
            
        async with aiosqlite.connect(self.db_path) as db:
            # Gunakan ON CONFLICT jika user belum ada, lalu set nilai tambahannya (atau default + amount)
            await db.execute(f'''
                INSERT INTO users (user_id, {stat}) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET {stat} = {stat} + ?
            ''', (user_id, amount, amount))
            
            # Khusus untuk health, hunger, thirst maksimum 100, stress maks 100, min 0
            if stat in ['health', 'hunger', 'thirst']:
                await db.execute(f"UPDATE users SET {stat} = MIN(100, MAX(0, {stat})) WHERE user_id = ?", (user_id,))
            elif stat == 'stress':
                await db.execute(f"UPDATE users SET {stat} = MIN(100, MAX(0, {stat})) WHERE user_id = ?", (user_id,))
            elif stat in ['balance', 'bank']:
                await db.execute(f"UPDATE users SET {stat} = MAX(0, {stat}) WHERE user_id = ?", (user_id,))
                
            await db.commit()
            
            # Ambil nilai baru
            async with db.execute(f"SELECT {stat} FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def set_user_stat(self, user_id: int, stat: str, value):
        """Mengeset stat user ke nilai tertentu."""
        valid_stats = ['balance', 'bank', 'health', 'hunger', 'thirst', 'stress', 'job_id', 'business_id', 'last_work', 'last_daily']
        if stat not in valid_stats:
            raise ValueError(f"Stat {stat} tidak valid.")
            
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f'''
                INSERT INTO users (user_id, {stat}) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET {stat} = ?
            ''', (user_id, value, value))
            
            # Batasi nilai jika statnya bertipe angka yang memiliki limit
            if stat in ['health', 'hunger', 'thirst', 'stress']:
                await db.execute(f"UPDATE users SET {stat} = MIN(100, MAX(0, {stat})) WHERE user_id = ?", (user_id,))
            
            await db.commit()

    async def get_inventory(self, user_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT item_id, quantity FROM inventory WHERE user_id = ? AND quantity > 0", (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return {row[0]: row[1] for row in rows}
                
    async def add_item(self, user_id: int, item_id: str, quantity: int = 1):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)
                ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + ?
            ''', (user_id, item_id, quantity, quantity))
            await db.commit()
            
    async def remove_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        inv = await self.get_inventory(user_id)
        if inv.get(item_id, 0) < quantity:
            return False
            
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?
            ''', (quantity, user_id, item_id))
            await db.commit()
        return True

    async def get_assets(self, user_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT asset_type, asset_id FROM assets WHERE user_id = ?", (user_id,)) as cursor:
                rows = await cursor.fetchall()
                assets = {'vehicle': [], 'property': []}
                for row in rows:
                    assets[row[0]].append(row[1])
                return assets
                
    async def add_asset(self, user_id: int, asset_type: str, asset_id: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR IGNORE INTO assets (user_id, asset_type, asset_id) VALUES (?, ?, ?)
            ''', (user_id, asset_type, asset_id))
            await db.commit()

    # --- Commands ---

    @app_commands.command(name="dompet", description="Cek status keuangan dan kondisi fisik Anda atau orang lain")
    async def dompet(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        if target.bot:
            await interaction.response.send_message("Bot tidak punya dompet! 🤖", ephemeral=True)
            return

        data = await self.get_user_data(target.id)
        
        embed = discord.Embed(title=f"📊 Status Kehidupan: {target.display_name}", color=discord.Color.blue())
        embed.set_thumbnail(url=target.display_avatar.url if target.display_avatar else None)
        
        # Keuangan
        uang_desc = f"🪙 **Uang Tunai:** {data['balance']:,} Koin\n🏦 **Bank:** {data['bank']:,} Koin"
        embed.add_field(name="💰 Keuangan", value=uang_desc, inline=False)
        
        # Karir & Bisnis
        pekerjaan = data['job_id'].replace('_', ' ').title() if data['job_id'] else "Pengangguran"
        embed.add_field(name="💼 Karir", value=f"**Pekerjaan:** {pekerjaan}", inline=True)
        
        bisnis = data['business_id'].replace('_', ' ').title() if data['business_id'] else "Belum punya"
        embed.add_field(name="🏢 Bisnis", value=f"**Kepemilikan:** {bisnis}", inline=True)
        
        # Status Fisik
        def make_bar(val):
            filled = int(val / 100 * 10)
            return "█" * filled + "░" * (10 - filled)
            
        health_bar = make_bar(data['health'])
        hunger_bar = make_bar(data['hunger'])
        thirst_bar = make_bar(data['thirst'])
        stress_bar = make_bar(data['stress'])
        
        fisik_desc = (
            f"❤️ **Kesehatan:** {data['health']}/100 `[{health_bar}]`\n"
            f"🍔 **Lapar:** {data['hunger']}/100 `[{hunger_bar}]`\n"
            f"💧 **Haus:** {data['thirst']}/100 `[{thirst_bar}]`\n"
            f"😫 **Stress:** {data['stress']}/100 `[{stress_bar}]`"
        )
        embed.add_field(name="🏃 Kondisi Fisik", value=fisik_desc, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kerja", description="Bekerja untuk mendapatkan uang (Cooldown 1 jam)")
    async def kerja(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        
        data = await self.get_user_data(user_id)
        
        # Cek darah & status
        if data['health'] <= 0:
            await interaction.response.send_message("🏥 Anda sedang dirawat di Rumah Sakit! Gunakan /berobat sebelum bisa bekerja.", ephemeral=True)
            return
            
        if data['hunger'] <= 20 or data['thirst'] <= 20:
            await interaction.response.send_message("😵 Anda terlalu lapar/haus untuk bekerja! Segera /makan atau /minum sesuatu.", ephemeral=True)
            return
            
        if data['stress'] >= 90:
            await interaction.response.send_message("😫 Anda terlalu stress! Pergi /tidur di hotel/rumah atau liburan dulu.", ephemeral=True)
            return

        # Cooldown 1 jam
        last_work = data['last_work']
        cooldown = 3600
        time_passed = current_time - last_work
        
        if time_passed < cooldown:
            remaining_time = int(cooldown - time_passed)
            minutes, seconds = divmod(remaining_time, 60)
            await interaction.response.send_message(f"Anda masih capek! Istirahat dulu selama **{minutes} menit {seconds} detik** lagi. 😴", ephemeral=True)
            return
            
        # Sistem job
        job_id = data['job_id']
        cur_job = self.JOBS.get(job_id, self.JOBS["pengangguran"])
        reward = random.randint(cur_job["gaji_min"], cur_job["gaji_max"])
        
        # Update stat & uang
        await self.update_user_stat(user_id, 'hunger', -cur_job['hunger'])
        await self.update_user_stat(user_id, 'thirst', -cur_job['thirst'])
        await self.update_user_stat(user_id, 'stress', cur_job['stress'])
        await self.update_user_stat(user_id, 'balance', reward)
        await self.set_user_stat(user_id, 'last_work', current_time)
        
        embed = discord.Embed(title="💼 Pulang Kerja", color=discord.Color.green())
        embed.description = f"Anda bekerja keras sebagai **{cur_job['name']}** dan mendapat gaji sebesar **{reward:,} Koin**! 🪙\n\n**Dampak Fisik:**"
        embed.add_field(name="🍔 Lapar", value=f"-{cur_job['hunger']}", inline=True)
        embed.add_field(name="💧 Haus", value=f"-{cur_job['thirst']}", inline=True)
        embed.add_field(name="😫 Stress", value=f"+{cur_job['stress']}", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="harian", description="Klaim bonus Koin gratis setiap 24 jam!")
    async def harian(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        
        data = await self.get_user_data(user_id)
        last_daily = data['last_daily']
        cooldown = 86400
        time_passed = current_time - last_daily
        
        if time_passed < cooldown:
            remaining_time = int(cooldown - time_passed)
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            await interaction.response.send_message(f"Anda sudah merampok bank hari ini! Tunggu **{hours} jam {minutes} menit** lagi. ⏳", ephemeral=True)
            return
            
        reward = 500
        await self.update_user_stat(user_id, 'balance', reward)
        await self.set_user_stat(user_id, 'last_daily', current_time)
        
        await interaction.response.send_message(f"🎁 Selamat! Anda mengklaim bonus harian sebesar **{reward:,} Koin**! 🪙")

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
        
        sender_data = await self.get_user_data(sender_id)
        
        if sender_data['balance'] < jumlah:
            await interaction.response.send_message(f"❌ Transfer Gagal! Saldo Tunai Anda tidak cukup. (Sisa: {sender_data['balance']:,} Koin)", ephemeral=True)
            return
            
        await self.update_user_stat(sender_id, 'balance', -jumlah)
        await self.update_user_stat(receiver_id, 'balance', jumlah)
        
        embed = discord.Embed(title="💸 Transfer Berhasil!", color=discord.Color.green())
        embed.description = f"**{interaction.user.display_name}** mengirim uang tunai ke **{target.display_name}**"
        embed.add_field(name="Jumlah", value=f"{jumlah:,} Koin 🪙")
        
        await interaction.response.send_message(f"{target.mention}", embed=embed)

    @app_commands.command(name="nabung", description="Simpan uang tunai Anda ke Bank")
    async def nabung(self, interaction: discord.Interaction, jumlah: int):
        if jumlah <= 0:
            await interaction.response.send_message("Jumlah tidak valid!", ephemeral=True)
            return
            
        user_id = interaction.user.id
        data = await self.get_user_data(user_id)
        
        if data['balance'] < jumlah:
            await interaction.response.send_message(f"Uang tunai Anda tidak cukup! (Tunai: {data['balance']:,})", ephemeral=True)
            return
            
        await self.update_user_stat(user_id, 'balance', -jumlah)
        await self.update_user_stat(user_id, 'bank', jumlah)
        
        await interaction.response.send_message(f"🏦 Anda berhasil menabung **{jumlah:,} Koin** ke Bank.")

    @app_commands.command(name="tarik", description="Tarik uang dari Bank ke tunai")
    async def tarik(self, interaction: discord.Interaction, jumlah: int):
        if jumlah <= 0:
            await interaction.response.send_message("Jumlah tidak valid!", ephemeral=True)
            return
            
        user_id = interaction.user.id
        data = await self.get_user_data(user_id)
        
        if data['bank'] < jumlah:
            await interaction.response.send_message(f"Saldo Bank Anda tidak cukup! (Saldo: {data['bank']:,})", ephemeral=True)
            return
            
        await self.update_user_stat(user_id, 'bank', -jumlah)
        await self.update_user_stat(user_id, 'balance', jumlah)
        
        await interaction.response.send_message(f"🏧 Anda berhasil menarik **{jumlah:,} Koin** dari Bank.")

    @app_commands.command(name="toko", description="Lihat daftar barang yang dijual di toko")
    async def toko(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛒 Toko Serba Ada", color=discord.Color.blue())
        for item_id, info in self.ITEMS.items():
            desc = f"Harga: **{info['price']:,} Koin**\n"
            if info['type'] == 'food':
                desc += f"🍔 +{info['hunger']} Lapar"
            elif info['type'] == 'drink':
                desc += f"💧 +{info['thirst']} Haus"
            elif info['type'] == 'medical':
                desc += f"❤️ +{info.get('health', 0)} Darah"
            elif info['type'] == 'tool':
                desc += "Alat untuk bekerja"
                
            embed.add_field(name=f"{info['name']} (`{item_id}`)", value=desc, inline=True)
            
        embed.set_footer(text="Gunakan /beli <item_id> <jumlah> untuk membeli.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="beli", description="Beli barang dari toko")
    async def beli(self, interaction: discord.Interaction, item_id: str, jumlah: int = 1):
        if jumlah <= 0:
            await interaction.response.send_message("Jumlah tidak valid!", ephemeral=True)
            return
            
        if item_id not in self.ITEMS:
            await interaction.response.send_message("Barang tidak ditemukan di toko!", ephemeral=True)
            return
            
        item = self.ITEMS[item_id]
        total_harga = item['price'] * jumlah
        user_id = interaction.user.id
        
        data = await self.get_user_data(user_id)
        if data['balance'] < total_harga:
            await interaction.response.send_message(f"Uang tunai tidak cukup! (Total: {total_harga:,} Koin)", ephemeral=True)
            return
            
        await self.update_user_stat(user_id, 'balance', -total_harga)
        await self.add_item(user_id, item_id, jumlah)
        
        await interaction.response.send_message(f"🛍️ Anda berhasil membeli **{jumlah}x {item['name']}** seharga {total_harga:,} Koin!")

    @app_commands.command(name="inventory", description="Lihat isi tas Anda")
    async def inventory(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        inv = await self.get_inventory(user_id)
        
        if not inv:
            await interaction.response.send_message("Tas Anda kosong melompong. 🎒", ephemeral=True)
            return
            
        embed = discord.Embed(title=f"🎒 Tas {interaction.user.display_name}", color=discord.Color.orange())
        for item_id, quantity in inv.items():
            if item_id in self.ITEMS:
                name = self.ITEMS[item_id]['name']
                embed.add_field(name=name, value=f"Jumlah: {quantity}", inline=True)
                
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="makan", description="Makan sesuatu dari tas Anda")
    async def makan(self, interaction: discord.Interaction, item_id: str):
        if item_id not in self.ITEMS or self.ITEMS[item_id]['type'] != 'food':
            await interaction.response.send_message("Itu bukan makanan!", ephemeral=True)
            return
            
        user_id = interaction.user.id
        success = await self.remove_item(user_id, item_id, 1)
        if not success:
            await interaction.response.send_message("Anda tidak punya makanan ini di tas!", ephemeral=True)
            return
            
        item = self.ITEMS[item_id]
        await self.update_user_stat(user_id, 'hunger', item.get('hunger', 0))
        await self.update_user_stat(user_id, 'thirst', item.get('thirst', 0))
        await self.update_user_stat(user_id, 'health', item.get('health', 0))
        
        await interaction.response.send_message(f"🍽️ Anda telah memakan **{item['name']}**. Nyam nyam!")

    @app_commands.command(name="minum", description="Minum sesuatu dari tas Anda")
    async def minum(self, interaction: discord.Interaction, item_id: str):
        if item_id not in self.ITEMS or self.ITEMS[item_id]['type'] != 'drink':
            await interaction.response.send_message("Itu bukan minuman!", ephemeral=True)
            return
            
        user_id = interaction.user.id
        success = await self.remove_item(user_id, item_id, 1)
        if not success:
            await interaction.response.send_message("Anda tidak punya minuman ini di tas!", ephemeral=True)
            return
            
        item = self.ITEMS[item_id]
        await self.update_user_stat(user_id, 'thirst', item.get('thirst', 0))
        await self.update_user_stat(user_id, 'hunger', item.get('hunger', 0))
        await self.update_user_stat(user_id, 'stress', item.get('stress', 0))
        
        await interaction.response.send_message(f"🥤 Anda meminum **{item['name']}**. Segarrr!")

    @app_commands.command(name="tidur", description="Tidur di hotel letih, memulihkan stress & health (Bayar 100 Koin)")
    async def tidur(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = await self.get_user_data(user_id)
        
        harga = 100
        if data['balance'] < harga:
            await interaction.response.send_message("Anda tidak punya uang untuk sewa kamar hotel! Bekerja dulu.", ephemeral=True)
            return
            
        await self.update_user_stat(user_id, 'balance', -harga)
        await self.update_user_stat(user_id, 'health', 50) # +50 health
        await self.update_user_stat(user_id, 'stress', -50) # -50 stress
        
        await interaction.response.send_message("🛌 Anda menginap di hotel dan tidur nyenyak. Stress berkurang drastis, kesehatan pulih!")

    @app_commands.command(name="berobat", description="Pergi ke Rumah Sakit untuk memulihkan semua darah (Bayar 500 Koin)")
    async def berobat(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = await self.get_user_data(user_id)
        
        harga = 500
        if data['balance'] < harga:
            await interaction.response.send_message(f"Uang Anda tidak cukup untuk berobat! (Butuh {harga} Koin)", ephemeral=True)
            return
            
        await self.update_user_stat(user_id, 'balance', -harga)
        await self.set_user_stat(user_id, 'health', 100)
        
        await interaction.response.send_message("🏥 Dokter berhasil menyembuhkan Anda. Kesehatan kembali maksimal (100)!")

    @app_commands.command(name="pekerjaan", description="Lihat daftar pekerjaan yang tersedia")
    async def pekerjaan(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📋 Pusat Karir", description="Gunakan `/lamar <id_pekerjaan>` untuk mendaftar.", color=discord.Color.blue())
        for j_id, info in self.JOBS.items():
            if j_id == "pengangguran":
                continue
            req_text = []
            if info['req_asset']:
                req_text.append(f"Aset: {info['req_asset'].title()}")
            if info['req_item']:
                req_text.append(f"Item: {info['req_item'].title()}")
                
            req = ", ".join(req_text) if req_text else "Tidak Ada"
            embed.add_field(name=f"{info['name']} (`{j_id}`)", value=f"Gaji: **{info['gaji_min']}-{info['gaji_max']}**\nSyarat: {req}", inline=False)
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="lamar", description="Lamar pekerjaan baru")
    async def lamar(self, interaction: discord.Interaction, job_id: str):
        if job_id not in self.JOBS or job_id == "pengangguran":
            await interaction.response.send_message("Pekerjaan tidak ditemukan! Cek `/pekerjaan`.", ephemeral=True)
            return
            
        user_id = interaction.user.id
        job_info = self.JOBS[job_id]
        
        # Pengecekan Syarat
        if job_info['req_asset']:
            assets = await self.get_assets(user_id)
            if job_info['req_asset'] not in assets['vehicle'] and job_info['req_asset'] not in assets['property']:
                await interaction.response.send_message(f"❌ Anda belum memenuhi syarat! Anda butuh memiliki aset: **{job_info['req_asset'].title()}**.", ephemeral=True)
                return
                
        if job_info['req_item']:
            inv = await self.get_inventory(user_id)
            if job_info['req_item'] not in inv:
                await interaction.response.send_message(f"❌ Anda belum memenuhi syarat! Anda butuh memiliki item: **{job_info['req_item'].title()}**.", ephemeral=True)
                return
                
        await self.set_user_stat(user_id, 'job_id', job_id)
        await interaction.response.send_message(f"🎉 Selamat! Anda telah diterima bekerja sebagai **{job_info['name']}**.")

    @app_commands.command(name="resign", description="Keluar dari pekerjaan saat ini")
    async def resign(self, interaction: discord.Interaction):
        await self.set_user_stat(interaction.user.id, 'job_id', 'pengangguran')
        await interaction.response.send_message("Anda telah resign dan sekarang menjadi **Pengangguran**.")

    @app_commands.command(name="aset", description="Lihat aset properti dan kendaraan Anda")
    async def aset(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        assets = await self.get_assets(user_id)
        
        embed = discord.Embed(title=f"🏡 Aset Kekayaan {interaction.user.display_name}", color=discord.Color.gold())
        
        kendaraan = [self.VEHICLES[v]['name'] for v in assets['vehicle'] if v in self.VEHICLES]
        mobil_str = "\n".join(kendaraan) if kendaraan else "Tidak ada"
        embed.add_field(name="🚗 Kendaraan", value=mobil_str, inline=False)
        
        properti = [self.PROPERTIES[p]['name'] for p in assets['property'] if p in self.PROPERTIES]
        prop_str = "\n".join(properti) if properti else "Tidak ada"
        embed.add_field(name="🏢 Properti", value=prop_str, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="diler", description="Lihat dan beli kendaraan")
    async def diler(self, interaction: discord.Interaction, beli: str = None):
        if not beli:
            embed = discord.Embed(title="🏎️ Diler Kendaraan", description="Gunakan `/diler <id_kendaraan>` untuk membeli.", color=discord.Color.red())
            for v_id, info in self.VEHICLES.items():
                embed.add_field(name=f"{info['name']} (`{v_id}`)", value=f"Harga: **{info['price']:,} Koin**", inline=False)
            await interaction.response.send_message(embed=embed)
            return

        if beli not in self.VEHICLES:
            await interaction.response.send_message("Kendaraan tidak ditemukan di diler!", ephemeral=True)
            return
            
        user_id = interaction.user.id
        info = self.VEHICLES[beli]
        
        data = await self.get_user_data(user_id)
        if data['balance'] < info['price']:
            await interaction.response.send_message(f"Uang Anda tidak cukup! Butuh {info['price']:,} Koin.", ephemeral=True)
            return
            
        # Cek sudah punya belum
        assets = await self.get_assets(user_id)
        if beli in assets['vehicle']:
            await interaction.response.send_message("Anda sudah memiliki kendaraan ini!", ephemeral=True)
            return
            
        await self.update_user_stat(user_id, 'balance', -info['price'])
        await self.add_asset(user_id, 'vehicle', beli)
        await interaction.response.send_message(f"🚙 Selamat! Anda baru saja membawa pulang **{info['name']}**!")

    @app_commands.command(name="properti", description="Lihat dan beli rumah/properti")
    async def properti(self, interaction: discord.Interaction, beli: str = None):
        if not beli:
            embed = discord.Embed(title="🏢 Properti Real Estate", description="Gunakan `/properti <id>` untuk membeli. Punya properti membuat `/tidur` jadi GRATIS!", color=discord.Color.red())
            for p_id, info in self.PROPERTIES.items():
                embed.add_field(name=f"{info['name']} (`{p_id}`)", value=f"Harga: **{info['price']:,} Koin**", inline=False)
            await interaction.response.send_message(embed=embed)
            return

        if beli not in self.PROPERTIES:
            await interaction.response.send_message("Properti tidak ditemukan!", ephemeral=True)
            return
            
        user_id = interaction.user.id
        info = self.PROPERTIES[beli]
        
        data = await self.get_user_data(user_id)
        if data['bank'] < info['price']:
            await interaction.response.send_message(f"Pembelian properti harus menggunakan uang dari Bank! Uang Bank Anda kurang. (Butuh {info['price']:,})", ephemeral=True)
            return
            
        assets = await self.get_assets(user_id)
        if beli in assets['property']:
            await interaction.response.send_message("Anda sudah memiliki properti ini!", ephemeral=True)
            return
            
        await self.update_user_stat(user_id, 'bank', -info['price'])
        await self.add_asset(user_id, 'property', beli)
        await interaction.response.send_message(f"🏡 Selamat! Anda resmi menjadi pemilik **{info['name']}**!")

    @app_commands.command(name="bisnis", description="Lihat daftar opsi bisnis")
    async def bisnis(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📊 Bursa Bisnis", description="Gunakan `/beli_bisnis` untuk membeli dan `/ambil_untung` mencairkan hasil.", color=discord.Color.purple())
        for b_id, info in self.BUSINESSES.items():
            embed.add_field(name=f"{info['name']} (`{b_id}`)", value=f"Harga: **{info['price']:,}** (Bank)\nUntung/24j: **+{info['income']:,}**", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="beli_bisnis", description="Beli bisnis menggunakan uang di bank")
    async def beli_bisnis(self, interaction: discord.Interaction, b_id: str):
        if b_id not in self.BUSINESSES:
            await interaction.response.send_message("Bisnis tidak valid!", ephemeral=True)
            return
            
        user_id = interaction.user.id
        info = self.BUSINESSES[b_id]
        
        data = await self.get_user_data(user_id)
        if data['business_id']:
            await interaction.response.send_message("Anda sudah punya bisnis! Tidak bisa memiliki lebih dari 1.", ephemeral=True)
            return
            
        if data['bank'] < info['price']:
            await interaction.response.send_message(f"Uang Bank Anda tidak cukup! Butuh {info['price']:,} Koin.", ephemeral=True)
            return
            
        await self.update_user_stat(user_id, 'bank', -info['price'])
        await self.set_user_stat(user_id, 'business_id', b_id)
        # Tambahan: set waktu beli awal (karena bisa numpang last_daily atau tambah kolom, kita bikin ambil untung manual dengan trick ini)
        current_time = time.time()
        # Untuk simplicitas, set business date ke None (bisa ambil lgsg atau tunggu 24 jam)
        # Tapi ini butuh tabel terpisah buat passive income. Kita gabungkan ke last_daily atau sekadar last_work. 
        # Kita butuh stat `last_business` di user. 
        # Coba update schema atau manfaatkan `last_daily` biar gampang.
        await interaction.response.send_message(f"📈 Selamat! Anda telah memborong saham penuh **{info['name']}**. Pergi `/ambil_untung` setiap hari!")

    @app_commands.command(name="ambil_untung", description="Klaim penghasilan pasif bisnis setiap 24 jam")
    async def ambil_untung(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = await self.get_user_data(user_id)
        
        b_id = data.get('business_id')
        if not b_id or b_id not in self.BUSINESSES:
            await interaction.response.send_message("Anda belum punya bisnis aktif yang terdaftar!", ephemeral=True)
            return
            
        # Gunakan cooldown simpel 24 jam (hacky way menggunakan stat last_daily untuk ngecheck, tapi ini numpuk harian dan bisnis)
        # Daripada numpuk dengan /harian, kita cek dari DB langsung (butuh kolom baru)
        # Tapi karena tadi tidak bikin kolom last_business, saya tambahkan on-the-fly pakai pragma kalau error, atau kita jalankan query langsung dgn error handling.
        current_time = time.time()
        
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("ALTER TABLE users ADD COLUMN last_business REAL DEFAULT 0")
            except:
                pass
            
            async with db.execute("SELECT last_business FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                last_business = row[0] if (row and len(row) > 0 and row[0] is not None) else 0
                
            cooldown = self.BUSINESSES[b_id]['cooldown']
            time_passed = current_time - last_business
            
            if time_passed < cooldown:
                sisa = int(cooldown - time_passed)
                h, r = divmod(sisa, 3600)
                m, s = divmod(r, 60)
                await interaction.response.send_message(f"Pegawai sedang bekerja, tunggu klaim berikutnya dalam **{h} jam {m} menit**. ⏳", ephemeral=True)
                return
                
            income = self.BUSINESSES[b_id]['income']
            # Masuk ke Bank agar stabil
            await db.execute("UPDATE users SET bank = bank + ?, last_business = ? WHERE user_id = ?", (income, current_time, user_id))
            await db.commit()
            
        await interaction.response.send_message(f"💸 Mantap boss! Omset **{self.BUSINESSES[b_id]['name']}** hari ini sebesar **{income:,} Koin** telah masuk ke Bank Anda.")

    @app_commands.command(name="resep", description="Lihat daftar resep masakan yang bisa dibuat")
    async def resep(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🍳 Buku Resep Masakan", description="Gunakan `/masak <id_resep>`. Pastikan Anda punya bahan di tas!", color=discord.Color.orange())
        for r_id, info in self.RECIPES.items():
            reqs = []
            for item_id, qty in info['ingredients'].items():
                item_name = self.ITEMS[item_id]['name'] if item_id in self.ITEMS else item_id
                reqs.append(f"{qty}x {item_name}")
            
            req_str = "\n".join(reqs)
            embed.add_field(name=f"{info['name']} (`{r_id}`)", value=f"**Bahan:**\n{req_str}\nBiaya Masak: **{info['cost']} Koin**", inline=False)
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="masak", description="Memasak item dari bahan yang ada di tas")
    async def masak(self, interaction: discord.Interaction, resep_id: str):
        if resep_id not in self.RECIPES:
            await interaction.response.send_message("Resep tidak ditemukan! Cek `/resep`.", ephemeral=True)
            return
            
        user_id = interaction.user.id
        recipe = self.RECIPES[resep_id]
        
        data = await self.get_user_data(user_id)
        if data['balance'] < recipe['cost']:
            await interaction.response.send_message(f"Uang Anda tidak cukup untuk biaya kompor/masak! (Butuh {recipe['cost']} Koin)", ephemeral=True)
            return
            
        # Cek inventory
        inv = await self.get_inventory(user_id)
        missing = []
        for item_id, qty in recipe['ingredients'].items():
            if inv.get(item_id, 0) < qty:
                item_name = self.ITEMS[item_id]['name'] if item_id in self.ITEMS else item_id
                missing.append(f"{qty}x {item_name}")
                
        if missing:
            miss_str = ", ".join(missing)
            await interaction.response.send_message(f"❌ Bahan Anda kurang! Anda butuh: **{miss_str}**", ephemeral=True)
            return
            
        # Semua aman, proses masak
        await self.update_user_stat(user_id, 'balance', -recipe['cost'])
        
        for item_id, qty in recipe['ingredients'].items():
            await self.remove_item(user_id, item_id, qty)
            
        # Asumsikan ID resep sama dengan ID item hasil jadinya, contoh "nasi_goreng"
        await self.add_item(user_id, resep_id, 1)
        
        await interaction.response.send_message(f"👨‍🍳 Ting... Tong... Tarara! Anda sukses memasak **{recipe['name']}**!")

    @app_commands.command(name="mancing", description="Memancing ikan (Butuh: Alat Pancing & Umpan, Mengurangi: Lapar, Haus)")
    async def mancing(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        inv = await self.get_inventory(user_id)
        if 'pancingan' not in inv:
            await interaction.response.send_message("🎣 Anda tidak punya **Alat Pancing**! Beli dulu di `/toko`.", ephemeral=True)
            return
            
        if 'umpan' not in inv:
            await interaction.response.send_message("🪱 Anda butuh **Umpan Cacing** untuk memancing! Beli di `/toko`.", ephemeral=True)
            return
            
        data = await self.get_user_data(user_id)
        if data['hunger'] <= 15 or data['thirst'] <= 15:
            await interaction.response.send_message("😵 Anda terlalu lelah untuk memancing! Makan/minum dulu.", ephemeral=True)
            return
            
        # Proses mancing
        await self.remove_item(user_id, 'umpan', 1)
        await self.update_user_stat(user_id, 'hunger', -10)
        await self.update_user_stat(user_id, 'thirst', -10)
        await self.update_user_stat(user_id, 'stress', -5) # mancing ngurangin stress dikit
        
        # RNG hasil
        if random.random() < 0.6: # 60% peluang dapat
            dapat = random.randint(1, 3)
            await self.add_item(user_id, 'ikan_lele', dapat)
            await interaction.response.send_message(f"🎣 JLEB! Anda berhasil memancing dan mendapatkan **{dapat}x Ikan Lele Segar** 🐟!")
        else:
            await interaction.response.send_message("🎣 Yaaah... umpannya dimakan ikan tapi ikannya kabur. Coba lagi!")

    @app_commands.command(name="berburu", description="Berburu hewan peliharaan (Butuh: Senapan Angin, Mengurangi: Lapar, Haus)")
    async def berburu(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        inv = await self.get_inventory(user_id)
        if 'senapan' not in inv:
            await interaction.response.send_message("🔫 Anda tidak punya **Senapan Angin**! Beli dulu di `/toko`.", ephemeral=True)
            return
            
        data = await self.get_user_data(user_id)
        if data['hunger'] <= 20 or data['thirst'] <= 20:
            await interaction.response.send_message("😵 Anda butuh banyak energi untuk berburu! Makan/minum dulu.", ephemeral=True)
            return
            
        # Proses berburu
        await self.update_user_stat(user_id, 'hunger', -20)
        await self.update_user_stat(user_id, 'thirst', -20)
        
        # RNG hasil
        if random.random() < 0.5: # 50% peluang dapat
            dapat = random.randint(1, 2)
            await self.add_item(user_id, 'daging_rusa', dapat)
            await interaction.response.send_message(f"🔫 DOR! Tembakan tepat sasaran. Anda mendapatkan **{dapat}x Daging Rusa Mentah** 🥩!")
        else:
            await interaction.response.send_message("🔫 Dor... dor... Hewannya keburu kabur. Anda gagal berburu kali ini.")

    @app_commands.command(name="slot", description="Judi mesin slot (Bayar Taruhan dari uang Tunai)")
    async def slot(self, interaction: discord.Interaction, taruhan: int):
        if taruhan <= 0:
            await interaction.response.send_message("Taruhan harus lebih dari 0!", ephemeral=True)
            return
            
        user_id = interaction.user.id
        data = await self.get_user_data(user_id)
        
        if data['balance'] < taruhan:
            await interaction.response.send_message(f"Uang tunai Anda tidak cukup! (Tunai: {data['balance']:,} Koin)", ephemeral=True)
            return
            
        # Potong uang 
        await self.update_user_stat(user_id, 'balance', -taruhan)
        
        simbol = ["🍒", "🍇", "🍊", "🍋", "🔔", "💎", "7️⃣"]
        hasil = [random.choice(simbol) for _ in range(3)]
        
        embed = discord.Embed(title="🎰 Mesin Slot 🎰", color=discord.Color.gold())
        embed.description = f"**{hasil[0]} | {hasil[1]} | {hasil[2]}**\n\n"
        
        if hasil[0] == hasil[1] == hasil[2]:
            menang = taruhan * 10
            embed.description += f"🎉 **JACKPOT!** Tiga gambar sama! Anda menang **{menang:,} Koin**!"
            embed.color = discord.Color.green()
            await self.update_user_stat(user_id, 'balance', menang)
        elif hasil[0] == hasil[1] or hasil[1] == hasil[2] or hasil[0] == hasil[2]:
            menang = int(taruhan * 1.5)
            embed.description += f"👍 Dua gambar sama! Anda memenangkan **{menang:,} Koin**."
            await self.update_user_stat(user_id, 'balance', menang)
        else:
            embed.description += "💥 Kering! Anda kalah taruhan."
            embed.color = discord.Color.red()
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rampok_bank", description="Nekat merampok bank (Resiko Besar)")
    async def rampok_bank(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        
        data = await self.get_user_data(user_id)
        
        # Syarat minimal punya senapan biar logis
        inv = await self.get_inventory(user_id)
        if 'senapan' not in inv:
            await interaction.response.send_message("🔫 Buat merampok bank setidaknya Anda harus punya **Senapan Angin**!", ephemeral=True)
            return

        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("ALTER TABLE users ADD COLUMN last_rob REAL DEFAULT 0")
            except:
                pass
            
            async with db.execute("SELECT last_rob FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                last_rob = row[0] if row else 0
                
            cooldown = 86400  # 1 Hari
            time_passed = current_time - last_rob
            
            if time_passed < cooldown:
                remaining_time = int(cooldown - time_passed)
                h, r = divmod(remaining_time, 3600)
                m, s = divmod(r, 60)
                await interaction.response.send_message(f"Polisi masih berjaga ketat! Tunggu **{h} jam {m} menit** lagi. 👮‍♂️", ephemeral=True)
                return
                
            await db.execute("UPDATE users SET last_rob = ? WHERE user_id = ?", (current_time, user_id))
            await db.commit()
            
        # Peluang berhasil 30%
        if random.random() < 0.30:
            dapat = random.randint(50000, 250000)
            await self.update_user_stat(user_id, 'balance', dapat)
            await interaction.response.send_message(f"🥷 **BERHASIL!** Anda membobol brankas dan membawa kabur uang **{dapat:,} Koin**!")
        else:
            # Denda besar
            denda = random.randint(10000, 50000)
            if data['balance'] < denda:
                denda = data['balance'] # Ambil semua tuang tunai
                
            await self.update_user_stat(user_id, 'balance', -denda)
            await interaction.response.send_message(f"🚨 **TERTANGKAP!** Polisi menyergap Anda. Uang tunai Anda disita sebesar **{denda:,} Koin** sebagai denda pengadilan!")

    @app_commands.command(name="curi", description="Mencuri uang dari orang lain")
    async def curi(self, interaction: discord.Interaction, target: discord.Member):
        if target.bot or target.id == interaction.user.id:
            await interaction.response.send_message("Target tidak valid!", ephemeral=True)
            return
            
        user_id = interaction.user.id
        current_time = time.time()
        
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("ALTER TABLE users ADD COLUMN last_steal REAL DEFAULT 0")
            except:
                pass
            
            async with db.execute("SELECT last_steal FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                last_steal = row[0] if (row and len(row) > 0 and row[0] is not None) else 0
                
            cooldown = 3600 # 1 jam
            time_passed = current_time - last_steal
            
            if time_passed < cooldown:
                m, s = divmod(int(cooldown - time_passed), 60)
                await interaction.response.send_message(f"Masih capek mencopet! Tunggu **{m} menit {s} detik** lagi. 🏃‍♂️", ephemeral=True)
                return
                
            await db.execute("UPDATE users SET last_steal = ? WHERE user_id = ?", (current_time, user_id))
            await db.commit()
            
        target_data = await self.get_user_data(target.id)
        if target_data['balance'] < 100:
            await interaction.response.send_message(f"{target.display_name} terlalu miskin, tidak ada yang bisa dicuri (Tunai < 100 Koin).", ephemeral=True)
            return
            
        max_curi = min(target_data['balance'], 5000)
        
        if random.random() < 0.40: # 40% sukses
            dapat = random.randint(50, max_curi)
            await self.update_user_stat(target.id, 'balance', -dapat)
            await self.update_user_stat(user_id, 'balance', dapat)
            await interaction.response.send_message(f"🤫 Sssst... Anda berhasil menyusup dan mencuri **{dapat:,} Koin** tunai dari dompet {target.mention}!")
        else:
            denda = random.randint(50, 500)
            await self.update_user_stat(user_id, 'balance', -denda)
            await self.update_user_stat(target.id, 'balance', denda)
            await interaction.response.send_message(f"😠 Ketahuan! Anda digebukin oleh warga saat mencoba mencuri dari {target.mention} dan harus ganti rugi **{denda:,} Koin** kepadanya!")

    @app_commands.command(name="saham", description="Investasi saham kripto (Untung/Rugi acak)")
    async def saham(self, interaction: discord.Interaction, modal: int):
        if modal < 1000:
            await interaction.response.send_message("Minimal modal saham adalah 1000 Koin!", ephemeral=True)
            return
            
        user_id = interaction.user.id
        data = await self.get_user_data(user_id)
        
        if data['bank'] < modal:
            await interaction.response.send_message(f"Uang Bank Anda tidak cukup! Transaksi saham hanya via Bank. (Saldo: {data['bank']:,} Koin)", ephemeral=True)
            return
            
        # Potong langsung di bank
        await self.update_user_stat(user_id, 'bank', -modal)
        
        embed = discord.Embed(title="📈 Trading Saham", color=discord.Color.blue())
        embed.description = f"Anda mengeksekusi *Buy* saham DISCO dengan uang modal **{modal:,} Koin**...\n\n"
        
        # RNG Saham
        multiplier = random.uniform(0.1, 2.5) # Dari rugi 90% sampai untung 150%
        hasil = int(modal * multiplier)
        
        if multiplier >= 1.0:
            embed.description += f"🤑 Saham MEROKET! Anda balik modal dan untung, menerima kembali **{hasil:,} Koin** ({(multiplier-1)*100:.1f}%)"
            embed.color = discord.Color.green()
        else:
            embed.description += f"😭 Saham ANJLOK! Anda rugi besar, hanya mendapat kembali **{hasil:,} Koin** ({(1-multiplier)*100:.1f}%)"
            embed.color = discord.Color.red()
            
        await self.update_user_stat(user_id, 'bank', hasil)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
