"""
Smart Literature Miner
Intelligent PubMed mining with rubric-based scoring
"""

import re
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional, Callable

from Bio import Entrez
import chromadb
import chromadb
# from sentence_transformers import SentenceTransformer # Deprecated: Switched to Gemini
# from core.chatbot.gemini_embeddings import GeminiEmbeddings


from config import (
    RUBRIC_CONFIG,
    EMBEDDING_MODEL,
    PUBMED_EMAIL
)
# from core.impact_factors import get_impact_factor, calculate_if_score

try:
    from metapub import PubMedFetcher
    METAPUB_AVAILABLE = True
except ImportError:
    METAPUB_AVAILABLE = False


class SmartMiner:
    """
    Intelligent literature miner for PubMed.
    Scores papers based on: journal quality, recency, data richness, citations
    """

    def __init__(self, email: str = None, log_callback: Optional[Callable] = None):
        """
        Args:
            email: Contact email for PubMed API
            log_callback: Optional callback for logging (called with message string)
        """
        self.email = email or PUBMED_EMAIL
        Entrez.email = self.email
        self.log_callback = log_callback
        self.rubric = RUBRIC_CONFIG

    def _log(self, message: str):
        """Log message via callback if provided"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def mine(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Execute full mining pipeline.

        Args:
            search_term: PubMed search query (already expanded)
            limit: Maximum number of papers to fetch

        Returns:
            List of selected papers with scores and metadata
        """
        self._log(f"🔍 Starting smart mining: searching PubMed...")
        self._log(f"📝 Query: {search_term[:100]}...")

        # 1. Search PubMed for IDs
        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=search_term,
                retmax=limit,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()
            id_list = record["IdList"]

            if not id_list:
                self._log("⚠️ No papers found")
                return []

            self._log(f"✅ Found {len(id_list)} papers")
        except Exception as e:
            self._log(f"❌ Search failed: {e}")
            return []

        # 2. Fetch details
        self._log("📦 Fetching paper details...")
        try:
            handle = Entrez.efetch(
                db="pubmed",
                id=",".join(id_list),
                retmode="xml"
            )
            raw_data = Entrez.read(handle)
            handle.close()
            articles = raw_data.get("PubmedArticle", []) + raw_data.get("PubmedBookArticle", [])
        except Exception as e:
            self._log(f"❌ Fetch failed: {e}")
            return []

        # 3. Get citation counts
        self._log("📊 Fetching citation data...")
        citation_counts = self._get_citations(id_list)

        # 4. Score all papers
        self._log("⚙️ Scoring papers...")
        processed = self._score_papers(articles, citation_counts)

        # 5. Select final papers
        self._log(f"🎯 Selecting final papers based on rubric...")
        final_papers = self._select_final_papers(processed)

        self._log(f"✅ Selected {len(final_papers)} papers")
        return final_papers

    def _get_citations(self, pmid_list: List[str]) -> Dict[str, int]:
        """Get citation counts via elink"""
        citation_counts = {}
        try:
            handle = Entrez.elink(
                dbfrom="pubmed",
                db="pubmed",
                linkname="pubmed_pubmed_citedin",
                id=",".join(pmid_list)
            )
            linksets = Entrez.read(handle)
            handle.close()

            for ls in linksets:
                src_list = ls.get("IdList", [])
                if not src_list:
                    continue
                src_pmid = str(src_list[0])
                count = 0
                for ldb in ls.get("LinkSetDb", []):
                    if ldb.get("LinkName") == "pubmed_pubmed_citedin":
                        count += len(ldb.get("Link", []))
                citation_counts[src_pmid] = count
        except Exception:
            pass

        return citation_counts

    def _extract_abstract(self, article: Dict[str, Any]) -> str:
        """Extract abstract text from article structure"""
        try:
            abstract_data = (
                article["MedlineCitation"]["Article"]
                .get("Abstract", {})
                .get("AbstractText", [])
            )
            if not abstract_data:
                return ""

            if isinstance(abstract_data, list):
                text_parts = []
                for item in abstract_data:
                    if hasattr(item, "attributes") and "Label" in item.attributes:
                        text_parts.append(f"{item.attributes['Label']}: {str(item)}")
                    else:
                        text_parts.append(str(item))
                return " ".join(text_parts)
            return str(abstract_data)
        except Exception:
            return ""

    def _score_papers(self, articles: List[Dict], citation_counts: Dict[str, int]) -> List[Dict[str, Any]]:
        """Score all papers and return processed list"""
        processed = []

        for article in articles:
            try:
                pmid = str(article["MedlineCitation"]["PMID"])
                article_core = article["MedlineCitation"]["Article"]
                title = article_core.get("ArticleTitle", "No Title")
                abstract = self._extract_abstract(article)

                if not abstract:
                    continue

                # ⚠️ Quality Assurance 1: Check for retraction
                is_retracted = self._check_retraction_status(article)
                if is_retracted:
                    self._log(f"⚠️  Skipping retracted paper: {title[:50]}...")
                    continue  # Skip retracted papers entirely

                # Calculate base score
                score, journal, year, reasons, is_review = self._calculate_score(article)

                # 🔬 Quality Assurance 2: Impact Factor bonus
                from core.impact_factors import get_impact_factor, calculate_if_score
                impact_factor = get_impact_factor(journal)
                if impact_factor > 0:
                    if_score = calculate_if_score(impact_factor)
                    if if_score > 0:
                        score += if_score
                        reasons.append(f"IF={impact_factor}(+{if_score})")

                # 📄 Quality Assurance 3: Preprint marking
                is_preprint = self._check_preprint(journal)
                if is_preprint:
                    score = int(score * 0.5)  # 50% penalty for preprints
                    reasons.append("preprint(-50%)")

                # Data quality bonus
                bone_vals = re.findall(r"(\d+\.?\d*)\s?mm", abstract)
                if bone_vals:
                    score += self.rubric["data_quality_bonus"]
                    reasons.append(f"data(+{self.rubric['data_quality_bonus']})")

                # Citation bonus
                citations = citation_counts.get(pmid, 0)
                if citations > 0:
                    cite_score = self._get_citation_score(citations)
                    if cite_score > 0:
                        score += cite_score
                        reasons.append(f"cited(+{cite_score})")

                # Extract DOI if available
                doi = ""
                try:
                    article_ids = article.get("PubmedData", {}).get("ArticleIdList", [])
                    for aid in article_ids:
                        if hasattr(aid, "attributes") and aid.attributes.get("IdType") == "doi":
                            doi = str(aid)
                            break
                except Exception:
                    pass

                processed.append({
                    "id": pmid,
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "year": year,
                    "score": score,
                    "is_review": is_review,
                    "is_preprint": is_preprint,
                    "impact_factor": impact_factor,
                    "citations": citations,
                    "doi": doi,
                    "reasons": ", ".join(reasons) if reasons else "base"
                })
            except Exception:
                continue

        return processed

    def _calculate_score(self, article: Dict[str, Any]) -> Tuple[int, str, int, List[str], bool]:
        """Calculate base score for one paper"""
        score = 1
        reasons = []

        # Journal
        journal = "Unknown"
        try:
            journal = article["MedlineCitation"]["Article"]["Journal"].get("Title", "Unknown")
        except Exception:
            pass

        for name, points in self.rubric["top_journals"].items():
            if name.lower() in journal.lower():
                score += points
                reasons.append(f"journal(+{points})")
                break

        # Year
        year = 2020
        try:
            pub_date = article["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"]
            if "Year" in pub_date:
                year = int(pub_date["Year"])
            elif "MedlineDate" in pub_date:
                found = re.search(r"\d{4}", pub_date["MedlineDate"])
                if found:
                    year = int(found.group())

            gap = datetime.now().year - year
            year_score = max(0, self.rubric["recency_max_score"] - gap)
            if year_score > 0:
                score += year_score
                reasons.append(f"recent(+{year_score})")
        except Exception:
            pass

        # Review check
        is_review = False
        try:
            pub_types = article["MedlineCitation"]["Article"].get("PublicationTypeList", [])
            for pt in pub_types:
                if "review" in str(pt).lower():
                    is_review = True
                    reasons.append("review")
                    break
        except Exception:
            pass

        return score, journal, year, reasons, is_review

    def _check_retraction_status(self, article: Dict[str, Any]) -> bool:
        """
        Check if paper has been retracted

        PubMed marks retracted papers in PublicationTypeList
        """
        try:
            pub_types = article["MedlineCitation"]["Article"].get("PublicationTypeList", [])
            for pt in pub_types:
                pt_str = str(pt).lower()
                if "retract" in pt_str:
                    return True

            # Also check in Comments/Corrections
            comments = article.get("MedlineCitation", {}).get("CommentsCorrectionsList", [])
            for comment in comments:
                if hasattr(comment, "attributes"):
                    ref_type = comment.attributes.get("RefType", "")
                    if ref_type in ["RetractionIn", "RetractionOf"]:
                        return True

            return False
        except Exception:
            return False

    def _check_preprint(self, journal: str) -> bool:
        """
        Check if paper is from a preprint server

        Preprint servers: bioRxiv, medRxiv, arXiv, etc.
        """
        if not journal:
            return False

        journal_lower = journal.lower()
        preprint_servers = ["biorxiv", "medrxiv", "arxiv", "ssrn", "preprint"]

        return any(server in journal_lower for server in preprint_servers)

    def _get_citation_score(self, count: int) -> int:
        """Calculate citation score"""
        for threshold, points in sorted(self.rubric["citation_rules"], reverse=True):
            if count >= threshold:
                return points
        return 0

    def _select_final_papers(self, processed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Select final papers based on strategy"""
        if not processed:
            return []
        
        current_year = datetime.now().year
        selected = []
        selected_ids = set()
        
        # 1. Top 2 reviews
        reviews = [p for p in processed if p.get("is_review")]
        reviews.sort(key=lambda x: x["score"], reverse=True)
        for p in reviews[:2]:
            p = dict(p)
            p["category"] = "high_impact"
            selected.append(p)
            selected_ids.add(p["id"])
        
        # 2. Recent papers from top journals (4)
        def in_top_journal(journal: str) -> bool:
            j_lower = journal.lower()
            return any(name.lower() in j_lower for name in self.rubric["top_journals"].keys())
        
        recent_top = [
            p for p in processed
            if not p.get("is_review")
            and p["id"] not in selected_ids
            and p.get("year", 0) >= current_year - 1
            and in_top_journal(p.get("journal", ""))
        ]
        recent_top.sort(key=lambda x: (x.get("year", 0), x["score"]), reverse=True)
        for p in recent_top[:4]:
            p = dict(p)
            p["category"] = "recent"
            selected.append(p)
            selected_ids.add(p["id"])
        
        # 3. Top scored studies (4)  
        remaining = [p for p in processed if not p.get("is_review") and p["id"] not in selected_ids]
        remaining.sort(key=lambda x: x["score"], reverse=True)
        for p in remaining[:4]:
            p = dict(p)
            p["category"] = "data_rich"
            selected.append(p)
            selected_ids.add(p["id"])
        
        return selected


class PersistentMemory:
    """
    Vector database for storing and querying paper abstracts
    """
    
    def __init__(self, db_name: str, data_dir: str):
        """
        Args:
            db_name: Collection name (use slug from query)
            data_dir: Directory path for ChromaDB storage
        """
        self.client = chromadb.PersistentClient(path=data_dir)
        # self.embedding_fn = SentenceTransformer(EMBEDDING_MODEL)
        from core.chatbot.gemini_embeddings import GeminiEmbeddings
        self.embeddings = GeminiEmbeddings()
        self.collection = self.client.get_or_create_collection(name=db_name)
        
        # Check and migrate if dimensions don't match (legacy 384 -> gemini 768)
        self._migrate_if_needed(db_name)

    def _migrate_if_needed(self, db_name: str, force: bool = False):
        """Check embedding dimension and migrate if mismatch"""
        try:
            # Peek to check dimension unless forced
            if not force:
                peek = self.collection.peek(limit=1)
                if not peek or not peek["embeddings"]:
                    return
                
                curr_dim = len(peek["embeddings"][0])
                expected_dim = 768 # Gemini text-embedding-004
                if curr_dim == expected_dim:
                    return

            print(f"⚠️ Vector DB dimension mismatch or forced migration. Migrating...")

            # Fetch all existing data
            all_data = self.collection.get()
            if not all_data["ids"]:
                return
            
            print(f"📦 Migrating {len(all_data['ids'])} documents...")
            ids = all_data["ids"]
            docs = all_data["documents"]
            metas = all_data["metadatas"]
            
            # Delete old collection
            self.client.delete_collection(name=db_name)
            
            # Create new
            self.collection = self.client.create_collection(name=db_name)
            
            # Re-embed and add
            new_embeddings = self.embeddings.embed_documents(docs)
            self.collection.add(
                ids=ids,
                embeddings=new_embeddings,
                documents=docs,
                metadatas=metas
            )
            print("✅ Migration complete!")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")

    def _force_migration(self):
        """Force migration of current collection"""
        self._migrate_if_needed(self.collection.name, force=True)




    
    def add_papers(self, papers: List[Dict[str, Any]]):
        """Add papers to vector database"""
        if not papers:
            return
        
        ids_to_add = []
        docs_to_add = []
        metas_to_add = []
        
        for p in papers:
            ids_to_add.append(p["id"])
            docs_to_add.append(p["abstract"])
            # Remove abstract from metadata
            metas_to_add.append({k: v for k, v in p.items() if k != "abstract"})
        
        # Check existing
        existing = self.collection.get(ids=ids_to_add)
        existing_ids = set(existing["ids"])
        
        # Filter new papers
        final_ids = []
        final_docs = []
        final_metas = []
        
        for i, pid in enumerate(ids_to_add):
            if pid not in existing_ids:
                final_ids.append(pid)
                final_docs.append(docs_to_add[i])
                final_metas.append(metas_to_add[i])
        
        # Add to database
        if final_ids:
            # embeddings = self.embedding_fn.encode(final_docs).tolist()
            embeddings = self.embeddings.embed_documents(final_docs)
            try:
                self.collection.add(
                    ids=final_ids,
                    embeddings=embeddings,
                    documents=final_docs,
                    metadatas=final_metas
                )
            except Exception as e:
                if "dimension" in str(e).lower():
                    print(f"⚠️ Dimension mismatch detected during add: {e}")
                    self._force_migration()
                    # Retry add
                    self.collection.add(
                        ids=final_ids,
                        embeddings=embeddings,
                        documents=final_docs,
                        metadatas=final_metas
                    )
                else:
                    raise e

    
    def query(self, topic: str, n: int = 20) -> Dict[str, Any]:
        """
        Query for relevant papers.
        
        Args:
            topic: Search topic (can be different from original query)
            n: Number of results to return
            
        Returns:
            ChromaDB query results with ids, distances, metadatas, documents
        """
        # q_vec = self.embedding_fn.encode([topic]).tolist()
        q_vec = self.embeddings.embed_query(topic)
        try:
            results = self.collection.query(query_embeddings=[q_vec], n_results=n)
        except Exception as e:
            if "dimension" in str(e).lower():
                print(f"⚠️ Dimension mismatch detected during query: {e}")
                self._force_migration()
                # Retry query
                results = self.collection.query(query_embeddings=[q_vec], n_results=n)
            else:
                raise e
        return results


