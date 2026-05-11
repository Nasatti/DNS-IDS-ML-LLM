# 🕵️‍♂️ Esfiltrazione Dati: Simulazione di DNS Tunneling

Questa directory contiene gli script sviluppati per simulare e dimostrare l'esfiltrazione di dati sensibili tramite il protocollo DNS. L'obiettivo di questa fase della tesi è mostrare come un attaccante possa aggirare policy di rete stringenti, come i firewall configurati in modalità **Default Deny Outgoing**, sfruttando il fatto che il traffico DNS è tipicamente sempre consentito per la risoluzione dei nomi a dominio.

## ⚠️ Contesto della Simulazione e C2 Beaconing
Per gli scopi di questo progetto, ci siamo concentrati esclusivamente sull'**esecuzione** attiva dell'esfiltrazione dei dati. Non abbiamo provveduto a simulare le fasi iniziali della *Kill Chain*, ovvero non abbiamo diffuso il malware tramite campagne di phishing, mail infette o tecniche di ingegneria sociale.

In uno scenario reale, una volta che il malware infetta con successo una macchina vittima, il primo passo non è l'esfiltrazione immediata, bensì la creazione di un **Beaconing** verso il server Command & Control (C2). Il malware invia segnali periodici (spesso sfruttando tecniche DGA per variare i domini) per notificare all'attaccante che il sistema è compromesso e per mettersi in ascolto di eventuali istruzioni su quali file colpire. Nel nostro ambiente di test, abbiamo assunto la compromissione come già avvenuta e abbiamo innescato direttamente la sottrazione del bersaglio predefinito.

---

## 🦠 1. Il Malware di Esfiltrazione (VM-Kali)
Questa cartella contiene lo script Python che agisce come agente malevolo all'interno della rete compromessa. Il suo compito è elaborare i dati locali e farli fuoriuscire furtivamente:
*   **Accesso ai Dati Reali:** Lo script è stato configurato per prelevare file critici di sistema, come `/etc/shadow`. Per aggirare i permessi, viene eseguito con privilegi di amministratore (`sudo`) e utilizza percorsi assoluti.
*   **Codifica Base32:** Per garantire che il contenuto del file possa viaggiare senza corrompersi e formare nomi a dominio validi, l'intero payload viene convertito in Base32 (che utilizza solo caratteri alfanumerici A-Z e 2-7).
*   **Frammentazione (Chunking):** Lo standard RFC 1035 impone un limite massimo di 63 caratteri per singola etichetta di un dominio. Lo script provvede quindi a spezzare la lunga stringa Base32 in frammenti più piccoli di circa 50-55 caratteri.
*   **Evasione tramite Jitter:** Ogni frammento viene accodato a un dominio controllato dall'attaccante (es. `chunk.sandbox.alphasoc.xyz`) e inviato come query DNS. Per ingannare i sistemi IDS (Intrusion Detection System) che analizzano la frequenza dei pacchetti, viene introdotto un **Jitter**, ovvero una pausa stocastica e casuale compresa tra 0.5 e 1.5 secondi tra una query e l'altra.

## 💻 2. Il Decoder Lato C2 e l'Analisi (Server-Ubuntu)
Questo script agisce come l'infrastruttura dell'attaccante (il server ricevente) a completamento della Kill Chain. Il suo scopo è ricostruire il file rubato partendo dalle query intercettate:
*   **Estrazione e Pulizia:** Il decoder analizza i log di rete, filtra le richieste DNS pertinenti all'attacco ed elimina il dominio radice (il suffisso) per isolare il puro payload.
*   **Riassemblaggio e Padding:** I frammenti vengono concatenati in sequenza. Dato che la frammentazione rimuove i caratteri di riempimento, lo script ripristina matematicamente il *padding* (i caratteri `=`) richiesto dallo standard Base32 calcolando il modulo 8 della lunghezza della stringa totale.
*   **Decodifica Finale:** La stringa riassemblata e corretta viene decodificata, rivelando in chiaro all'attaccante il contenuto originale del file esfiltrato con successo.

## 🏆 Risultato della Decodifica

Di seguito è mostrato il risultato finale dell'esecuzione del decoder (salvato nel file `risultato.png`). L'immagine dimostra l'avvenuta ricostruzione e decodifica del file esfiltrato, confermando il successo dell'attacco di DNS Tunneling simulato:

