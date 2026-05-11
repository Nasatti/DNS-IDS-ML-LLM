# 💻 VM Kali: Attaccante

Questa directory contiene gli script e i tool utilizzati all'interno della macchina virtuale Kali Linux (che funge da Client/Attaccante nell'infrastruttura). L'obiettivo di questo ambiente è generare un traffico di rete realistico, miscelando query DNS legittime a richieste malevole per testare l'efficacia del sistema IDS.

---

## 🛠️ 1. Simulazione Stocastica e Limiti di FlightSim

L'iniezione dei payload malevoli è orchestrata principalmente dallo script `scenario_launcher.py`, che combina per il 55% traffico benigno (campionato da una whitelist) e per il 45% raffiche di anomalie. Per generare alcune minacce è stato integrato **Network Flight Simulator** (FlightSim). 

Tuttavia, durante le fasi di test, sono emersi dei limiti intrinseci nell'utilizzo esclusivo di FlightSim:
*   **C2 (Command & Control):** FlightSim genera traffico C2, ma con pochissima varianza, riutilizzando costantemente gli stessi domini. Inoltre, dal punto di vista metodologico, il rilevamento strutturale del C2 necessita della correlazione con la risposta del server (es. direttive nei record TXT). Poiché il nostro modello analizza unicamente le feature lessicali della query lato client, **l'attacco C2 è stato rimosso dal task di Machine Learning**.
*   **Imposter (Typosquatting):** Anche per gli attacchi Imposter, FlightSim offriva un bacino di esempi troppo ridotto. Per evitare il rischio di *overfitting* sui modelli di Machine Learning (che avrebbero imparato a memoria quei pochi domini), è stato creato un **nuovo script personalizzato** dedicato esclusivamente alla generazione massiva e variegata di attacchi Typosquatting e Homograph.

---

## 🎭 2. L'Attacco Imposter e la Magia del Punycode

Il nuovo script dedicato agli attacchi Imposter sfrutta a pieno tecniche di contraffazione visiva, con un focus particolare sugli attacchi omofoni basati su **Punycode**. 

Il protocollo DNS originale accetta esclusivamente caratteri ASCII (alfabeto inglese, numeri e trattini). Per permettere la registrazione di domini internazionalizzati (IDN - Internationalized Domain Names) contenenti caratteri speciali, accenti o alfabeti diversi (come cirillico o greco), è stato introdotto il Punycode. Questo sistema codifica i caratteri speciali in una stringa ASCII compatibile, anteponendo sempre il prefisso **`xn--`**.

**Come lo sfruttano gli hacker?**
Gli attaccanti registrano domini utilizzando caratteri cirillici che sono visivamente identici alle normali lettere latine. I browser moderni, per comodità dell'utente, traducono automaticamente il Punycode mostrando il carattere speciale, ingannando l'occhio umano. 

![Punycode](https://github.com/Nasatti/DNS-IDS-ML-LLM/blob/main/Architettura_Attacchi/VM-Kali/punycode.png)

Mentre un essere umano vedrà un link apparentemente legittimo (es. *apple.com*), il traffico DNS sottostante, analizzato dal nostro IDS, mostrerà la sua vera natura codificata (es. *xn--80ak6aa92e.com*). 

---

## 🚀 3. Comandi per l'Esecuzione degli Attacchi

Di seguito sono riportati i comandi da lanciare all'interno del terminale della VM Kali per avviare le diverse simulazioni. *(Nota: per tutti gli script è necessario essere posizionati in questa directory)*.

**Per avviare la simulazione principale (Tunneling e DGA miscelati al traffico normale):**
Esegui il comando: 
```bash
python3 scenario_launcher.py [tunnel_dns/dga/imposter/c2]
```

**Per avviare la simulazione specifica degli attacchi Imposter/Punycode:**
Esegui il comando: 
```bash
./imposter_launcher.sh
```
