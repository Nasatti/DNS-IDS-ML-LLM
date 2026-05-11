#!/bin/bash

# --- CONFIGURAZIONE ---
PROJECT_DIR=$(pwd)
LOG_DIR="./logs"
PCAP_DIR="./pcaps"
JSON_DIR="./output_json"
MONGO_DATA="./mongo_data"

echo "🚀 Avvio procedura di Reset e Riavvio Sistema..."

# 1. Fase di Pulizia
echo "🧹 [1/4] Pulizia in corso..."
sudo docker compose down
tmux kill-server 2>/dev/null
sudo rm -rf $LOG_DIR/*.log
sudo rm -rf $PCAP_DIR/*.pcap
sudo rm -rf $JSON_DIR/*.json

# 2. Reset MongoDB
echo "🗄️ [2/4] Reset del database MongoDB..."
sudo rm -rf $MONGO_DATA
mkdir $MONGO_DATA
sudo chmod 777 $MONGO_DATA

# 3. Riavvio Docker
echo "🐳 [3/4] Avvio container Docker..."
sudo docker compose up -d

# Fondamentale: attendere che MongoDB sia pronto per le connessioni
echo "⏳ Attesa inizializzazione MongoDB (15 secondi)..."
sleep 15

# 4. Avvio Pipeline Python in Tmux
echo "🐍 [4/4] Avvio sessioni di analisi Python..."

# Sessione Ingestor
tmux new-session -d -s ingestor "cd $PROJECT_DIR && source venv/bin/activate && python3 ingestor.py; read"
echo "  > Ingestor avviato in tmux"

# Sessione Analyzer
tmux new-session -d -s analyzer "cd $PROJECT_DIR && source venv/bin/activate && python3 analyzer.py; read"
echo "  > Analyzer avviato in tmux"

# Sessione Detector
tmux new-session -d -s detector "cd $PROJECT_DIR && source venv/bin/activate && python3 detector.py; read"
echo "  > Detector avviato in tmux"

echo "------------------------------------------------"
echo "✅ Sistema pronto! Stato attuale:"
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
tmux ls
echo "------------------------------------------------"
