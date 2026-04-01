import re
import os

files = ['translations.py', 'cogs/economy.py', 'cogs/games.py', 'cogs/info.py']

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Menambahkan emoji koin jika belum ada
    content = re.sub(r'(?<!🪙)\s+Koin\b', ' 🪙 Koin', content)
    content = re.sub(r'(?<!🪙)\s+Coins\b', ' 🪙 Coins', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('DONE')
