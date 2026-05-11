import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

# --- CONFIGURAZIONE ---
FILE_CSV = "risultati_llm.csv" 

print(f"Caricamento dati da {FILE_CSV}...")
df = pd.read_csv(FILE_CSV)

colonna_reale = 'attack_tag'
colonna_predetta = 'llm_prediction'

print("\n" + "="*40)
print(" RISULTATI DETTAGLIATI PER CLASSE")
print("="*40)

classi = sorted(df[colonna_reale].unique())

for c in classi:
    totale_classe = len(df[df[colonna_reale] == c])
    giuste = len(df[(df[colonna_reale] == c) & (df[colonna_predetta] == c)])
    sbagliate = totale_classe - giuste
    accuratezza = (giuste / totale_classe) * 100 if totale_classe > 0 else 0
    
    print(f"Classe {c}:")
    print(f"  ➤ Totali analizzate:    {totale_classe}")
    print(f"  ➤ Predizioni GIUSTE:    {giuste}")
    print(f"  ➤ Predizioni SBAGLIATE: {sbagliate}")
    print(f"  ➤ Accuratezza:          {accuratezza:.2f}%\n")

print("="*40)
print(" REPORT DI CLASSIFICAZIONE GLOBALE")
print("="*40)

print(classification_report(df[colonna_reale], df[colonna_predetta], zero_division=0))



etichette_predette = sorted(df[colonna_predetta].unique())
tutte_le_etichette = sorted(list(set(classi) | set(etichette_predette)))

cm = confusion_matrix(df[colonna_reale], df[colonna_predetta], labels=tutte_le_etichette)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=tutte_le_etichette, 
            yticklabels=tutte_le_etichette,
            cbar=False,
            annot_kws={"size": 14}) # Numeri più grandi per la tesi

plt.title('Matrice di Confusione (Modello LLM: gpt-oss:120b)', fontsize=14, pad=15)
plt.ylabel('Classe REALE (Ground Truth)', fontsize=12)
plt.xlabel('Classe PREDETTA (LLM)', fontsize=12)

# Mettiamo una griglia leggera
plt.tight_layout()

nome_immagine = 'matrice_confusione_llm.png'
plt.savefig(nome_immagine, dpi=300)
print(f"\n[OK] Immagine della Matrice di Confusione salvata in: {nome_immagine}")

plt.show()