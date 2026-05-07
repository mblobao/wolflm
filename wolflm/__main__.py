from pathlib import Path
import os

index = 'index.py'

os.system(f'cd "{Path(__file__).parent}" && streamlit run "{Path(__file__).parent / index}"')

# hide = win32gui.GetForegroundWindow()
# win32gui.ShowWindow(hide, win32con.SW_HIDE)
