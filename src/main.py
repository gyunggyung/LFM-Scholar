import argparse
import yaml
import os
import sys

# Fix Windows MKL memory leak warning and joblib core detection issue
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.search_tool import PaperSearcher
from src.agent.local_llm import LocalLLM
from src.agent.verifier import CitationVerifier

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_keywords(idea: str, max_words: int = 8) -> str:
    """
    Extract key search terms from a research idea.
    Removes common stopwords and limits to most important terms.
    """
    stopwords = {
        'is', 'a', 'an', 'the', 'for', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'with', 'by', 'from', 'as', 'of', 'that', 'this', 'it', 'its', 'are', 'was',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'can', 'we', 'our', 'i', 'my',
        'delivering', 'providing', 'using', 'based', 'such', 'like', 'also'
    }
    
    # Split and clean
    words = idea.lower().replace('-', ' ').split()
    keywords = [w.strip('.,!?()[]{}":;') for w in words if w.lower() not in stopwords]
    
    # Remove very short words and duplicates while preserving order
    seen = set()
    filtered = []
    for w in keywords:
        if len(w) > 2 and w not in seen:
            seen.add(w)
            filtered.append(w)
    
    # Return top keywords
    return ' '.join(filtered[:max_words])

def extract_multiple_queries(idea: str) -> list:
    """
    패턴 기반 다중 쿼리 추출 (개선됨)
    1. 모델명 + 연도 패턴 (LSTM 1997, Transformers 2017)
    2. 대문자 약어 (RNN, LSTM, GRU)
    3. 비교 대상 추출 (faster than X, better than X)
    4. 목적 키워드 (efficient, speed, parallel 등)
    5. 기본 키워드
    """
    import re
    queries = []
    idea_lower = idea.lower()
    
    # 1. 모델명 + 연도 패턴 (예: "LSTMs (1997)", "Transformers in 2017")
    model_year_patterns = [
        r'(\w+)\s*[\(\[](\d{4})[\)\]]',  # LSTM (1997)
        r'(\w+)\s+in\s+(\d{4})',          # Transformers in 2017
        r'(\w+)\s+(\d{4})',               # BERT 2018
    ]
    for pattern in model_year_patterns:
        for match in re.findall(pattern, idea):
            model, year = match
            if len(model) > 2:
                queries.append(f"{model} {year}")
    
    # 2. 대문자 약어 감지 (RNN, LSTM, GRU, NLP, CNN 등)
    acronyms = re.findall(r'\b([A-Z]{2,}s?)\b', idea)
    for acr in acronyms:
        if acr not in [q.split()[0].upper() for q in queries]:
            queries.append(acr)
    
    # 3. 비교 대상 추출 (faster than X, better than X, compared to X, vs X)
    comparison_patterns = [
        r'(?:faster|better|efficient|superior)\s+than\s+(\w+)',
        r'compared\s+to\s+(\w+)',
        r'vs\.?\s+(\w+)',
        r'versus\s+(\w+)',
        r'outperform(?:s|ing)?\s+(\w+)',
    ]
    for pattern in comparison_patterns:
        matches = re.findall(pattern, idea_lower)
        for match in matches:
            target = match.capitalize()
            if len(target) > 2 and target.lower() not in [q.lower() for q in queries]:
                queries.append(target)
                # 비교 쿼리도 추가 (e.g., "RNN vs Transformer")
                if acronyms:
                    queries.append(f"{acronyms[0]} vs {target}")
    
    # 4. 목적 키워드 기반 확장 (efficiency, speed, parallel 등)
    objective_keywords = {
        'faster': ['efficient', 'speed', 'fast'],
        'efficient': ['efficient', 'optimization'],
        'speed': ['speed', 'fast', 'accelerate'],
        'parallel': ['parallel', 'parallelization'],
        'optimize': ['optimization', 'efficient'],
        'scalable': ['scalable', 'scaling'],
        'lightweight': ['lightweight', 'compact', 'efficient'],
    }
    for keyword, expansions in objective_keywords.items():
        if keyword in idea_lower:
            for acr in acronyms[:2]:  # 상위 2개 약어와 조합
                for exp in expansions[:1]:  # 첫 번째 확장만
                    combo = f"{exp} {acr}"
                    if combo.lower() not in [q.lower() for q in queries]:
                        queries.append(combo)
    
    # 5. 기본 키워드 추출 (fallback)
    basic = extract_keywords(idea, max_words=5)
    if basic:
        queries.append(basic)
    
    # 중복 제거 및 최대 8개로 확장 (더 넓은 검색)
    seen = set()
    unique_queries = []
    for q in queries:
        q_lower = q.lower()
        if q_lower not in seen:
            seen.add(q_lower)
            unique_queries.append(q)
    
    return unique_queries[:8]

