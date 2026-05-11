import json
import base64
import os

def decodifica_da_file(percorso_file, dominio_base):
    print(f"[*] Avvio decodifica dal file: {percorso_file}")
    
    payload_completo = ""
    conteggio_pacchetti = 0
    
    # 1. Lettura del file
    try:
        with open(percorso_file, 'r') as file:
            for linea in file:
                linea = linea.strip()
                if not linea:
                    continue  # Salta le righe vuote
                    
                # Parsing del JSON per ogni riga
                try:
                    dati_json = json.loads(linea)
                except json.JSONDecodeError:
                    print("[-] Ignorata una riga non in formato JSON valido.")
                    continue
                
                # Estrazione della query
                query_completa = dati_json.get('query', '')
                if not query_completa:
                    continue
                    
                # 2. Pulizia ed estrazione del chunk
                da_rimuovere = "." + dominio_base
                # Ci assicuriamo che la query contenga il nostro dominio di esfiltrazione
                if da_rimuovere in query_completa:
                    # Rimuoviamo il dominio radice e mettiamo in maiuscolo (richiesto dal Base32)
                    chunk_base32 = query_completa.replace(da_rimuovere, "").upper()
                    payload_completo += chunk_base32
                    conteggio_pacchetti += 1
                    
    except FileNotFoundError:
        print(f"[-] ERRORE: Il file '{percorso_file}' non è stato trovato.")
        return

    if conteggio_pacchetti == 0:
        print("[-] Nessuna query di esfiltrazione trovata per il dominio specificato.")
        return
        
    print(f"[*] Estratti con successo {conteggio_pacchetti} frammenti DNS.")
    print(f"[*] Payload Base32 concatenato: {payload_completo[:60]}... [TRUNCATED]")
    
    # 3. Ripristino del Padding
    # Il Base32 deve essere un multiplo di 8. Calcoliamo quanti '=' mancano alla fine.
    mancanti = len(payload_completo) % 8
    if mancanti != 0:
        payload_completo += "=" * (8 - mancanti)
        
    # 4. Decodifica finale
    try:
        testo_chiaro = base64.b32decode(payload_completo).decode('utf-8')
        print("\n[+] DECIFRATURA COMPLETATA. Dati esfiltrati:")
        print("--------------------------------------------------")
        print(testo_chiaro)
        print("--------------------------------------------------")
    except Exception as e:
        print(f"\n[-] Errore durante la decodifica finale: {e}")

# --- ESECUZIONE ---
if __name__ == "__main__":
    file_di_log = "log_esfiltrazione.json" 
    
    # Inserisci il dominio base che hai usato nel malware
    dominio_usato = "sandbox.alphasoc.xyz"
    decodifica_da_file(file_di_log, dominio_usato)