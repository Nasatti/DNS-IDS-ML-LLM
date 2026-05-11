# 🏗️ Architettura e Attacchi: Infrastruttura IDS e Simulazione

Questa directory contiene il cuore dell'infrastruttura di rete, la configurazione dei container Docker per il monitoraggio e l'intera pipeline software sviluppata in Python per analizzare il traffico DNS in tempo reale. 

L'ambiente è stato concepito seguendo i principi dell'isolamento logico e della segregazione dei servizi per l'identificazione di minacce quali DNS Tunneling, DGA e Typosquatting (Imposter).

---

## 🗂️ 1. Struttura della Directory

Di seguito la mappa visiva della repository e dei file generati a runtime dall'infrastruttura. 

*(Nota: le cartelle contenenti file pesanti o dati sensibili sono escluse dal tracciamento tramite `.gitignore` e verranno generate localmente al primo avvio).*

```text
📂 architettura_attacchi/
├── 📂 logs/                  # Generati a runtime da Zeek
│   ├── 📄 conn.log
│   ├── 📄 dns.log            # Log operativo principale in formato JSON
│   ├── 📄 packet_filter.log
│   ├── 📄 reporter.log
│   └── 📄 ssl.log
├── 📂 output_json/           # Dati strutturati post-elaborazione
│   ├── 📄 analyze_data.json
│   └── 📄 detected_data.json
├── 📂 pcaps/                 # Catture raw di Tshark
│   └── 📄 attack_tunneling_sample.pcap  # Esempio di traffico catturato
├── 📂 mongo_data/            # Volume persistente del DB NoSQL
├── 📂 pihole/                # File di configurazione del DNS Sinkhole
├── 📄 analyzer.py            # Orchestratore e classificazione dei dati
├── 📄 detector.py            # Motore IDS basato su euristiche
├── 📄 dns_math.py            # Calcolo entropia e metriche matematiche
├── 🐳 docker-compose.yml     # File di orchestrazione dei microservizi
├── 📄 export_tesi.json       # Export finale dei dati per l'addestramento
├── 📄 ingestor.py            # Inserimento in real-time dei log nel DB
├── 📄 log_streamer.py        # Generatore iterativo (tail-f) per lettura log
├── 📄 make_plot.py           # Script per la generazione dei grafici
└── 📜 reset_system.sh        # Script per riavvio pulito dell'ambiente (Docker + Tmux)
```
## 🐋 2. Configurazione Docker e Isolamento di Rete (UFW)

L'infrastruttura di monitoraggio si avvale di un'architettura a microservizi orchestrata tramite **Docker Compose (V2)**. Per garantire che le configurazioni siano perfette e il sistema acquisisca tutto il traffico senza rumore di fondo o fughe di dati, è fondamentale impostare rigorosamente le policy di rete.

