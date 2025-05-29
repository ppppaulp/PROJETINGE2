# Assistant Médical Intelligent pour le Diagnostic

Ce projet est un prototype d'assistant médical basé sur des techniques de NLP et de RAG (Retrieval-Augmented Generation), combinant des embeddings sémantiques, la recherche d'articles scientifiques PubMed et une synthèse via un modèle de langage (LLM).

---

##  Fonctionnalités

- Extraction des maladies possibles à partir de symptômes en langage naturel.
- Recherche sémantique dans un corpus d’articles médicaux issus de PubMed.
- Résumé automatique des pathologies probables avec mention des sources (PMID, titre, auteurs).
- Interface console interactive.
- Compte rendu effectuer par une IA pour aider à la compréhension du
---

##  Technologies utilisées

- LLM & RAG : Résumé médical assisté par un modèle Mistral.
- Embeddings : Sentence-Transformers (`all-MiniLM-L6-v2`)
- Vector Search : Index FAISS
- Dataset : Articles scientifiques issus de PubMed, pré-nettoyés au format JSON.
- NLP : NLTK pour le découpage en phrases.

---

##  Structure des fichiers

- `mainfinal.py` : Script principal pour interagir avec l'utilisateur.
- `document_store.py` : Construction de l’index FAISS à partir des articles.
- `pubmed_json.py` : Téléchargement des articles depuis PubMed.
- `Pubmed_centralisé_nettoyage1.json` : Données sources utilisées pour la recherche.
- `index_faiss.idx` & `metadata.json` : Index vectoriel et métadonnées associées.
- `exploration_donnees_medicales.ipynb` : Analyse exploratoire des données PubMed.

---

##  Dépendances

Installe toutes les dépendances via :

pip install -r requirements.txt

---

##  Exécution

1. Télécharger les articles depuis PubMed :

python pubmed_json.py

puis on centralise les données à la main pour avoir Pubmed_centralisé


2. Le fichier `exploration_donnees_medicales.ipynb` permet d'explorer et de mieux comprendre le corpus PubMed utilisé.

Ce notebook sert donc à préparer et valider les données avant indexation



3. Créer l’index FAISS :

python document_store.py


3. Lancer le chatbot médical :

python mainfinal.py


4. Entrer des symptômes en anglais :

>> fever, cough, rash


---

##  Remarques

- Vérifier que les codes d'accès PubMedAPI sont valide dans PubMed_Result.
- La clé API Mistral doit être valide dans le fichier `mainfinal.py`.
- Le fichier `Pubmed_centralisé_nettoyage1.json` est attendu dans le même dossier.
- Le script `pubmed_json.py` permet de récupérer les articles au format brut depuis PubMed, mais **le passage de ce format brut au format centralisé (`Pubmed_centralisé_nettoyage1.json`) se fait manuellement** à cette étape.

---
