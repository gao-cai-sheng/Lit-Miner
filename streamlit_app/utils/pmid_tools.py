"""
PMID Lookup Tools
Quick information retrieval from PubMed
"""

from typing import Dict
from Bio import Entrez
from config import PUBMED_EMAIL


def lookup_pmid(pmid: str) -> Dict:
    """
    Look up PMID and return DOI, title, and links.
    
    Args:
        pmid: PubMed ID
        
    Returns:
        Dict with doi, title, abstract, journal, year, and URLs
    """
    Entrez.email = PUBMED_EMAIL
    
    try:
        # Fetch from PubMed
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        records = Entrez.read(handle)
        handle.close()
        
        if not records or 'PubmedArticle' not in records:
            raise ValueError(f"No results found for PMID {pmid}")
        
        article = records['PubmedArticle'][0]
        medline = article['MedlineCitation']
        article_data = medline['Article']
        
        # Extract title
        title = article_data.get('ArticleTitle', 'No title')
        
        # Extract abstract
        abstract_data = article_data.get('Abstract', {}).get('AbstractText', [])
        if isinstance(abstract_data, list):
            abstract = ' '.join(str(item) for item in abstract_data)
        else:
            abstract = str(abstract_data) if abstract_data else 'No abstract available'
        
        # Extract journal and year
        journal = article_data.get('Journal', {}).get('Title', 'Unknown')
        pub_date = article_data.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
        year = pub_date.get('Year', 'Unknown')
        
        # Extract DOI
        article_ids = article.get('PubmedData', {}).get('ArticleIdList', [])
        doi = ""
        for aid in article_ids:
            if hasattr(aid, 'attributes') and aid.attributes.get('IdType') == 'doi':
                doi = str(aid)
                break
        
        # Generate URLs
        pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        doi_url = f"https://doi.org/{doi}" if doi else ""
        scihub_url = f"https://sci-hub.se/{doi}" if doi else ""
        
        return {
            'pmid': pmid,
            'doi': doi if doi else "Not available",
            'title': title,
            'abstract': abstract,
            'journal': journal,
            'year': year,
            'pubmed_url': pubmed_url,
            'doi_url': doi_url,
            'scihub_url': scihub_url
        }
        
    except Exception as e:
        raise Exception(f"Failed to lookup PMID {pmid}: {str(e)}")
