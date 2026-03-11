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

    @app_commands.command(name="botinfo", description="Lihat informasi tentang bot ini")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Bot Info", description="Bot Discord Serbaguna dengan Fitur Game", color=discord.Color.blue())
        embed.add_field(name="Developer", value="David Adesta", inline=False)
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Total Server", value=str(len(self.bot.guilds)), inline=True)
        if self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
