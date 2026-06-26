import os
import subprocess

# Paths
python_path = r"C:\Users\raffaele.beffa\Documents\python\1_so_list\venv\Scripts\python.exe"
script_path = r"C:\Users\raffaele.beffa\Documents\python\1_so_list\SO_list.py"
vbs_path = "launcher.vbs"

# Create VBS content
vbs_content = f'''
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "{python_path} {script_path}", 0, False
'''

# Write VBS file
with open(vbs_path, "w", encoding="utf-8") as f:
    f.write(vbs_content)

print("launch_main_widget.vbs created.")

# Optional: automatically run it
subprocess.Popen(["wscript.exe", vbs_path])
