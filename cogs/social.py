import discord
from discord.ext import commands
from discord import app_commands
import random

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def interaction_embed(self, interaction, target, action, emoji, self_msg, target_msg):
        if target == interaction.user:
            await interaction.response.send_message(self_msg, ephemeral=True)
            return

        embed = discord.Embed(
            description=target_msg.format(user=interaction.user.mention, target=target.mention),
            color=discord.Color.random()
        )
        await interaction.response.send_message(content=target.mention, embed=embed)

    aksi_group = app_commands.Group(name="aksi", description="Kumpulan aksi & ekspresi / Actions & expressions")

    @aksi_group.command(name="peluk", description="Berikan pelukan hangat ke seseorang")
    async def peluk(self, interaction: discord.Interaction, target: discord.Member):
        await self.interaction_embed(interaction, target, "memeluk", "🫂", 
            "Anda memeluk diri sendiri... Kesepian ya? 🥺", 
            "💖 {user} memberikan pelukan hangat kepada {target}!")

    @aksi_group.command(name="cium", description="Berikan kecupan kasih sayang")
    async def cium(self, interaction: discord.Interaction, target: discord.Member):
        await self.interaction_embed(interaction, target, "mencium", "💋", 
            "Mencium cermin? Bergaya sekali! ✨", 
            "💋 {user} memberikan kecupan manis kepada {target}!")

    @aksi_group.command(name="tampar", description="Tampar seseorang (Canda ya!)")
    async def tampar(self, interaction: discord.Interaction, target: discord.Member):
        await self.interaction_embed(interaction, target, "menampar", "🖐️", 
            "Plak! Anda menampar pipi sendiri. Sadar woi! 😵‍💫", 
            "🖐️ {user} menampar {target}! Waduh, ada masalah apa nih?")

    @aksi_group.command(name="elus", description="Elus kepala seseorang")
    async def elus(self, interaction: discord.Interaction, target: discord.Member):
        await self.interaction_embed(interaction, target, "mengelus", "👋", 
            "Mengelus kepala sendiri... Pintar! 🐶", 
            "👋 {user} mengelus kepala {target}. Anak baik~")

    @aksi_group.command(name="colek", description="Colek seseorang biar diperhatikan")
    async def colek(self, interaction: discord.Interaction, target: discord.Member):
        await self.interaction_embed(interaction, target, "mencolek", "👉", 
            "Jangan colek diri sendiri di depan umum! 😳", 
            "👉 {user} mencolek {target}. Pstt, lirik sini dong!")

    @aksi_group.command(name="joget", description="Ekspresikan kegembiraan dengan joget")
    async def joget(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"💃 **{interaction.user.display_name}** sedang asyik berjoget ria! *De-cet-det-det...* 🎶")

    @aksi_group.command(name="nangis", description="Tunjukkan kalau kamu sedih")
    async def nangis(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"😭 **{interaction.user.display_name}** sedang menangis tersedu-sedu... Sini peluk. 🥺")

    @aksi_group.command(name="ketawa", description="Tertawa terbahak-bahak")
    async def ketawa(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🤣 **{interaction.user.display_name}** tertawa sampai sakit perut! WKWKWK!")

    @aksi_group.command(name="senyum", description="Berikan senyuman termanismu")
    async def senyum(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"😊 **{interaction.user.display_name}** tersenyum manis... Hatiku meleleh! ❤️")

    @aksi_group.command(name="marah", description="Tunjukkan kalau kamu sedang marah")
    async def marah(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"💢 **{interaction.user.display_name}** sedang marah besar! Awas kena semprot! 😤")

    @app_commands.command(name="avatar", description="Lihat profil lengkap, avatar, ID, dan info dompet seseorang")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        
        # Ambil data ekonomi
        eco_cog = self.bot.get_cog('Economy')
        if eco_cog:
            data = await eco_cog.get_user_data(member.id)
            uang_tunai = f"{data['balance']:,}"
            uang_bank = f"{data['bank']:,}"
        else:
            uang_tunai = "?"
            uang_bank = "?"

        # Join date
        join_date = member.joined_at.strftime("%d %b %Y, %H:%M") if member.joined_at else "Tidak diketahui"
        
        embed = discord.Embed(title=f"👤 Profil & Avatar: {member.display_name}", color=member.color or discord.Color.blue())
        
        embed.add_field(name="🆔 Discord ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="💰 Uang Tunai", value=f"{uang_tunai} Koin", inline=True)
        embed.add_field(name="🏦 Uang Bank", value=f"{uang_bank} Koin", inline=True)
        embed.add_field(name="📅 Join Server", value=join_date, inline=False)
        
        # Profile Discord (Global) vs Profile Server (Guild)
        avatar_global = member.avatar.url if member.avatar else member.default_avatar.url
        avatar_server = member.guild_avatar.url if member.guild_avatar else "Sama dengan Global"
        
        desc = f"**🔗 Link Avatar:**\n[Avatar Global]({avatar_global})"
        if member.guild_avatar:
            desc += f" | [Avatar Server]({avatar_server})"
            
        embed.description = desc
        
        # Set images
        if member.guild_avatar:
            embed.set_image(url=member.guild_avatar.url)
            embed.set_thumbnail(url=avatar_global)
            embed.set_footer(text="Gambar besar: Avatar Server | Thumbnail: Avatar Global")
        else:
            embed.set_image(url=avatar_global)
            embed.set_footer(text="User ini menggunakan Avatar Global untuk Server ini")
            
        await interaction.response.send_message(embed=embed)

    sosial_group = app_commands.Group(name="sosial", description="Interaksi sosial & Info / Social interactions & info")

    @sosial_group.command(name="serverinfo", description="Lihat statistik server ini")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"🏰 Info Server: {guild.name}", color=discord.Color.green())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Tidak diketahui", inline=True)
        embed.add_field(name="ID Server", value=guild.id, inline=True)
        embed.add_field(name="Dibuat Pada", value=guild.created_at.strftime("%d %b %Y"), inline=True)
        embed.add_field(name="Total Member", value=guild.member_count, inline=True)
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        embed.add_field(name="Total Role", value=len(guild.roles), inline=True)
        await interaction.response.send_message(embed=embed)

    @sosial_group.command(name="lelucon", description="Dengarkan lelucon garing dari bot")
    async def lelucon(self, interaction: discord.Interaction):
        jokes = [
            "Kenapa ayam kalau berkokok matanya merem? Soalnya sudah hafal teksnya.",
            "Sayur apa yang jago nyanyi? Kol-play.",
            "Ikan apa yang berhenti? Ikan pause.",
            "Penyanyi luar negeri yang suka bersepeda? Selena Gowes.",
            "Kenapa matahari tenggelam? Karena gak bisa berenang.",
            "Gajah apa yang paling baik hati? Gajah jahat (Gak jahat)."
        ]
        await interaction.response.send_message(f"😂 **Lelucon Hari Ini:**\n\n*{random.choice(jokes)}*")

    @sosial_group.command(name="kutipan", description="Kata-kata bijak untuk motivasimu")
    async def kutipan(self, interaction: discord.Interaction):
        quotes = [
            "'Pekerjaan besar tidak dilakukan dengan kekuatan, melainkan dengan ketekunan.'",
            "'Jangan pernah menyerah pada hal yang benar-benar kamu inginkan.'",
            "'Keberhasilan adalah kemampuan untuk berpindah dari kegagalan ke kegagalan tanpa kehilangan antusiasme.'",
            "'Hari ini adalah kesempatan untuk membangun hari esok yang Anda inginkan.'",
            "'Jadilah perubahan yang ingin kamu lihat di dunia ini.'"
        ]
        await interaction.response.send_message(f"📖 **Kutipan Bijak:**\n\n*{random.choice(quotes)}*")

    @sosial_group.command(name="berantem", description="Ajak seseorang beradu argumen (Canda)")
    async def berantem(self, interaction: discord.Interaction, target: discord.Member):
        outcomes = [
            "{user} menang telak! {target} lari terbirit-birit. 🏃‍♂️💨",
            "{target} membalas dengan argumen maut, {user} terdiam. 😶",
            "Keduanya capek berantem, akhirnya malah jajan bareng. 🍟",
            "{user} terpeleset saat mau marah, {target} tertawa. 😂"
        ]
        await interaction.response.send_message(random.choice(outcomes).format(user=interaction.user.mention, target=target.mention))

    @sosial_group.command(name="puji", description="Puji seseorang biar dia senang")
    async def puji(self, interaction: discord.Interaction, target: discord.Member):
        pujian = [
            "Wah {target}, kamu hari ini terlihat sangat bersinar! ✨",
            "{target} memang member terbaik di server ini. No debat! 🏆",
            "Suatu kehormatan bisa mengenal orang seperti {target}. 💖",
            "Senyuman {target} bisa mengalahkan cahaya matahari. ☀️"
        ]
        await interaction.response.send_message(random.choice(pujian).format(target=target.mention))

    @sosial_group.command(name="ejek", description="Ejek teman dengan candaan ringan")
    async def ejek(self, interaction: discord.Interaction, target: discord.Member):
        ejekan = [
            "{target} kok bau bawang sih? Mandi sana! 🧅🚿",
            "Muka {target} kayak karakter NPC yang belum di-render. 👾",
            "{target} kalau jalan kayak pinguin keberatan beban hidup. 🐧",
            "IQ {target} kayaknya setara dengan suhu ruangan ber-AC. ❄️"
        ]
        await interaction.response.send_message(random.choice(ejekan).format(target=target.mention))

    @sosial_group.command(name="tanya_kabar", description="Tanyakan kabar seseorang")
    async def tanya_kabar(self, interaction: discord.Interaction, target: discord.Member):
        await interaction.response.send_message(f"👋 Halo {target.mention}, apa kabar hari ini? {interaction.user.mention} nanyain nih! 😊")

    @sosial_group.command(name="pamer", description="Pamer sesuatu yang keren (atau nggak)")
    async def pamer(self, interaction: discord.Interaction, hal: str):
        await interaction.response.send_message(f"😎 **LIHAT INI SEMUA!**\n\n**{interaction.user.display_name}** sedang pamer tentang: **{hal}**! Gimana? Iri nggak? 😂")

    @sosial_group.command(name="sembunyi", description="Coba sembunyi dari teman-teman")
    async def sembunyi(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🧩 **{interaction.user.display_name}** sedang sembunyi di bawah meja... Sstt, jangan bilang siapa-siapa! 🤫")

    @sosial_group.command(name="cari", description="Cari orang yang lagi sembunyi")
    async def cari(self, interaction: discord.Interaction, target: discord.Member):
        await interaction.response.send_message(f"🔍 **{interaction.user.display_name}** sedang mencari {target.mention}! Ketemu nggak ya?")

    @sosial_group.command(name="bisik", description="Bisikkan sesuatu ke seseorang (Hanya kalian berdua yang tahu?)")
    async def bisik(self, interaction: discord.Interaction, target: discord.Member, pesan: str):
        await interaction.response.send_message(f"🤫 **{interaction.user.display_name}** membisikkan sesuatu ke telinga {target.mention}...", ephemeral=False)
        try:
            await target.send(f"🤫 **Bisikan dari {interaction.user.display_name}:** {pesan}")
        except:
            pass

    @sosial_group.command(name="teriak", description="Terjemahkan emosimu dengan berteriak")
    async def teriak(self, interaction: discord.Interaction, pesan: str):
        await interaction.response.send_message(f"📢 **{interaction.user.display_name} BERTERIAK:** {pesan.upper()}!!!")

    @aksi_group.command(name="pingsan", description="Pura-pura pingsan karena kaget atau lelah")
    async def pingsan(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"😵 **{interaction.user.display_name}** tiba-tiba pingsan! Kasih napas buatan gais! 🚑")

async def setup(bot):
    await bot.add_cog(Social(bot))
