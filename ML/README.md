# 🧠 Machine Learning: Analisi Avanzata del Traffico DNS per la Rilevazione di Minacce

Questa directory contiene il Jupyter Notebook per l'addestramento e la valutazione dei modelli di Machine Learning. L'obiettivo principale di questa sezione è **confrontare l'efficacia di diverse architetture algoritmiche nel distinguere il traffico DNS legittimo da tre vettori di attacco critici**, trattando il problema come un task di classificazione multiclasse.

---

## 🎯 1. Classificazione e Definizione delle Minacce

Il modello è stato istruito per riconoscere e categorizzare le query DNS in quattro classi distinte:
*   **Classe 0 (Normal):** Query legittime, che sono state attivamente filtrate e validate per assicurare l'effettiva vitalità del dominio tramite la risoluzione IP.
*   **Classe 1 (Tunneling):** Simulazione di attacchi di esfiltrazione dati sfruttando domini specifici configurati per il test (es. *sandbox.alphasoc.xyz*).
*   **Classe 2 (DGA):** Domini generati algoritmicamente (Domain Generation Algorithms), tipici dei ceppi di malware per stabilire connessioni C2 evadendo le blacklist statiche.
*   **Classe 3 (Imposter):** Domini utilizzati in attacchi di typosquatting o attacchi omografi, spesso basati sulla codifica Punycode (riconoscibile dal prefisso *xn--*).

---

## 🧹 2. Preprocessing e Feature Engineering

Il dataset originale è stato costruito partendo dai log JSON catturati dall'infrastruttura di rete (Zeek). Tramite Pandas su Jupyter, i dati sono stati appiattiti e normalizzati, applicando le seguenti fasi:

1.  **Deduplicazione e Bilanciamento:** Le query duplicate sono state rimosse, portando il dataset **da 30.521 a 20.155 righe uniche**. Successivamente, è stato effettuato un campionamento rappresentativo per bilanciare le classi ed evitare bias nei modelli.
2.  **Data Split:** Il dataset finale è stato diviso seguendo rigorosamente le proporzioni **70% per il Training, 15% per la Validation (utile per l'early stopping) e 15% per il Test**, stratificando le variabili target.
3.  **Labeling:** Sono state assegnate le etichette numeriche (0, 1, 2, 3) a seconda del tipo di traffico.

### Le Feature Matematiche
Per permettere ai modelli di analizzare la struttura della query, sono state estratte le seguenti feature matematiche:

| Feature | Descrizione |
| :--- | :--- |
| `len` | Lunghezza totale della query (valori estremamente alti indicano potenziale Tunneling). |
| `entropy` | Entropia di Shannon calcolata sulla stringa (indicatore chiave di elevata casualità nei DGA). |
| `sub_count` | Numero totale di livelli di sottodominio presenti. |
| `qtype` | Tipo di record DNS richiesto (es. A, AAAA, TXT). Questa feature è stata determinante per isolare e identificare il Tunneling. |
| `max_cons` | La sequenza più lunga di consonanti consecutive. |

---

## 🤖 3. Modelli Addestrati

Sono state implementate e addestrate tre diverse architetture di Machine Learning per valutare differenti approcci:

*   **Random Forest:** Un modello *ensemble* robusto, configurato con 100 alberi di decisione.
*   **CatBoost:** Un potente algoritmo di Gradient Boosting ottimizzato specificamente per la gestione nativa delle feature categoriche (come il `qtype`) e testuali, che include meccanismi di protezione dall'overfitting come l'early stopping.
*   **MLP (Multi-Layer Perceptron):** Una rete neurale artificiale profonda configurata con due livelli nascosti (64 e 32 neuroni) a cui è stata applicata una standardizzazione preventiva delle feature.

---

## 📊 4. Risultati e Metriche

Tutti i modelli hanno dimostrato performance eccellenti, raggiungendo un'**accuratezza complessiva del 94%**. Di seguito si riporta il *classification report* ottenuto sul Test Set dai modelli migliori (CatBoost e MLP):

| Classe | Precision | Recall | F1-Score |
| :--- | :--- | :--- | :--- |
| **0 (Normal)** | 0.92 | 0.84 | 0.88 |
| **1 (Tunneling)** | **1.00** | **1.00** | **1.00** |
| **2 (DGA)** | 0.99 | 0.99 | 0.99 |
| **3 (Imposter)** | 0.86 | 0.94 | 0.90 |

### Considerazioni Finali e Importanza delle Feature
L'analisi dell'importanza delle variabili ha dimostrato che **`sub_count`, `len` ed `entropy` rappresentano i driver principali** per il rilevamento delle minacce.
*   **Tunneling (1.00 F1-Score):** L'integrazione del parametro `qtype` ha permesso di risolvere completamente ogni ambiguità relativa all'esfiltrazione dati, garantendo una perfezione statistica nel suo riconoscimento.
*   **DGA (0.99 F1-Score):** L'utilizzo congiunto di entropia e lunghezza rende i domini algoritmici quasi immediatamente individuabili per i modelli ad albero.
*   **Limiti (Normal vs Imposter):** La sfida più complessa per i modelli basati puramente sulla statistica matematica risiede nel separare il traffico Normal dagli attacchi Imposter (Typosquatting). La loro estrema somiglianza strutturale (lunghezza ed entropia simili) causa un leggero aumento dei falsi positivi, dimostrando la necessità di affiancare tecniche di analisi semantica più avanzate (come l'utilizzo dei Large Language Models).
