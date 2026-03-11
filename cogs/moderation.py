import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Menghapus sejumlah pesan di chat (Admin/Mod)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int = 5):
        if amount > 100:
            await interaction.response.send_message("Maksimal menghapus 100 pesan sekaligus!", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True) # Defer because purge can take time
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Brumm! 🧹 Berhasil menghapus {len(deleted)} pesan.", ephemeral=True)

    @app_commands.command(name="kick", description="Mengeluarkan member dari server (Admin/Mod)")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if member == interaction.user:
            await interaction.response.send_message("Anda tidak bisa kick diri sendiri!", ephemeral=True)
            return
            
        reason = reason or "Tidak ada alasan yang diberikan."
        
        try:
            await member.send(f"Anda telah di-kick dari server **{interaction.guild.name}**.\nAlasan: {reason}")
        except discord.Forbidden:
            pass # User might have DMs disabled
            
        await member.kick(reason=reason)
        
        embed = discord.Embed(title="Member Di-Kick 👢", color=discord.Color.orange())
        embed.add_field(name="Member", value=member.mention, inline=True)
        embed.add_field(name="Oleh", value=interaction.user.mention, inline=True)
        embed.add_field(name="Alasan", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Mem-banned member dari server (Admin)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if member == interaction.user:
            await interaction.response.send_message("Anda tidak bisa ban diri sendiri!", ephemeral=True)
            return
            
        reason = reason or "Tidak ada alasan yang diberikan."
        
        try:
            await member.send(f"Anda telah di-ban dari server **{interaction.guild.name}**.\nAlasan: {reason}")
        except discord.Forbidden:
            pass
            
        await member.ban(reason=reason)
        
        embed = discord.Embed(title="Member Di-Ban 🔨", color=discord.Color.red())
        embed.add_field(name="Member", value=member.mention, inline=True)
        embed.add_field(name="Oleh", value=interaction.user.mention, inline=True)
        embed.add_field(name="Alasan", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="timeout", description="Memberikan timeout (mute) sementara ke member (Mod)")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = None):
        if member == interaction.user:
            await interaction.response.send_message("Anda tidak bisa mute diri sendiri!", ephemeral=True)
            return
            
        reason = reason or "Tidak ada alasan yang diberikan."
        duration = datetime.timedelta(minutes=minutes)
        
        try:
            await member.timeout(duration, reason=reason)
            embed = discord.Embed(title="Member Di-Timeout 🔇", color=discord.Color.dark_gray())
            embed.add_field(name="Member", value=member.mention, inline=True)
            embed.add_field(name="Durasi", value=f"{minutes} menit", inline=True)
            embed.add_field(name="Oleh", value=interaction.user.mention, inline=False)
            embed.add_field(name="Alasan", value=reason, inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Gagal melakukan timeout: {e}", ephemeral=True)

    # Slash command error handling
    def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            return interaction.response.send_message("❌ Anda tidak memiliki izin untuk menggunakan perintah ini!", ephemeral=True)
        return interaction.response.send_message(f"Terjadi kesalahan: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
