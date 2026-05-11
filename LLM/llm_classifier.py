import pandas as pd
import requests
import time
import re

# --- CONFIGURAZIONI ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELLO_LLM = "gpt-oss:120b" 
FILE_OUTPUT = "risultati_llm.csv"

print("Caricamento e preparazione dei dati in corso...")
try:
    df_dga = pd.read_json('../attacchi/dga.json', lines=True)
    df_tunnel = pd.read_json('../attacchi/tunnel.json', lines=True)
    df_imposter = pd.read_json('../attacchi/imposter.json', lines=True)

    df_dga_feat = pd.json_normalize(df_dga['features'])
    df_tunnel_feat = pd.json_normalize(df_tunnel['features'])
    df_imposter_feat = pd.json_normalize(df_imposter['features'])

    df_dga = pd.concat([df_dga_feat, df_dga[['query', 'label', 'attack_tag', 'qtype']]], axis=1)
    df_tunnel = pd.concat([df_tunnel_feat, df_tunnel[['query', 'label', 'attack_tag', 'qtype']]], axis=1)
    df_imposter = pd.concat([df_imposter_feat, df_imposter[['query', 'label', 'attack_tag', 'qtype']]], axis=1)

    df_completo = pd.concat([df_dga, df_tunnel, df_imposter], ignore_index=True)
    
    df_sample = df_completo.groupby('attack_tag').sample(n=100, random_state=42).reset_index(drop=True)
    df_sample = df_sample.sample(frac=1, random_state=42).reset_index(drop=True)
    print(df_sample['attack_tag'].value_counts())
    print(f"Creato campione finale bilanciato: {len(df_sample)} query totali.")

except Exception as e:
    print(f"Errore: {e}")
    exit()

def interroga_llm_ragionato(dominio, f_len, f_entropy, f_digit_p, f_alpha_p, f_vowel_p, f_special_p, f_sub_count, f_max_cons, f_qtype, max_tentativi=3):
    
    prompt = f"""Agisci come un analista di sicurezza DNS. Analizza le metriche e classifica il dominio.
Regole delle classi:
0 = Traffico Normale (Domini legittimi, parole di senso compiuto, assenza di anomalie strutturali, anche indirizzi ip, solitamente record A o AAAA)
1 = Tunneling / Data Exfiltration (LUNGHEZZA ESTREMA. Molto spesso utilizzano record di tipo TXT per trasportare payload codificati. L'attaccante infila i dati rubati in una stringa lunghissima attaccata al dominio base)
2 = Malware DGA (Stringhe casuali, altissima entropia(non per tutto il dominio, anche per solo un sotto-dominio), lunghezza media/corta, POCHI sottodomini, sembrano ammassi di lettere impronunciabili, non basarti solamente sul dato dell'entropia ma prova a leggere il dominio e a capire se sembra una parola reale o no)
3 = Imposter / Typosquatting (Domini malevoli che imitano brand, spesso usano caratteri speciali, errori di battitura o sostituzioni di lettere per confondere gli utenti, spesso è in Punycode(xn--))

Dati da analizzare per la query: '{dominio}'
- Tipo di record DNS (qtype): {f_qtype}
- Lunghezza stringa (len): {f_len}
- Entropia di Shannon (entropy): {f_entropy}
- Numero di sottodomini (sub_count): {f_sub_count}
- Massima sequenza di consonanti (max_cons): {f_max_cons}
- Percentuale cifre (digit_p): {f_digit_p}
- Percentuale vocali (vowel_p): {f_vowel_p}
- Percentuale caratteri speciali (special_p): {f_special_p}

ISTRUZIONI:
Fai una brevissima analisi (max 2 righe) spiegando come le feature (specialmente qtype, lunghezza ed entropia) si allineano alle regole.
Alla fine, scrivi come ultima riga il risultato in questo ESATTO formato:
CLASSE: [NUMERO]"""

    payload = {"model": MODELLO_LLM, "prompt": prompt, "stream": False}
    
    for tentativo in range(max_tentativi):
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=120)
            if response.status_code == 200:
                risposta_completa = response.json().get('response', '').strip()
                
                # Regex per cercare "CLASSE: X" 
                match = re.search(r'CLASSE:\s*([0-3])', risposta_completa, re.IGNORECASE)
                
                if match:
                    classe_estratta = int(match.group(1))
                    return classe_estratta, risposta_completa
                else:
                    return -1, risposta_completa
            else:
                pass
        except:
            time.sleep(3)
            
    return -1, "Errore di Rete o Timeout"

previsioni_llm = []
ragionamenti_llm = [] 

print("\nInizio classificazione Ragionata LLM con QTYPE...")
print(f"{'DOMINIO':<35} | {'LLM':<5} | {'REALE':<5} | {'ESITO':<5}")
print("-" * 60)

for index, row in df_sample.iterrows():
    dominio = row.get('query', 'Sconosciuto')
    f_qtype = row.get('qtype', 'Sconosciuto')
    f_len = row.get('len', 0)
    f_entropy = round(row.get('entropy', 0.0), 3)
    f_digit_p = round(row.get('digit_p', 0.0), 3)
    f_alpha_p = round(row.get('alpha_p', 0.0), 3)
    f_vowel_p = round(row.get('vowel_p', 0.0), 3)
    f_special_p = round(row.get('special_p', 0.0), 3)
    f_sub_count = int(row.get('sub_count', 0))
    f_max_cons = int(row.get('max_cons', 0))
    classe_reale = row.get('attack_tag', -1)
    
    print(f"[{index+1:03d}] {dominio[:30]: <30} |", end=" ", flush=True)
    
    predizione, ragionamento = interroga_llm_ragionato(
        dominio, f_len, f_entropy, f_digit_p, f_alpha_p, f_vowel_p, f_special_p, f_sub_count, f_max_cons, f_qtype
    )
    
    previsioni_llm.append(predizione)
    ragionamenti_llm.append(ragionamento)
    
    esito = "✅" if predizione == classe_reale else "❌"
    print(f"{predizione:<5} | {classe_reale:<5} | {esito}")

df_sample['llm_prediction'] = previsioni_llm
df_sample['llm_reasoning'] = ragionamenti_llm

df_sample.to_csv(FILE_OUTPUT, index=False)
print("-" * 60)
print(f"Test completato! Risultati salvati in: {FILE_OUTPUT}")