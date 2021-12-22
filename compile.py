import os
import datetime as dt
current_ver = 1
for c in os.listdir('dist'):
    if c[-6] == 'v':
        latest_ver = float(c[-5])
        if latest_ver >= current_ver:
            current_ver = latest_ver + 1

exeFname = f"mouldMonitor_v{int(current_ver)}"
os.system(f'/venv/Scripts/activate & pyinstaller --onefile --specpath "mould logs" --add-data "FACT_LOGO.png;." -n {exeFname} main.py')
