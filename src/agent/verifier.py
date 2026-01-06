from typing import List, Dict, Tuple
import re
from .search_tool import Paper, generate_bibtex_entry, generate_bibtex_key

class CitationVerifier:
    def __init__(self, papers: List[Paper]):
        self.papers = papers
        # Map generated keys (theoretical) to papers
        self.paper_map = {generate_bibtex_key(p): p for p in papers}
        
    def find_matches(self, text: str) -> Tuple[str, str]:
        """
        Identify citation keys in text, check overlap with search results,
        and generate valid BibTeX.
        Returns (modified_text_with_fixed_keys, bibtex_string)
        Also detects potential hallucinations (citations not in paper_map).
        """
        # Find all [Key] patterns
        # LFM2 might generate [AuthorYearKeyword] or \cite{...}
        # We assume it follows instructions to use [Key]
        
        found_keys = re.findall(r'\[(.*?)\]', text)
        valid_entries = []
        
        # Track verified vs suspicious citations
        verified_keys = []
        suspicious_keys = []
        
        used_papers = []
        
        for key in found_keys:
            if key in self.paper_map:
                verified_keys.append(key)
                used_papers.append(self.paper_map[key])
            else:
                # Check if it looks like a citation key (author+year pattern)
                if re.match(r'^[a-z]+\d{4}', key.lower()):
                    suspicious_keys.append(key)
        
        # Remove duplicates
        used_papers = list({p.paper_id: p for p in used_papers}.values())
        
        # Log suspicious citations (potential hallucinations)
        if suspicious_keys:
            print(f"[Verifier] ⚠️ Suspicious citations detected (not in search results):")
            for key in suspicious_keys[:5]:  # Show max 5
                print(f"  - [{key}]")
            print(f"[Verifier] These may be hallucinated. Consider manual verification.")
        
        # Log verified citations
        if verified_keys:
            print(f"[Verifier] ✅ Verified {len(set(verified_keys))} citations against search results.")
        
        bib_entries = [generate_bibtex_entry(p) for p in used_papers]
        
        return text, "\n\n".join(bib_entries)

    def verify_and_fix(self, text: str, used_keys: List[str]) -> Tuple[str, str]:
        # Alternative method if LLM returns list of used keys explicitly
        pass
