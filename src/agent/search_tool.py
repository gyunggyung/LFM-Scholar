import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Paper:
    """Represents a scientific paper."""
    paper_id: str
    title: str
    authors: List[str]
    year: Optional[int]
    citation_count: int
    doi: Optional[str]
    arxiv_id: Optional[str]
    abstract: Optional[str]

    def to_dict(self) -> Dict:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "citation_count": self.citation_count,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "abstract": self.abstract
        }

class PaperSearcher:
    """Search for academic papers using Semantic Scholar API with OpenAlex and arXiv fallback."""

    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.openalex_url = "https://api.openalex.org"
        self.arxiv_url = "http://export.arxiv.org/api/query"
        self.session = requests.Session()
        self.email = email or "lfm-citeagent@example.com"  # OpenAlex polite pool
        headers = {
            "User-Agent": "LFM-CiteAgent/0.1.0"
        }
        if api_key:
            headers["x-api-key"] = api_key
        self.session.headers.update(headers)

    def search_papers(self, query: str, limit: int = 5, min_citations: int = 10) -> List[Paper]:
        """
        Search papers with fallback strategy:
        1. Semantic Scholar API (best quality, citation data)
        2. OpenAlex API (no rate limit, good coverage)
        3. arXiv API (latest preprints, real-time)
        """
        print(f"\n[Search] Query: '{query}'")
        
        # Step 1: Try Semantic Scholar first
        papers = self._search_semantic_scholar(query, limit, min_citations)
        if papers:
            print(f"[Search] Found {len(papers)} papers via Semantic Scholar.")
            return papers
        
        # Step 2: Fallback to OpenAlex
        print("[Search] Switching to OpenAlex API...")
        papers = self._search_openalex(query, limit, min_citations)
        if papers:
            print(f"[Search] Found {len(papers)} papers via OpenAlex.")
            return papers
        
        # Step 3: Try arXiv for latest preprints (no citation filter)
        print("[Search] Switching to arXiv API (latest preprints)...")
        papers = self._search_arxiv(query, limit)
        if papers:
            print(f"[Search] Found {len(papers)} papers via arXiv.")
            return papers
        
        # Step 4: Last resort - inform user and return empty
        print("[Search] ⚠️ No relevant papers found from any API.")
        print("[Search] Consider refining your search query or trying again later.")
        return []  # Return empty instead of silent fallback

    def _search_semantic_scholar(self, query: str, limit: int, min_citations: int) -> List[Paper]:
        """Search using Semantic Scholar API."""
        try:
            url = f"{self.base_url}/paper/search"
            params = {
                "query": query,
                "limit": limit * 2, 
                "fields": "title,authors,year,citationCount,paperId,externalIds,abstract"
            }
            
            # Retry logic with exponential backoff
            max_retries = 3
            for i in range(max_retries):
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 429:
                    wait_time = (i + 1) * 2
                    print(f"[Search] Semantic Scholar rate limit. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                break
            
            # If rate limit persists after retries, return empty to trigger OpenAlex
            if response.status_code == 429:
                print("[Search] Semantic Scholar rate limit exceeded after retries.")
                return []
                
            if response.status_code != 200:
                print(f"[Search] Semantic Scholar error: {response.status_code}")
                return []

            data = response.json()
            
            papers = []
            if "data" not in data:
                return []
                
            for item in data["data"]:
                if item.get("citationCount", 0) < min_citations:
                    continue
                    
                authors = [a.get("name", "Unknown") for a in item.get("authors", [])]
                ext_ids = item.get("externalIds", {})
                
                paper = Paper(
                    paper_id=item.get("paperId", ""),
                    title=item.get("title", "Unknown"),
                    authors=authors,
                    year=item.get("year"),
                    citation_count=item.get("citationCount", 0),
                    doi=ext_ids.get("DOI"),
                    arxiv_id=ext_ids.get("ArXiv"),
                    abstract=item.get("abstract", "")
                )
                papers.append(paper)
                
                if len(papers) >= limit:
                    break
                    
            return papers
            
        except Exception as e:
            print(f"[Search] Semantic Scholar error: {e}")
            return []

    def _search_openalex(self, query: str, limit: int, min_citations: int) -> List[Paper]:
        """Search using OpenAlex API (no rate limit, polite pool)."""
        try:
            url = f"{self.openalex_url}/works"
            
            # Build params - filter by citations if specified
            params = {
                "search": query,
                "per_page": limit * 2,
                "mailto": self.email,  # Polite pool for faster responses
                "select": "id,title,authorships,publication_year,cited_by_count,doi,open_access,abstract_inverted_index"
            }
            
            # Only add citation filter if min_citations > 0
            if min_citations > 0:
                params["filter"] = f"cited_by_count:>{min_citations}"
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"[Search] OpenAlex error: {response.status_code}")
                return []
            
            data = response.json()
            
            papers = []
            results = data.get("results", [])
            
            # If no results with citation filter, retry without it
            if not results and min_citations > 0:
                print(f"[Search] No results with min_citations={min_citations}, retrying without filter...")
                params.pop("filter", None)
                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
            
            for item in results:
                # Extract authors
                authors = []
                for authorship in item.get("authorships", []):
                    author_info = authorship.get("author", {})
                    name = author_info.get("display_name", "Unknown")
                    authors.append(name)
                
                # Reconstruct abstract from inverted index
                abstract = self._reconstruct_abstract(item.get("abstract_inverted_index"))
                
                # Extract DOI and arXiv ID
                doi = item.get("doi", "").replace("https://doi.org/", "") if item.get("doi") else None
                arxiv_id = None
                openalex_id = item.get("id", "").replace("https://openalex.org/", "")
                
                paper = Paper(
                    paper_id=openalex_id,
                    title=item.get("title", "Unknown"),
                    authors=authors[:5],  # Limit authors
                    year=item.get("publication_year"),
                    citation_count=item.get("cited_by_count", 0),
                    doi=doi,
                    arxiv_id=arxiv_id,
                    abstract=abstract
                )
                papers.append(paper)
                
                if len(papers) >= limit:
                    break
            
            return papers
            
        except Exception as e:
            print(f"[Search] OpenAlex error: {e}")
            return []

    def _reconstruct_abstract(self, inverted_index: Optional[Dict]) -> str:
        """Reconstruct abstract text from OpenAlex inverted index format."""
        if not inverted_index:
            return ""
        
        try:
            # Build word position list
            word_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            
            # Sort by position and join
            word_positions.sort(key=lambda x: x[0])
            abstract = " ".join([wp[1] for wp in word_positions])
            return abstract[:1000]  # Limit length
        except Exception:
            return ""

    def _search_arxiv(self, query: str, limit: int) -> List[Paper]:
        """Search using arXiv API (latest preprints, real-time index)."""
        try:
            import xml.etree.ElementTree as ET
            
            # arXiv API uses Atom format
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": limit * 2,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            response = self.session.get(self.arxiv_url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"[Search] arXiv error: {response.status_code}")
                return []
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Define namespaces
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            papers = []
            for entry in root.findall('atom:entry', ns):
                # Extract title
                title_elem = entry.find('atom:title', ns)
                title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else "Unknown"
                
                # Extract authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name_elem = author.find('atom:name', ns)
                    if name_elem is not None:
                        authors.append(name_elem.text)
                
                # Extract abstract
                summary_elem = entry.find('atom:summary', ns)
                abstract = summary_elem.text.strip().replace('\n', ' ')[:1000] if summary_elem is not None else ""
                
                # Extract arXiv ID from the id URL
                id_elem = entry.find('atom:id', ns)
                arxiv_id = ""
                if id_elem is not None:
                    # Format: http://arxiv.org/abs/2512.20491v1
                    arxiv_id = id_elem.text.split('/abs/')[-1].split('v')[0] if '/abs/' in id_elem.text else ""
                
                # Extract year from published date
                published_elem = entry.find('atom:published', ns)
                year = None
                if published_elem is not None:
                    year = int(published_elem.text[:4])
                
                # Extract DOI if available
                doi = None
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'doi':
                        doi = link.get('href', '').replace('http://dx.doi.org/', '')
                
                paper = Paper(
                    paper_id=f"arxiv:{arxiv_id}",
                    title=title,
                    authors=authors[:5],  # Limit authors
                    year=year,
                    citation_count=0,  # arXiv doesn't provide citation count
                    doi=doi,
                    arxiv_id=arxiv_id,
                    abstract=abstract
                )
                papers.append(paper)
                
                if len(papers) >= limit:
                    break
            
            return papers
            
        except Exception as e:
            print(f"[Search] arXiv error: {e}")
            return []

    def _get_fallback_papers(self, query: str) -> List[Paper]:
        # Simple mock data for demo (Transformer classics)
        return [
            Paper(
                paper_id="mock1",
                title="Attention Is All You Need",
                authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
                year=2017,
                citation_count=100000,
                doi=None,
                arxiv_id="1706.03762",
                abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
            ),
            Paper(
                paper_id="mock2",
                title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                authors=["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
                year=2018,
                citation_count=80000,
                doi=None,
                arxiv_id="1810.04805",
                abstract="We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers."
            ),
            Paper(
                paper_id="mock3",
                title="Language Models are Few-Shot Learners",
                authors=["Tom B. Brown", "Benjamin Mann", "Nick Ryder"],
                year=2020,
                citation_count=50000,
                doi=None,
                arxiv_id="2005.14165",
                abstract="Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. In this work, we show that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches."
            )
        ]

def generate_bibtex_key(paper: Paper) -> str:
    """Generate firstauthorYearkeyword key."""
    if not paper.authors:
        first = "unknown"
    else:
        first = paper.authors[0].split()[-1].lower()
    
    year = str(paper.year) if paper.year else "2024"
    
    # Simple keyword extraction
    words = [w.lower() for w in paper.title.split() if w.lower() not in {"the", "a", "an", "on", "in"}]
    keyword = words[0] if words else "paper"
    keyword = "".join(c for c in keyword if c.isalnum())
    first = "".join(c for c in first if c.isalnum())
    
    return f"{first}{year}{keyword}"

def generate_bibtex_entry(paper: Paper) -> str:
    key = generate_bibtex_key(paper)
    authors = " and ".join(paper.authors)
    
    entry_type = "article"
    if paper.arxiv_id:
        venue = f"arXiv preprint arXiv:{paper.arxiv_id}"
    elif paper.doi:
        venue = "Journal"
    else:
        venue = "Unknown Venue"
        
    bib = f"@article{{{key},\n"
    bib += f"  title={{{paper.title}}},\n"
    bib += f"  author={{{authors}}},\n"
    if paper.year:
        bib += f"  year={{{paper.year}}},\n"
    if paper.doi:
        bib += f"  doi={{{paper.doi}}},\n"
    if paper.arxiv_id:
        bib += f"  journal={{arXiv preprint arXiv:{paper.arxiv_id}}},\n"
    bib += "}"
    
    return bib
