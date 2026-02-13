import shutil
import os

src = 'bfsi_alpaca_1_to_160_final_clean.json'
dst = 'data/bfsi_dataset.json'

print(f"Current working directory: {os.getcwd()}")
print(f"Source exists: {os.path.exists(src)}")
print(f"Destination directory exists: {os.path.exists('data')}")

try:
    shutil.copy2(src, dst)
    print(f"Successfully copied {src} to {dst}")
except Exception as e:
    print(f"Error copying file: {e}")
