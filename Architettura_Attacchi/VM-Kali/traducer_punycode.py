# traduttore_tesi_completo.py
import sys

file_input = "dns_data/imposter_5k.txt"
file_output = "dns_data/imposter_tradotti.txt"

# Leggiamo TUTTI i domini dal file originale
with open(file_input, "r") as file:
    domini = file.readlines()

# Apriamo il nuovo file in scrittura ("w") con codifica UTF-8
with open(file_output, "w", encoding="utf-8") as outfile:
    
    # Scriviamo l'intestazione nel file
    outfile.write(f"{'DOMINIO DI RETE (PUNYCODE)'.ljust(35)} | {'DOMINIO VISIVO'}\n")
    outfile.write("-" * 75 + "\n")

    # Cicliamo su tutti i 5000 domini
    for dominio in domini:
        punycode = dominio.strip()
        if not punycode:  # Saltiamo eventuali righe vuote
            continue
            
        try:
            # Magia di Python per tradurre da xn-- ai caratteri speciali
            visivo = punycode.encode('utf-8').decode('idna')
            
            # Scriviamo la riga formattata nel nuovo file (aggiungendo \n per andare a capo)
            outfile.write(f"{punycode.ljust(35)} | {visivo}\n")
        except Exception:
            # In caso di un raro errore di decodifica, lo segnaliamo senza bloccare il programma
            outfile.write(f"{punycode.ljust(35)} | [ERRORE DI TRADUZIONE]\n")

print(f"Traduzione di {len(domini)} domini completata!")
print(f"Apri il file '{file_output}' per vedere i risultati.")
