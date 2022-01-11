import os

""" 
Run this to compile a portable .exe of the Mould Monitor
"""

current_ver = 1
for c in os.listdir('dist'):  # hunt for the most recent version number
    if c[-6] == 'v':
        latest_ver = float(c[-5])
        if latest_ver >= current_ver:
            current_ver = latest_ver + 1

exeFname = f"mouldMonitor_v{int(current_ver)}"
os.system(f'/venv/Scripts/activate & '
          f'pyinstaller '
          f'--splash "../FACT_LOGO.png" '
          f'--onefile '
          f'--specpath "mould logs" '
          f'-n {exeFname} '
          f'main.py')
