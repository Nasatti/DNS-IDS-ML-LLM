import os
import json
import time
from pymongo import MongoClient
from dns_math import shannon_entropy, get_string_metrics

# --- CONFIGURAZIONE ---
MONGO_URI = "mongodb://127.0.0.1:27017/"
DB_NAME = "tesi_dns"
SOURCE_COLLECTION = "test_reale"
OUTPUT_DIR = "output_json"
OUTPUT_FILE = f"{OUTPUT_DIR}/analyze_data.json"

# ATTACK_TYPE: 0-Test, 1-Tunneling, 2-DGA, 3-imposter
ATTACK_TYPE = 3

# LABEL: 0-BENIGNO, 1-MALIGNO
LABEL = 0

def main():
    print(f"Analizzatore avviato. Lettura da MongoDB [{SOURCE_COLLECTION}]")
    print(f"Output: {OUTPUT_FILE}")

    global LABEL

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[SOURCE_COLLECTION]

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    last_processed_id = None

    overhead_domains = ["alphasoc.com", "alphasoc.net", "wisdom.alphasoc"]

    while True:
        try:
            query_filter = {}
            if last_processed_id:
                query_filter = {"_id": {"$gt": last_processed_id}}

            cursor = collection.find(query_filter).sort("_id", 1)

            found_new = False
            with open(OUTPUT_FILE, "a") as out_file:
                for doc in cursor:
                    found_new = True
                    query_text = doc.get("query", "-")
                    
                    # Se intercettiamo il segnale da Kali, cambiamo la Label al volo
                    if "start-attack.signal" in query_text:
                        LABEL = 1
                        last_processed_id = doc["_id"]
                        print("Ricevuto START: query MALEVOLE (1)")
                        continue # Non scriviamo la query di segnale nel dataset

                    elif "stop-attack.signal" in query_text:
                        LABEL = 0
                        last_processed_id = doc["_id"]
                        print("Ricevuto STOP: query BENIGNE (0)")
                        continue # Non scriviamo la query di segnale nel dataset

                    # Validazione minima della query
                    if query_text == "-" or "." not in query_text:
                        last_processed_id = doc["_id"]
                        continue

                    # Controllo query dominio servizio tool utilizzato(flightsim)
                    is_overhead = any(dom in query_text for dom in overhead_domains)

                    if is_overhead:
                        final_label = 0
                        final_tag = 0
                    else:
                        # Segue l'andamento dell'interruttore generale
                        final_label = LABEL
                        final_tag = ATTACK_TYPE if LABEL == 1 else 0

                    # Calcolo Metriche (Solo per il file JSON)
                    ts = doc.get("ts")
                    qtype = doc.get("qtype_name", "UNK")
                    qproto = doc.get("proto", "UDP")
                    q_len, d_p, a_p, v_p, s_p, sub_c, m_cons = get_string_metrics(query_text)
                    entropy = shannon_entropy(query_text)

                    row = {
                        "ts": ts,
                        "query": query_text,
                        "qtype": qtype,
                        "qproto" : qproto,
                        "features": {
                            "len": q_len,
                            "entropy": round(entropy, 4),
                            "digit_p": d_p,
                            "alpha_p": a_p,
                            "vowel_p": v_p,
                            "special_p": s_p,
                            "sub_count": sub_c,
                            "max_cons": m_cons
                        },
                        "label": final_label,
                        "attack_tag": final_tag
                    }

                    out_file.write(json.dumps(row) + "\n")
                    out_file.flush()
                    
                    last_processed_id = doc["_id"]
                    
                    print(f"Processata: {query_text[:30]:<30} -> Salvata in JSON")

            if not found_new:
                time.sleep(1)

        except Exception as e:
            print(f"Errore durante l'elaborazione: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()