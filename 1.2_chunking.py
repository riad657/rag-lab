def chunker(texte, taille_chunk, overlap):
    chunks = []
    debut = 0
    while debut < len(texte):
        fin = debut + taille_chunk
        morceau = texte[debut:fin]
        chunks.append(morceau)
        debut = debut + taille_chunk - overlap
    return chunks

with open("corpus/01_doliprane_clean.txt", "r", encoding="utf-8") as f:
    texte = f.read()

chunks = chunker(texte, taille_chunk=500, overlap=50)

print(f"Nombre total de chunks : {len(chunks)}")
print()
print("--- Chunk 1 ---")
print(chunks[0])
print()
print("--- Chunk 2 ---")
print(chunks[1])
print()
print("--- Chunk 3 ---")
print(chunks[2])
