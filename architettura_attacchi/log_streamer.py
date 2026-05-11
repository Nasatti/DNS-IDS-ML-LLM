import os
import time

def read_zeek_log(file_path):
    if not os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        open(file_path, 'a').close()
        print(f"📁 File {file_path} non trovato. Creato nuovo file vuoto.")
    
    with open(file_path, "r") as f:
        f.seek(0, 2)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            if line.startswith("#"):
                continue
            
            yield line