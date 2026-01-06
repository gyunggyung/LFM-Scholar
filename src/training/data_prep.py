import os
import re
import json
import argparse
import glob
import sys
import logging
import threading
from typing import List, Dict, Optional
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(
    filename='preprocessing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a' # Append mode for log
)

def parse_latex_content(latex_content: str) -> Dict[str, str]:
    sections = {}
    pattern = r'\\section[*]?\{([^}]+)\}(.*?)(?=\\section[*]?\{|$)'
    matches = re.finditer(pattern, latex_content, re.DOTALL)
    for match in matches:
        title = match.group(1).strip().lower()
        content = match.group(2).strip()
        sections[title] = content
    return sections

def load_bib_file(bib_path: str) -> Dict[str, Dict]:
    if not os.path.exists(bib_path):
        return {}
    
    # Skip large bib files (>500KB) - they cause parsing hangs
    if os.path.getsize(bib_path) > 500 * 1024:
        logging.warning(f"Skipping large bib file: {bib_path}")
        return {}
    
    try:
        import bibtexparser
        with open(bib_path, 'r', encoding='utf-8', errors='ignore') as bibtex_file:
            content = bibtex_file.read()
            # Skip if too many entries (parser hangs on huge files)
            if content.count('@') > 500:
                logging.warning(f"Skipping bib with too many entries: {bib_path}")
                return {}
            bib_database = bibtexparser.loads(content)
        entries = {}
        for entry in bib_database.entries:
            if 'ID' in entry:
                entries[entry['ID']] = entry
        return entries
    except Exception as e:
        logging.error(f"Error loading bib {bib_path}: {e}")
        return {}

def extract_citations(text: str) -> List[str]:
    citations = []
    pattern = r'\\cite[a-z]*\{([^}]+)\}'
    matches = re.finditer(pattern, text)
    for match in matches:
        keys = match.group(1).split(',')
        citations.extend([k.strip() for k in keys])
    return list(set(citations))

def clean_text(text: str) -> str:
    text = re.sub(r'\\[a-zA-Z]+\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def process_paper(tex_path: str, bib_path: str) -> Optional[Dict]:
    try:
        with open(tex_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        sections = parse_latex_content(content)
        
        target_section = None
        for key in sections:
            if 'related work' in key or 'background' in key or 'literature' in key:
                target_section = sections[key]
                break
                
        if not target_section:
            logging.warning(f"{os.path.basename(tex_path)}: No Related Work section found")
            return None
            
        citation_keys = extract_citations(target_section)
        if len(citation_keys) < 3:
            logging.warning(f"{os.path.basename(tex_path)}: Too few citations ({len(citation_keys)})")
            return None
            
        bib_entries = load_bib_file(bib_path)
        input_abstracts = []
        valid_citations = 0
        
        for key in citation_keys:
            entry = bib_entries.get(key) or bib_entries.get(key.lower())
            if not entry:
                continue
            
            title = clean_text(entry.get('title', ''))
            abstract = entry.get('abstract', '')
            
            if not title:
                continue

            # Fallback: USE TITLE ONLY if abstract missing (for speed)
            if not abstract:
                abstract = "(Abstract not available)"
            else:
                abstract = clean_text(abstract)
                
            input_abstracts.append(f"[Paper] Title: {title}\nAbstract: {abstract}")
            valid_citations += 1
            
        if valid_citations < 3:
            logging.warning(f"{os.path.basename(tex_path)}: Only {valid_citations} valid citations found")
            return None
            
        return {
            "instruction": "Based on the following abstracts, write a comprehensive 'Related Work' section with proper citations.",
            "input": "\n\n".join(input_abstracts),
            "output": target_section
        }
        
    except Exception as e:
        logging.error(f"Error processing {tex_path}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="LFM-CiteAgent Data Preparation")
    parser.add_argument("--data_dir", type=str, default="./data/arxiv_source", help="Raw data directory")
    parser.add_argument("--output_file", type=str, default="./data/processed/train.jsonl", help="Output JSONL file")
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    
    # Use 'a' mode to append, preventing data loss
    # But if running fresh on new folder logic, maybe 'w' is okay?
    # User requested persistent storage, so let's check if we want to clear first manually
    # For this script run, let's use append to be safe
    
    paper_dirs = [f.path for f in os.scandir(args.data_dir) if f.is_dir()]
    logging.info(f"Found {len(paper_dirs)} paper directories in {args.data_dir}")
    
    successful = 0
    with open(args.output_file, 'a', encoding='utf-8') as out_f:
        for p_dir in tqdm(paper_dirs, desc="Processing papers"):
            try:
                tex_files = glob.glob(os.path.join(p_dir, "*.tex"))
                bib_files = glob.glob(os.path.join(p_dir, "*.bib"))
                
                if not tex_files or not bib_files:
                    logging.warning(f"{os.path.basename(p_dir)}: Missing .tex or .bib")
                    continue
                    
                main_tex = max(tex_files, key=os.path.getsize)
                main_bib = bib_files[0]
                
                example = process_paper(main_tex, main_bib)
                if example:
                    out_f.write(json.dumps(example, ensure_ascii=False) + '\n')
                    out_f.flush()
                    successful += 1
                    logging.info(f"SUCCESS: {os.path.basename(p_dir)}")
            except Exception as e:
                logging.error(f"CRITICAL ERROR processing {p_dir}: {e}")

    print(f"Processed {successful} new examples. Log saved to preprocessing.log")

if __name__ == "__main__":
    main()
