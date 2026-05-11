import math
from collections import Counter

# Shennon Entropy
def shannon_entropy(s):
    if not s or s == "-": return 0
    p = [float(v)/len(s) for v in Counter(s).values()]
    return round(-sum(pi * math.log2(pi) for pi in p), 3)

# DGA
# length : lunghezza dominio
# digit_p: percentuale di numeri presenti nel dominio (circa 0 | > 0.20)
# alpha_p: Indica la percentuale di lettere (circa 1 | < 0.50)
# vowel_p: percentuale di vocali (circa 0.4 | < 0.2)
# special_p: Indica la percentuale di simboli, no punti ( circa 0 | > 0.1)
# subdomain_count: numero di sottodomini (conteggio dei punti)
# max_cons: lunghezza massima di consonanti consecutive (circa 3 | > 5)
def get_string_metrics(s):
    if not s or s == "-": return 0, 0, 0, 0, 0, 0, 0

    length = len(s)
    clean_s = s.replace(".", "")
    c_len = len(clean_s) if len(clean_s) > 0 else 1

    subdomain_count = s.count(".")

    digit_p = round(sum(c.isdigit() for c in clean_s) / c_len, 3) 
    alpha_p = round(sum(c.isalpha() for c in clean_s) / c_len, 3)
    special_p = round((c_len - sum(c.isalnum() for c in clean_s)) / c_len, 3)

    vowels = "aeiou"
    vowel_p = round(sum(c.lower() in vowels for c in clean_s) / c_len, 3)
    
    consonants = "bcdfghjklmnpqrstvwxyz"
    max_cons = 0
    current_cons = 0
    for char in s.lower():
        if char in consonants:
            current_cons += 1
            max_cons = max(max_cons, current_cons)
        else:
            current_cons = 0

    return length, digit_p, alpha_p, vowel_p, special_p, subdomain_count, max_cons