def main():
    parser = argparse.ArgumentParser(description="LFM-CiteAgent: Secure Local Research Agent")
    parser.add_argument("--idea", type=str, required=True, help="User's research idea or abstract")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    parser.add_argument("--output", type=str, default="related_work.md", help="Output file path")
    parser.add_argument("--mode", type=str, default="agent", choices=["classic", "agent"],
                        help="Search mode: 'classic' (rule-based) or 'agent' (LLM Tool Use)")
    args = parser.parse_args()
    
    print(">>> Initializing LFM-CiteAgent...")
    config = load_config(args.config)
    
    searcher = PaperSearcher(api_key=config.get('semantic_scholar_api_key'))
    
    if args.mode == "agent":
        # Agent Mode: LLM decides what to search using Tool Use
        print(">>> Mode: AGENT (LFM2 Tool Use)")
        print(">>> Phase 1: Loading Local LLM...")
        llm = LocalLLM(config)
        
        print(">>> Phase 2: LLM-driven Paper Search...")
        all_papers = llm.search_with_tools(args.idea, searcher)
        
        if not all_papers:
            print("No papers found via Tool Use. Falling back to classic mode...")
            args.mode = "classic"
        else:
            papers = all_papers[:config['search'].get('top_k', 20)]
            print(f"Found {len(papers)} papers via LLM Tool Use.")
    
    if args.mode == "classic":
        # Classic Mode: Rule-based query extraction
        print(">>> Mode: CLASSIC (Rule-based)")
        print(">>> Phase 1: Searching for relevant papers...")
        
        # Extract multiple queries using pattern matching
        queries = extract_multiple_queries(args.idea)
        print(f"[Search] Extracted {len(queries)} queries: {queries}")
        
        # Search with each query and combine results
        all_papers = []
        seen_ids = set()
        
        for query in queries:
            print(f"[Search] Searching: '{query}'")
            found_papers = searcher.search_papers(query, limit=5, min_citations=0)
            for paper in found_papers:
                if paper.paper_id not in seen_ids:
                    all_papers.append(paper)
                    seen_ids.add(paper.paper_id)
        
        # Sort by citation count (Prioritize recent papers 2024+)
        all_papers.sort(key=lambda p: (1 if p.year and p.year >= 2024 else 0, p.citation_count), reverse=True)
        papers = all_papers[:config['search'].get('top_k', 20)]
        
        if not papers:
            print("No papers found. Try a different query.")
            return
        
        print(f"Found {len(papers)} papers total.")
        
        # Load LLM for generation (if not already loaded)
        print(">>> Phase 2: Loading Local LLM...")
        llm = LocalLLM(config)
        
        # LLM-based Query Expansion (find Mamba, RWKV, etc.)
        print(">>> Phase 2.5: Expanding queries with LLM...")
        expanded_queries = llm.expand_queries(args.idea, queries.copy())
        
        # Search for new queries only
        new_queries = [q for q in expanded_queries if q not in queries]
        if new_queries:
            print(f"[LLM] Expanded queries: {new_queries}")
            for query in new_queries:
                print(f"[Search] Searching: '{query}'")
                new_papers = searcher.search_papers(query, limit=5, min_citations=0)
                for paper in new_papers:
                    if paper.paper_id not in seen_ids:
                        all_papers.append(paper)
                        seen_ids.add(paper.paper_id)
            
            # Re-sort and limit (Prioritize recent papers 2024+)
            all_papers.sort(key=lambda p: (1 if p.year and p.year >= 2024 else 0, p.citation_count), reverse=True)
            papers = all_papers[:config['search'].get('top_k', 20)]
            print(f"[LLM] Total papers after expansion: {len(papers)}")
    
    # 3. Generate
    print(">>> Phase 3: Generating Related Work...")
    draft_text = llm.generate_related_work(args.idea, papers)
    
    # 4. Verify
    print(">>> Phase 4: Verifying Citations...")
    verifier = CitationVerifier(papers)
    final_text, bibtex = verifier.find_matches(draft_text)
    
    # 5. Save
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write("# Related Work\n\n")
        f.write(final_text)
        f.write("\n\n## References\n\n")
        f.write("```bibtex\n")
        f.write(bibtex)
        f.write("\n```\n")
        
    print(f"\n>>> Done! Output saved to {args.output}")

if __name__ == "__main__":
    main()
