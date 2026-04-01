import os

history_dir = r"C:\Users\David Adesta\AppData\Roaming\Code\User\History"

print('Mencari backup...')
found_eco = []
found_games = []
found_info = []
found_trans = []

if not os.path.exists(history_dir):
    print("History directory doesn't exist.")
else:
    for folder in os.listdir(history_dir):
        folder_path = os.path.join(history_dir, folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if "class Economy(commands.Cog):" in content:
                                found_eco.append((os.path.getmtime(file_path), file_path))
                            if "class Games(commands.Cog):" in content or "class Permainan(commands.Cog):" in content or "name=\"slots\"" in content:
                                found_games.append((os.path.getmtime(file_path), file_path))
                            if "class Info(commands.Cog):" in content or "name=\"help\"" in content:
                                found_info.append((os.path.getmtime(file_path), file_path))
                            if "TRANSLATIONS = {" in content:
                                found_trans.append((os.path.getmtime(file_path), file_path))
                    except Exception:
                        pass

def report(name, lst):
    if lst:
        lst.sort(reverse=True)
        print(f"{name} BACKUP DITEMUKAN: {lst[0][1]}")
    else:
        print(f"{name} GAGAL DITEMUKAN")

report('economy.py', found_eco)
report('games.py', found_games)
report('info.py', found_info)
report('translations.py', found_trans)
