import customtkinter
import os
import PyInstaller.__main__

# Get customtkinter path for data inclusion
customtkinter_path = os.path.dirname(customtkinter.__file__)

print("Building executable... This may take a few minutes.")

PyInstaller.__main__.run([
    'SDAW_Modern.py',
    '--name=SDAW_Assistant',
    '--onefile',
    '--noconsole',
    f'--add-data={customtkinter_path};customtkinter/',
    '--add-data=AI Interface.gif;.',
    '--add-data=Mic.png;.', 
    '--add-data=Keyboard.png;.',
    '--hidden-import=PIL._tkinter_finder',
    '--clean',
])

print("Build complete! Check the 'dist' folder for SDAW_Assistant.exe")
