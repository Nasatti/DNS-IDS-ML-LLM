# 🛡️ Analisi e Rilevamento di Attacchi DNS tramite Machine Learning e LLM

Questa repository contiene il codice sorgente, l'infrastruttura e i modelli sviluppati per il mio progetto di tesi. L'obiettivo del progetto è l'acquisizione, il monitoraggio e l'analisi del traffico DNS al fine di identificare anomalie e minacce informatiche quali DNS Tunneling, DGA (Domain Generation Algorithms) e Typosquatting (Imposter).

Il progetto confronta l'efficacia di un approccio classico basato su Machine Learning con l'utilizzo di Large Language Models (LLM) avanzati per l'ispezione della semantica delle query.

## 🏗️ Architettura del Progetto

La repository segue una rigorosa Separazione delle Responsabilità (SoC) ed è divisa in 4 macro-aree:

### 1. `Architettura_Attacchi/`
Contiene la configurazione dell'ambiente di simulazione e difesa isolato tramite UFW (Default Deny Outgoing) per garantire la riproducibilità:
*   **`Server-Ubuntu/`**: L'infrastruttura di monitoraggio orchestrata via Docker Compose (V2), comprensiva di Pi-hole, Zeek, Tshark e MongoDB. Contiene la pipeline Python di analisi: `log_streamer.py`, `dns_math.py`, `ingestor.py`, `analyzer.py` e `detector.py`.
*   **`VM-Kali/`**: L'ambiente dell'attaccante. Include lo script `scenario_launcher.py` per l'iniezione stocastica di payload malevoli (Tunneling, DGA, Imposter) miscelati a traffico benigno.

### 2. `ML/` (Machine Learning)
Contiene i Jupyter Notebook e i dataset anonimizzati utilizzati per l'addestramento dei modelli.
*   I modelli implementati (Random Forest, CatBoost e Multi-Layer Perceptron) eseguono una classificazione multiclasse (0: Normal, 1: Tunneling, 2: DGA, 3: Imposter).
*   L'estrazione delle feature si concentra su parametri matematici come `len`, `entropy`, `sub_count` e `qtype`. 

### 3. `LLM/` (Large Language Models)
Contiene gli script Python per l'interazione via API REST con un'istanza locale di Ollama (modello `gpt-oss:120b`).
*   Mostra le strategie di **Prompt Engineering** adottate, tra cui il *Chain of Thought* (ragionamento sequenziale) e le definizioni chirurgiche per distinguere le classi e individuare attacchi complessi tramite Punycode.
*   Include i risultati prestazionali e il confronto diretto con la baseline di ML.

### 4. `Exfiltration/`
Una sezione dedicata alla dimostrazione pratica dell'esfiltrazione dati (Data Exfiltration) sfruttando il DNS Tunneling]:
*   **`VM-Kali/`**: Script Python (lato Kali) che codifica file sensibili (es. `/etc/shadow`) in Base32, ne effettua il frammentamento (chunking) e introduce un ritardo (Jitter) per bypassare i controlli temporali.
*   **`Server-Ubuntu/`**: Il decoder lato C2 che estrae il payload dai log di rete, gestisce il padding matematico della codifica Base32 e ricostruisce la stringa originale.

## ⚙️ Requisiti e Setup
Per l'ambiente Server è richiesto Docker e i conteiner specifici, nella VM servirà il tool [Network Flight Simulator](https://github.com/alphasoc/flightsim), per la parte di ML è stato utilizzato Jupyter, infine per LLM è necessaria un'istanza locale di Ollama. 
*Più informazioni verranno date nelle specifiche cartelle.*

## ⚠️ Disclaimer
Questo progetto è stato sviluppato esclusivamente per scopi accademici e di ricerca nell'ambito della sicurezza informatica. I file di configurazione e di esfiltrazione sono proof-of-concept progettati per operare in ambienti controllati.
