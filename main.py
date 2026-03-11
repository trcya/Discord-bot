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

@bot.event
async def on_ready():
    print(f'Login berhasil sebagai {bot.user} (ID: {bot.user.id})')
    print('------')
    
    # Ganti activity bot
    await bot.change_presence(activity=discord.Game(name="Membantu Server | /help"))
    
    # Sync slash commands saat bot siap
    try:
        synced = await bot.tree.sync()
        print(f"Berhasil sinkronisasi {len(synced)} slash command(s) secara global.")
    except Exception as e:
        print(f"Gagal sinkronisasi command: {e}")

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
