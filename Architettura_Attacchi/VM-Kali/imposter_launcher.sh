while read -r domain; do
    dig +short "$domain" @192.168.1.33
    sleep 0.1
done < dns_data/imposter_5k_bilanciato.txt
