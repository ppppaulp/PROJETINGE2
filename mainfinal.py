# === rag_rag_with_disease_summary_top3_docteur.py ===
import os
import json
import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

# — Config FAISS & PubMed —
FAISS_INDEX_PATH   = r"index_faiss.idx"
METADATA_IDX_PATH  = r"metadata.json"
PUBMED_JSON_PATH   = r"Pubmed_centralisé_nettoyage1.json"
TOP_K              = 3  # Ne conserver que les 3 articles les plus proches

# — Config Mistral API —
MISTRAL_API_KEY    = "2J3ZRHNEORI1xczjD5QkbtJf2LxkWKeG"
MISTRAL_ENDPOINT   = "https://api.mistral.ai/v1/chat/completions"
HEADERS_MISTRAL    = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

# — Chargement du modèle d'embeddings & de l'index FAISS —
print(" Chargement du modèle d'embeddings…")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
index = faiss.read_index(FAISS_INDEX_PATH)

# — Chargement des articles PubMed —
print(" Chargement du JSON PubMed…")
with open(PUBMED_JSON_PATH, "r", encoding="utf-8") as f:
    full_articles = json.load(f)
articles_by_pmid = { str(a["PMID"]) : a for a in full_articles }


def rechercher(symptomes: str, k: int = TOP_K):
    """Retourne les k articles les plus similaires aux symptômes."""
    q_emb = model.encode([symptomes], convert_to_numpy=True).astype("float32")
    distances, indices = index.search(q_emb, k)
    with open(METADATA_IDX_PATH, "r", encoding="utf-8") as f:
        idx_metadatas = json.load(f)
    pmids = [ str(idx_metadatas[idx].get("PMID", ""))
              for idx in indices[0] if idx < len(idx_metadatas) ]
    return list(zip(pmids, distances[0]))


def summarize_diseases(pmids_with_dist) -> str:
    """
    Construit un prompt en anglais pour que l'IA résume en une phrase les maladies possibles
    et cite les articles (PMID titre et auteur) dont elle se base.
    """
    contenus = []
    for pmid, dist in pmids_with_dist:
        art = articles_by_pmid.get(pmid, {})
        titre = art.get("Title", "Titre introuvable")
        abstract = art.get("Abstract", "")
        contenus.append(f"PMID {pmid} — {titre} : {abstract}")

    prompt = (
        "Vous êtes un médecin expert. À partir des extraits suivants d'articles PubMed, "
        "rédigez **une seule phrase** qui :\n"
        "parler à la première personne, résume les pathologies possibles évoquées, "
        "1. Résume les différentes pathologies possibles évoquées dans ces abstracts.\n"
        "2. Indique pour chaque pathologie les sources (PMID et titre et autheur) utilisées.\n\n"
        + "\n\n".join(contenus)
    )

    payload = {
        "model": "mistral-medium",
        "messages": [
            {"role": "system", "content": "Vous êtes un médecin, clair, professionnel et concis."},
            {"role": "user",   "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.4
    }

    response = requests.post(MISTRAL_ENDPOINT, headers=HEADERS_MISTRAL, json=payload)
    if response.status_code != 200:
        print(f" Erreur Mistral {response.status_code} :", response.text)
        return "— résumé indisponible —"

    return response.json()["choices"][0]["message"]["content"].strip()


def afficher_articles(pmids_with_dist):
    if not pmids_with_dist:
        print(" Aucun article trouvé.")
        return
    print("\n Articles retenus :")
    for pmid, dist in pmids_with_dist:
        art = articles_by_pmid.get(pmid, {})
        titre = art.get('Title', '—')
        auteurs = art.get('Authors', '—')
        print(f"- PMID {pmid} : {titre} | Auteurs : {auteurs} (dist={dist:.3f})")

    print("\n Synthèse médicale :")
    phrase = summarize_diseases(pmids_with_dist)
    print(phrase)

if __name__ == "__main__":
    print("\n Entre tes symptoms en anglais (fever, vomit) ")
    while True:
        query = input(">> symptoms ou q pour quitter : ").strip()
        if query.lower() == 'q':
            print("Merci d'avoir utiliser votre docteur IA j'espère que ça ira mieux!")
            break
        if not query:
            continue
        results = rechercher(query)
        afficher_articles(results)

