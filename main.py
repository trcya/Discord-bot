import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load variables dari file .env
load_dotenv()

# Setup bot intents
intents = discord.Intents.default()
intents.message_content = True  # Untuk membaca isi pesan
intents.members = True          # Untuk info member (join date, roles, dll)

# Inisialisasi Bot dengan prefix "!" (sebagai fallback, kita akan fokus ke slash commands)
bot = commands.Bot(command_prefix='!', intents=intents)

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Login berhasil sebagai {bot.user} (ID: {bot.user.id})')
    print('------')
    
    # Ganti activity bot
    await bot.change_presence(activity=discord.Game(name="Membantu Server | /help"))
    
    # Sync slash commands saat bot siap
    try:
        # Peringatan: Global sync bisa memakan waktu hingga 1 jam di Discord
        synced = await bot.tree.sync()
        print(f"Berhasil sinkronisasi {len(synced)} slash command(s) secara global.")
        
        # OTO-SYNC KE SERVER PERTAMA: Memaksa Discord mendaftarkan command ke server langsung
        if bot.guilds:
            first_guild = bot.guilds[0]
            bot.tree.copy_global_to(guild=first_guild)
            synced_local = await bot.tree.sync(guild=first_guild)
            print(f"MAMAKSA SYNC {len(synced_local)} command langsung ke server '{first_guild.name}' (Mencegah delay).")
            
    except Exception as e:
        print(f"Gagal sinkronisasi command: {e}")

@bot.command()
@commands.is_owner() # Atau setidaknya dengan perm admin. Untuk sekarang buka saja agar mudah ditest.
async def sync(ctx):
    """Command rahasi untuk nge-sync slash commands secara instan ke server ini"""
    try:
        # Syncing directly to the guild is instant
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ Berhasil sinkronisasi {len(synced)} slash command ke server ini secara instan!")
    except Exception as e:
        await ctx.send(f"Gagal: {e}")

# Load semua extension (cogs) dari folder cogs
async def load_cogs():
    if not os.path.exists('./cogs'):
        os.makedirs('./cogs')
        print("Folder 'cogs' dibuat.")
        
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Berhasil memuat cog: {filename}')

@bot.event
async def setup_hook():
    await load_cogs()

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    
    if token and token != "your_token_here":
        bot.run(token)
    else:
        print("PERINGATAN: Token tidak valid! Silakan masukkan token bot Anda ke file .env (DISCORD_TOKEN=token_anda)")
