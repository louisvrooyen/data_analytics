# dashboard.py
import subprocess
import os

base_dir = r"D:\Python\data_imports_project\main_data"

scripts = [
    os.path.join(base_dir, "add_Streets_Data.py"),
    os.path.join(base_dir, "generate_errors.py")
]

for script in scripts:
    print(f"Running {script}...")
    subprocess.run(["python", script], check=True)

print("All scripts executed successfully.")