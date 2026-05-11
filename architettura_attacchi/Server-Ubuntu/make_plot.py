import json
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime

# Modalità senza monitor per il server
matplotlib.use('Agg')

def genera_grafico(file_path, output_png):
    dataset = []

    try:
        with open(file_path, 'r') as f:
            for riga in f:
                dataset.append(json.loads(riga))

        dataset.sort(key=lambda x: x['ts'])

        tempi = [datetime.fromtimestamp(d['ts']) for d in dataset]
        entropie = [d['features']['entropy'] for d in dataset]
        labels = [d['label'] for d in dataset]

        plt.figure(figsize=(12, 6))
        
        #linea grafico
        plt.plot(tempi, entropie, label='Entropia DNS', color='blue', linewidth=1, alpha=0.8)
        
        #soglia
        plt.axhline(y=4.2, color='red', linestyle='--', label='Soglia Allerta')

        plt.title('Analisi Temporale Ordinata - Demo Tesi')
        plt.xlabel('Tempo')
        plt.ylabel('Entropia')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.savefig(output_png)
        print(f"✅ Grafico ordinato salvato in: {output_png}")

    except Exception as e:
        print(f"❌ Errore durante la generazione: {e}")

if __name__ == "__main__":
    #genera_grafico('archive/session_2/dns_tunnel/analyze_data.json', 'grafico_tesi.png')
    genera_grafico('output_json/analyze_data.json', 'grafico_tesi.png')