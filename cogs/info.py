import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Cek latency bot")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency bot: `{latency}ms`",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Lihat informasi tentang pengguna")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        
        # Format dates
        created_at = member.created_at.strftime("%d %b %Y, %H:%M")
        joined_at = member.joined_at.strftime("%d %b %Y, %H:%M") if member.joined_at else "Tidak diketahui"
        
        # Roles (excluding @everyone)
        roles = [role.mention for role in member.roles[1:]]
        roles_str = " ".join(roles) if roles else "Tidak ada role khusus"
        
        embed = discord.Embed(title=f"User Info - {member.name}", color=member.color)
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
            
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.display_name, inline=True)
        embed.add_field(name="Akun Dibuat", value=created_at, inline=False)
        embed.add_field(name="Bergabung di Server", value=joined_at, inline=False)
        embed.add_field(name=f"Roles ({len(member.roles)-1})", value=roles_str, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Menampilkan daftar semua perintah yang tersedia")
    async def help_command(self, interaction: discord.Interaction):
        # Build embed for help menu
        embed = discord.Embed(
            title="📚 Bantuan Perintah Bot",
            description="Berikut adalah daftar perintah yang bisa Anda gunakan:",
            color=discord.Color.blurple()
        )
        
        if self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
        # Group commands by Cog
        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_app_commands()
            if not commands_list:
                continue
                
            cmd_strings = []
            for cmd in commands_list:
                desc = cmd.description or "Tidak ada deskripsi"
                cmd_strings.append(f"`/{cmd.name}` - {desc}")
                
            if cmd_strings:
                embed.add_field(
                    name=f"🔸 {cog_name} Commands",
                    value="\n".join(cmd_strings),
                    inline=False
                )
                
        embed.set_footer(text="Gunakan / di chat untuk melihat daftar lengkap perintah dari Discord.")
        
        # Kirim pesan secara ephemeral (hanya bisa dilihat oleh user yang memanggil command)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Info(bot))