### Le Regole UFW (Uncomplicated Firewall)
Per assicurare la massima integrità del dataset e impedire il *Data Poisoning*, i nodi sono sottoposti a isolamento logico. Prima di avviare i container, è applicata una rigorosa policy **Default Deny Outgoing** tramite UFW. Questo garantisce:
*   **Integrità:** Eliminazione assoluta del rumore di fondo (es. telemetria dell'OS, aggiornamenti).
*   **Contenimento:** Prevenzione della fuoriuscita del traffico d'attacco verso ISP o reti pubbliche esterne.
*   **Riproducibilità:** Creazione di un ambiente puramente deterministico per le successive fasi di ML.

### I Microservizi Orchestrati
*   **Pi-hole:** Funge da DNS Sinkhole e risolutore primario. È agganciato agli altri strumenti tramite la direttiva `network_mode: service:pihole` per fornire visibilità totale sui pacchetti.
*   **Zeek:** Configurato come Network Security Monitor con il flag `-C` per ignorare il checksum offloading UDP, previene la perdita di pacchetti e produce i log strutturati in `dns.log`.
*   **Tshark & Wireshark-Web:** Sistema di cattura raw eseguito con privilegi elevati (`NET_ADMIN`, `NET_RAW`) che utilizza un *ring buffer* per prevenire la saturazione del disco.
*   **MongoDB:** Database NoSQL che si occupa dello storage persistente dei log, dividendo logicamente le collezioni in base allo scenario di attacco simulato.

---

## 🚀 3. Avvio del Sistema
Una volta configurate correttamente le regole firewall e i requisiti Docker, l'intero ambiente di analisi viene sollevato automaticamente tramite lo script di avvio.

Eseguendo il file:
```bash
./reset_system.sh
```

## ⚙️ 4. Pipeline Software e Moduli Python

La logica di elaborazione del traffico è basata sul principio di Separazione delle Responsabilità (SoC), frammentando il flusso in script indipendenti ed efficienti. Di seguito viene descritto il ruolo di ciascun modulo all'interno del ciclo di vita del dato, dall'ingestione alla visualizzazione:

### 📥 Ingestor (`ingestor.py`)
È il punto di ingresso dei dati: legge il flusso continuo generato dal log streamer, applica filtri selettivi sull'indirizzo IP sorgente della macchina Kali e si occupa dell'inserimento dei record validi in tempo reale all'interno del database MongoDB.

### 🧠 Analyzer (`analyzer.py`)
Agisce come orchestratore logico del sistema. Recupera i record grezzi, invoca la libreria `dns_math.py` per il calcolo delle metriche e assegna a ogni richiesta una **Label** di classe (es. 0: Legittimo, 1: Malevolo) basandosi su specifici segnali di trigger, salvando l'output per il successivo addestramento dei modelli di Machine Learning.

### 🚨 Detector (`detector.py`)
Rappresenta il motore IDS (Intrusion Detection System) euristico. Analizza le feature estratte e genera allarmi istantanei basandosi su rigide soglie matematiche, come ad esempio un'Entropia > 4.2, un numero di consonanti contigue >= 6 o livelli di sottodominio > 3.

### 🧮 DNS Math (`dns_math.py`)
È la libreria analitica core incaricata dell'estrazione delle feature matematiche da ogni singola query. Implementa il calcolo dell'Entropia di Shannon e l'estrazione di ratio specifiche fondamentali, come il rapporto di caratteri alfanumerici e speciali, la lunghezza totale della query e il conteggio dei livelli di sottodominio.

### 📜 Log Streamer (`log_streamer.py`)
Implementa un generatore iterativo basato sull'istruzione `yield` per la lettura in modalità *tail-f* del file `dns.log` prodotto da Zeek. Questa logica riduce la complessità spaziale a *O(1)* ed evita picchi anomali di utilizzo della CPU introducendo un micro-polling calibrato.

### 📊 Make Plot (`make_plot.py`)
*(Nota: modulo adibito alla visualizzazione, inserito in base alla struttura logica della tesi).* Si occupa di generare grafici e plot visivi estraendo i dati dal database o dai log consolidati. Fornisce una rappresentazione grafica essenziale per comprendere le metriche (come l'entropia, la lunghezza delle query e la distribuzione delle classi) ai fini della stesura del report finale.

## 🛑 5. Post Attacco e Salvataggio Dati

Una volta terminata la simulazione dell'attacco generata dalla VM Kali (tramite lo script scenario_launcher.py), è necessario spegnere correttamente l'ambiente di monitoraggio.
Eseguire il comando:
```bash
sudo docker compose down
```
Questo comando fermerà in modo sicuro e pulito tutti i container (Pi-hole, Zeek, Wireshark, ecc.). Tuttavia, grazie alla configurazione dei volumi persistenti, i dati elaborati e le query analizzate rimarranno saldamente salvati all'interno di MongoDB.
Per estrarre i dati da MongoDB, eseguiamo i due comandi:
```bash
sudo docker exec mongodb mongoexport --db tesi_dns --collection test_reale --out /data/db/export_tesi.json --jsonArray
sudo docker cp mongodb:/data/db/export_tesi.json ./export_tesi.json
```
Per avere i risultati finali, bisognerà semplicemente salvare quest'ultimo file di mongoDB e le cartelle `output_json`, `pcaps` e `log` 
