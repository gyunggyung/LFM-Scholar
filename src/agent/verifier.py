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
        from difflib import get_close_matches
        
        # Find all [Key] patterns
        # LFM2 might generate [AuthorYearKeyword] or \cite{...}
        # We assume it follows instructions to use [Key]
        
        found_keys = re.findall(r'\[(.*?)\]', text)
        valid_entries = []
        
        # Track verified vs suspicious citations
        verified_keys = []
        suspicious_keys = []
        fixed_keys = {}  # Map: wrong_key -> correct_key
        
        used_papers = []
        valid_keys_list = list(self.paper_map.keys())
        
        for key in found_keys:
            if key in self.paper_map:
                verified_keys.append(key)
                used_papers.append(self.paper_map[key])
            else:
                # Check if it looks like a citation key (author+year pattern)
                if re.match(r'^[a-z]+\d{4}', key.lower()):
                    # Try to find close match (fix typos)
                    matches = get_close_matches(key.lower(), [k.lower() for k in valid_keys_list], n=1, cutoff=0.7)
                    if matches:
                        # Find the original case key
                        correct_key = next((k for k in valid_keys_list if k.lower() == matches[0]), None)
                        if correct_key:
                            fixed_keys[key] = correct_key
                            verified_keys.append(correct_key)
                            used_papers.append(self.paper_map[correct_key])
                        else:
                            suspicious_keys.append(key)
                    else:
                        suspicious_keys.append(key)
        
        # Apply fixes to text
        modified_text = text
        for wrong_key, correct_key in fixed_keys.items():
            modified_text = modified_text.replace(f'[{wrong_key}]', f'[{correct_key}]')
        
        # Log fixed citations
        if fixed_keys:
            print(f"[Verifier] 🔧 Auto-fixed {len(fixed_keys)} citation keys:")
            for wrong, correct in list(fixed_keys.items())[:5]:
                print(f"  - [{wrong}] → [{correct}]")
        
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
        
        return modified_text, "\n\n".join(bib_entries)

    def verify_and_fix(self, text: str, used_keys: List[str]) -> Tuple[str, str]:
        # Alternative method if LLM returns list of used keys explicitly
        pass
