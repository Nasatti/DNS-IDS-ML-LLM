# 🏗️ Architettura e Attacchi: Infrastruttura IDS e Simulazione

Questa directory principale ospita l'intera infrastruttura di rete progettata per l'acquisizione, il monitoraggio e l'analisi del traffico DNS. L'ambiente è stato concepito seguendo i rigorosi principi dell'isolamento logico e della separazione delle responsabilità (SoC), ed è diviso in due macro-componenti che simulano un ecosistema reale: un attaccante (Client) e un difensore (IDS/Monitoraggio).

## 🗂️ 1. Struttura della Directory

All'interno di questa directory troverai due sottocartelle, ciascuna contenente il codice e le configurazioni del rispettivo ambiente:

*   **`VM-Kali/` (L'Attaccante):** Rappresenta il nodo sorgente. Contiene gli script per generare sia il traffico legittimo simulato sia i tool di adversary emulation per iniettare le minacce. Tutto il traffico DNS generato da questa macchina è forzatamente instradato verso il nodo di monitoraggio.
*   **`Server-Ubuntu/` (Il Difensore / IDS):** Ospita l'infrastruttura di analisi a microservizi (orchestrata tramite Docker) e l'intera pipeline software scritta in Python. Si occupa di intercettare il traffico di Kali, estrarre le feature matematiche tramite Zeek e classificare le query.

*Ogni cartella contiene un proprio `README.md` con le istruzioni dettagliate per l'avvio e la configurazione specifica dei servizi.*

---

## 🔒 2. Politiche di Sicurezza e Isolamento

Per garantire la validità scientifica dell'esperimento, i nodi sono sottoposti a un rigoroso isolamento logico tramite **UFW (Uncomplicated Firewall)**, con una policy di **Default Deny Outgoing**. Questo approccio garantisce tre obiettivi fondamentali:
1.  **Integrità:** Eliminazione assoluta del rumore di fondo (es. telemetria del sistema operativo, aggiornamenti automatici) per evitare inquinamento dei dati (*Data Poisoning*).
2.  **Contenimento:** Prevenzione della fuoriuscita accidentale del traffico d'attacco verso gli ISP o le reti pubbliche esterne.
3.  **Riproducibilità:** Creazione di un ambiente puramente deterministico, essenziale per la successiva fase di addestramento dei modelli di Machine Learning.

---

## 🦠 3. Simulazione Stocastica degli Attacchi

L'iniezione dei payload malevoli è delegata a uno script dedicato (`scenario_launcher.py`) presente nella VM Kali. Per produrre un dataset realistico ed evitare il rischio di *overfitting* sui modelli di Machine Learning, lo script utilizza una **logica stocastica**. 

Le sessioni di test miscelano il traffico in modo accurato: per ogni attacco, il **55% è traffico benigno** (campionato da una whitelist), mentre il **45% è composto da raffiche di anomalie** o traffico generato tramite *Network Flight Simulator*.

Le classi di minacce simulate e analizzate sono:
*   **DNS Tunneling:** Trasporto di stringhe ad elevata densità entropica, spesso all'interno di record rari come TXT o CNAME, per mascherare l'esfiltrazione dei dati.
*   **DGA (Domain Generation Algorithm):** Stringhe casuali generate proceduralmente, caratterizzate da lunghe sequenze di consonanti. Simulano la ricerca dinamica di un server C2 e vengono inviate a raffiche (*burst effect*).
*   **Imposter (Typosquatting):** Domini ad alta reputazione alterati morfologicamente (es. omofonia, suffissi o prefissi anomali). Essendo strutturati con bassa entropia, cercano di aggirare le euristiche matematiche tradizionali.

*(Nota metodologica: L'identificazione del traffico **C2 (Command & Control)** necessita della correlazione con la risposta del server (es. direttive nei record TXT). Poiché questo progetto si concentra esclusivamente sull'analisi delle feature lessicali della singola Query generata dal client, l'attacco C2 è stato escluso dal task di Machine Learning).*
