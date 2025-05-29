
import pandas as pd
import json
from Bio import Entrez

# Set email
Entrez.email = 'pierreastor25@gmail.com'

# Authors and topics
authors = [""]  # Adjust as needed
topics = ['gastroenterology']

# Date range
date_range = '("2012/03/01"[Date - Create] : "2022/12/31"[Date - Create])'

# Build query
queries = []

if authors:
    author_queries = ['{}[Author]'.format(author) for author in authors]
    queries.append('(' + ' OR '.join(author_queries) + ')')

if topics:
    topic_queries = ['{}[Title/Abstract]'.format(topic) for topic in topics]
    queries.append('(' + ' OR '.join(topic_queries) + ')')

full_query = ' AND '.join(queries) + ' AND ' + date_range

# PubMed search
handle = Entrez.esearch(db='pubmed', retmax=1000, term=full_query)
record = Entrez.read(handle)
id_list = record['IdList']

# List to store results
results = []

for pmid in id_list:
    handle = Entrez.efetch(db='pubmed', id=pmid, retmode='xml')
    records = Entrez.read(handle)

    for record in records['PubmedArticle']:
        title = record['MedlineCitation']['Article']['ArticleTitle']
        abstract = ' '.join(record['MedlineCitation']['Article']['Abstract']['AbstractText']) if 'Abstract' in record['MedlineCitation']['Article'] and 'AbstractText' in record['MedlineCitation']['Article']['Abstract'] else ''
        author_list = record['MedlineCitation']['Article'].get('AuthorList', [])
        if author_list:
            authors_str = ', '.join(
                author.get('LastName', '') + ' ' + author.get('ForeName', '')
                for author in author_list
            )
            affiliations = []
            for author in author_list:
                if 'AffiliationInfo' in author and author['AffiliationInfo']:
                    affiliations.append(author['AffiliationInfo'][0]['Affiliation'])
            affiliations = '; '.join(set(affiliations))
        else:
            authors_str = ''
            affiliations = ''


        journal = record['MedlineCitation']['Article']['Journal']['Title']
        keywords = ', '.join(keyword['DescriptorName'] for keyword in record['MedlineCitation'].get('MeshHeadingList', []))
        url = f"https://www.ncbi.nlm.nih.gov/pubmed/{pmid}"

        results.append({
            'PMID': pmid,
            'Title': title,
            'Abstract': abstract,
            'Authors': authors_str,
            'Journal': journal,
            'Keywords': keywords,
            'URL': url,
            'Affiliations': affiliations
        })

# Save to JSON file
with open('PubMed_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4, ensure_ascii=False)
