import json
import numpy as np
import faiss
import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer

# 1. Télécharge les deux ressources NLTK nécessaires
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# 2. Chargement du JSON d'articles
with open(r"Pubmed_centralisé_nettoyage1.json", encoding="utf-8") as f:
    articles = json.load(f)

# 3. Fonction de découpage en chunks de max 5 phrases
def chunk_text(text, max_sentences=5):
    sentences = sent_tokenize(text)
    return [
        " ".join(sentences[i : i + max_sentences])
        for i in range(0, len(sentences), max_sentences)
    ]

# 4. Préparation des chunks et des métadonnées
chunks = []
metadata = []

for article in articles:
    pmid = article.get("PMID")
    title = article.get("Title")
    abstract = article.get("Abstract", "")
    if abstract:
        article_chunks = chunk_text(abstract)
        chunks.extend(article_chunks)
        metadata.extend(
            [{"PMID": pmid, "Title": title, "Chunk": chunk} for chunk in article_chunks]
        )

# 5. Calcul des embeddings avec SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks, show_progress_bar=True)

# 6. Création et remplissage de l’index FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings, dtype="float32"))

# 7. Sauvegarde de l’index et des métadonnées
faiss.write_index(index, "index_faiss.idx")
with open("metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("✅ Index FAISS et métadonnées créés avec succès.")
