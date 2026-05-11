# 🧠 LLM: Analisi Semantica e Rilevamento tramite Large Language Models

Questo documento illustra la metodologia di implementazione, le strategie di prompt engineering e i risultati ottenuti utilizzando un Large Language Model (LLM) di ultima generazione per la classificazione della sicurezza DNS. L'obiettivo di questa sezione è superare i limiti statistici del Machine Learning classico aggiungendo un livello di comprensione semantica alle query analizzate.

---

## 🗂️ 1. Struttura della Directory

All'interno di questa cartella sono presenti gli script e i report generati durante la fase di inferenza e valutazione:

*   **`ll_classifier.py`**: Script principale che implementa le chiamate API verso l'LLM e definisce le logiche di Prompt Engineering.
*   **`valutation_llm.py`**: Script dedicato all'analisi dei risultati e al calcolo delle metriche di performance (Accuracy, Precision, Recall, F1-Score).
*   **`risultati_llm.csv`**: File generato in output contenente le predizioni del modello e le relative spiegazioni testuali.

---

## ⚙️ 2. Architettura e Tecnologie

Per la fase di sperimentazione avanzata è stato selezionato il modello **gpt-oss:120b**, caratterizzato da 120 miliardi di parametri. La scelta è ricaduta su questo modello per la sua elevata capacità di ragionamento semantico e comprensione del contesto testuale.

*   **Hosting Locale:** Il modello è stato ospitato localmente tramite la piattaforma **Ollama** sul server universitario.
*   **Ottimizzazione della Latenza:** L'interrogazione avviene tramite API REST puntando a `localhost`, eliminando i colli di bottiglia della rete esterna e garantendo la massima velocità di inferenza.

---

## 💬 3. Prompt Engineering e Integrazione Dati

A differenza dei modelli di Machine Learning classico, l'LLM ha elaborato contemporaneamente le metriche numeriche (lunghezza, entropia, conteggio sottodomini, qtype) e il dato testuale grezzo, ovvero la stringa della query DNS effettiva. Questo ha permesso al modello di "leggere" il dominio e identificare tentativi di imitazione di brand famosi (es. *g0ogle* vs *google*).

Il successo della classificazione è dipeso da un'attenta strutturazione del prompt, basata su due pilastri:

### 1. Definizioni Chirurgiche delle Classi
Nel prompt sono state inserite regole precise per guidare il modello:
*   **0 = Traffico Normale** (Domini legittimi, parole di senso compiuto, assenza di anomalie strutturali, anche indirizzi ip, solitamente record A o AAAA)
*   **1 = Tunneling / Data Exfiltration** (LUNGHEZZA ESTREMA. Molto spesso utilizzano record di tipo TXT per trasportare payload codificati. L'attaccante infila i dati rubati in una stringa lunghissima attaccata al dominio base)
*   **2 = Malware DGA** (Stringhe casuali, altissima entropia(non per tutto il dominio, anche per solo un sotto-dominio), lunghezza media/corta, POCHI sottodomini, sembrano ammassi di lettere impronunciabili, non basarti solamente sul dato dell'entropia ma prova a leggere il dominio e a capire se sembra una parola reale o no)
*   **3  = Imposter / Typosquatting** (Domini malevoli che imitano brand, spesso usano caratteri speciali, errori di battitura o sostituzioni di lettere per confondere gli utenti, spesso è in Punycode(xn--))


### 2. Chain of Thought (Ragionamento Sequenziale)
Al fine di migliorare l'accuratezza, è stata implementata la tecnica *Chain of Thought*. Il modello non restituisce solo la classe, ma è obbligato a produrre una breve analisi tecnica (max 2 righe) spiegando come le feature fornite si allineano alle regole.

---

## 🏆 4. Conclusioni

L'LLM rappresenta un'evoluzione fondamentale nei sistemi IDS DNS. Se i modelli di ML basati su alberi (come CatBoost) eccellono per velocità e rigore matematico nel trovare anomalie statistiche, l'LLM aggiunge un livello di **comprensione semantica testuale** imprescindibile per smascherare attacchi di ingegneria sociale e Typosquatting, fornendo al tempo stesso un log human-readable essenziale per gli analisti SOC.

Di seguito è riportata la matrice di confusione che illustra visivamente le performance di classificazione raggiunte dal modello:

![Matrice di Confusione LLM](https://github.com/Nasatti/DNS-IDS-ML-LLM/blob/main/LLM/matrice_confusione_llm.png)
