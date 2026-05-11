import json
import os
import time
from log_streamer import read_zeek_log

# --- CONFIGURAZIONE ---
OUTPUT_DIR = "output_json"
SOURCE_JSON = f"{OUTPUT_DIR}/analyze_data.json"
ALERTS_FILE = f"{OUTPUT_DIR}/detected_data.json"

# --- SOGLIE DI DETECTION ---
TYPES = ["TXT", "CNAME", "NULL"]
LEN = 50
ENTROPY = 4.2
DIGIT = 0.25
ALPHA = 0.5
VOWEL = 0.15
SPECIAL = 0.1
SUB_COUNT = 3
CONS = 6

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Detector attivo. Monitoraggio su: {SOURCE_JSON}")
    print("-" * 80)

    for riga_json in read_zeek_log(SOURCE_JSON):
        r = riga_json.strip()
        if not r:
            continue

        try:
            dati = json.loads(r)
            query = dati.get("query", "UNK")
            qtype = dati.get("qtype", "UNK")
            lbl = dati.get("label", 0)
            tag = dati.get("attack_tag", 0)
            f = dati.get("features", {})
            
            entr   = f.get("entropy", 0)
            m_cons = f.get("max_cons", 0)
            v_p    = f.get("vowel_p", 0)
            d_p    = f.get("digit_p", 0)
            a_p    = f.get("alpha_p", 0)
            s_p    = f.get("special_p", 0)
            sub_c  = f.get("sub_count", 0)
            q_len  = f.get("len", 0)

            alerts = []
            
            if entr > ENTROPY: 
                alerts.append(f"Alta Entropia ({entr})")
            if m_cons >= CONS:     
                alerts.append(f"Troppe Consonanti consecutive ({m_cons})")
            if v_p < VOWEL and v_p > 0: 
                alerts.append(f"Basso Rapporto Vocali ({v_p})")
            if d_p > DIGIT:       
                alerts.append(f"Troppi Numeri ({d_p})")
            if q_len >= LEN:       
                alerts.append(f"Lunghezza Sospetta ({q_len})")
            if sub_c > SUB_COUNT:
                alerts.append(f"Troppi Sottodomini ({sub_c})")
            if a_p < ALPHA and a_p > 0:
                alerts.append(f"Poche Lettere ({a_p})")
            if s_p > SPECIAL:
                alerts.append(f"Caratteri Speciali elevati ({s_p})")
            if qtype in TYPES:
                alerts.append(f"Tipo Record Sospetto ({qtype})")

            if alerts:
                alert_event = {
                    "ts": dati.get("ts"),
                    "query": query,
                    "label": lbl,
                    "attack_tag": tag,
                    "reasons": alerts,
                    "full_features": f
                }

                print(f"\033[91m[!!!] MINACCIA: {query[:50]}\033[0m")
                for reason in alerts:
                    print(f"    └─ {reason}")

                with open(ALERTS_FILE, "a") as f_out:
                    f_out.write(json.dumps(alert_event) + "\n")
                    f_out.flush()
                    os.fsync(f_out.fileno())

        except json.JSONDecodeError:
            time.sleep(0.1)#se riga incompleta, aspetta che si completi
            continue
        except Exception as e:
            print(f"Errore: {e}")
            continue

if __name__ == "__main__":
    main()