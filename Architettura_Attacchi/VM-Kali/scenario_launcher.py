import time
import random
import socket
import sys
import string
import threading
import subprocess

# --- CONFIGURAZIONE ---
TARGET_DNS = "192.168.1.33"
BENIGN_FILE = "dns_data/benign_domains_oarc.txt"
PROBABILITA_ATTACCO = 0.45   #45% di probabilità attacco
DURATA_TEST = 3600           # 60 minuti

# Carichiamo i domini una volta sola per efficienza
try:
    with open(BENIGN_FILE, "r") as f:
        BENIGN_DOMAINS = f.read().splitlines()
except Exception as e:
    print(f"Errore caricamento file: {e}")
    sys.exit(1)

def fast_query(domain):
    """Invia una query DNS ultra-rapida usando i socket di sistema"""
    try:
        # getaddrinfo invia la query DNS e aspetta la risoluzione
        socket.getaddrinfo(domain, 80)
        # Logghiamo solo internamente per non rallentare il terminale
    except:
        pass

def send_benign_burst(count=20):
    """Invia una raffica di query benigne in parallelo"""
    threads = []
    print(f"🟢 [NORMAL] Inizio raffica di {count} query...")
    for _ in range(count):
        dom = random.choice(BENIGN_DOMAINS)
        t = threading.Thread(target=fast_query, args=(dom,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    print(f"\tRaffica benigna completata.\n")

def send_signal(signal_name):
    """Invia i segnali START/STOP usando nslookup per il labeling nell'analyzer"""
    subprocess.run(["nslookup", signal_name, TARGET_DNS], capture_output=True)
    time.sleep(1) 

def run_custom_dga(count=100):
    """Genera una raffica di query DGA in parallelo"""
    send_signal("START-ATTACK.signal")
    print(f"🔴 [ATTACK] Inizio raffica DGA variabile ({count} query)...")
    
    threads = []
    for _ in range(count):
        lunghezza = random.randint(8, 63)
        prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=lunghezza))
        domain = f"{prefix}.attacco.test"
        
        t = threading.Thread(target=fast_query, args=(domain,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
    
    time.sleep(10)
    send_signal("STOP-ATTACK.signal")
    print(f"\t[ATTACK] Fine attacco.\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Mancanza parametri! Uso: python3 scenario_launcher.py <tunnel-dns|dga|c2>")
        sys.exit(1)

    ATTACK_TYPE = sys.argv[1]
    start_time = time.time()
    print(f"🚀 Avvio Generatore Turbo per scenario: {ATTACK_TYPE}")

    try:
        while (time.time() - start_time) < DURATA_TEST:
            scelta = random.random()
            
            if scelta < (1 - PROBABILITA_ATTACCO):
                # --- TRAFFICO NORMALE ---
                nb = random.randint(10, 40)
                send_benign_burst(nb)
                # Pausa tra le raffiche per simulare comportamento umano
                time.sleep(random.uniform(0.2, 0.6))
            else:
                # --- TRAFFICO MALEVOLO ---
                if ATTACK_TYPE == "dga":
                    nd = random.randint(30, 50)
                    run_custom_dga(nd)
                else:
        		# Per flightsim (Tunneling, Imposter, C2)
                        send_signal("START-ATTACK.signal")
                        print(f"🔴 [ATTACK] Lancio sessione multipla flightsim: {ATTACK_TYPE}")
        
                        # Eseguiamo l'attacco 4-5 volte per aumentare il volume dei campioni
                        for i in range(6):
                            print(f"   [+] Esecuzione {i+1}/6...")
                            subprocess.run(["flightsim", "run", ATTACK_TYPE], capture_output=True)
                            time.sleep(1) # Breve pausa tra le ripetizioni
                        
                        print(f"⏳ Attesa persistenza log...")
                        time.sleep(10)
                        send_signal("STOP-ATTACK.signal")
                        print(f"\t[ATTACK] Fine attacco {ATTACK_TYPE}.\n")
                
    except KeyboardInterrupt:
        print("\n👋 Generazione interrotta dall'utente.")
        sys.exit(0)
