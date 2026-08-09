def recomendar_tamanho(altura_cm, peso_kg):
    if altura_cm < 160 and peso_kg < 60:
        return "P"
    elif altura_cm < 170 and peso_kg < 70:
        return "M"
    elif altura_cm < 180 and peso_kg < 80:
        return "G"
    else:
        return "GG"