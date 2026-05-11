import json
import time
import os
from pymongo import MongoClient

# --- CONFIGURAZIONE DESTINAZIONE ---
# "test_reale", "attack_tunneling", "attack_dga", "attack_ddos"
TARGET_COLLECTION = "test_reale" 
MONGO_URI = "mongodb://127.0.0.1:27017/"
DB_NAME = "tesi_dns"
LOG_FILE_PATH = "logs/dns.log"
KALI_IP = "192.168.1.61"

def tail_f(file_path):
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        open(file_path, 'a').close()
    with open(file_path, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

def run_ingestor():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[TARGET_COLLECTION]

    try:
        client.admin.command('ping')
        print("✅ Connessione a MongoDB stabilita con successo!")
    except Exception as e:
        print(f"❌ Errore critico di connessione: {e}")
        return
    
    print(f"Ingestor avviato. Monitorando: {LOG_FILE_PATH}")
    for riga_log in tail_f(LOG_FILE_PATH):
        try:
            dato_json = json.loads(riga_log)

            if dato_json.get("id.orig_h") != KALI_IP:
                continue

            collection.insert_one(dato_json)
            print(f"[{TARGET_COLLECTION}] Inserito: {dato_json.get('query', 'N/A')}")
        except Exception as e:
            print(f"Errore: {e}")

if __name__ == "__main__":
    run_ingestor()