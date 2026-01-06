import torch
import re
from typing import List, Dict
import os
import json
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel
except ImportError:
    pass # Might be missing if only using GGUF

from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
from .search_tool import Paper, generate_bibtex_key

class LocalLLM:
    def __init__(self, config: Dict):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_type = config['model'].get('type', 'transformers') # 'transformers' or 'gguf'
        
        # Load Embedding Model for Clustering
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        if self.model_type == 'gguf':
            self._init_gguf()
        else:
            self._init_transformers()

    def _init_gguf(self):
        try:
            from llama_cpp import Llama
            from huggingface_hub import hf_hub_download
        except ImportError:
            raise ImportError("Please run: pip install llama-cpp-python huggingface_hub")

        repo_id = self.config['model']['base']
        filename = self.config['model'].get('file', 'LFM2-2.6B-Exp-Q4_K_M.gguf') 
        
        print(f"Loading GGUF Model: {repo_id}/{filename} for CPU...")
        
        # Download model (if not cached)
        try:
            model_path = hf_hub_download(repo_id=repo_id, filename=filename)
        except Exception as e:
            print(f"Warning: Failed to download {filename}: {e}")
            print("Attempting to find alternative GGUF files in repository...")
            try:
                from huggingface_hub import list_repo_files
                files = list_repo_files(repo_id)
                gguf_files = [f for f in files if f.endswith('.gguf') and 'Q4_K_M' in f]
                if not gguf_files:
                    gguf_files = [f for f in files if f.endswith('.gguf')]
                
                if gguf_files:
                    alt_filename = gguf_files[0]
                    print(f"Found alternative: {alt_filename}")
                    model_path = hf_hub_download(repo_id=repo_id, filename=alt_filename)
                    self.config['model']['file'] = alt_filename # Update config
                else:
                    raise FileNotFoundError(f"No GGUF files found in {repo_id}")
            except Exception as inner_e:
                raise ImportError(f"Could not download model: {inner_e}")
        
        # CPU Optimization logic
        physical_cores = os.cpu_count() // 2 if os.cpu_count() else 4
        
        self.model = Llama(
            model_path=model_path,
            n_ctx=4096, # Optimized Context Size
            n_batch=4096, # Match Context Size to avoid decoding errors
            n_threads=physical_cores,
            verbose=False 
        )
        print(f"LFM2 GGUF Loaded (Threads: {physical_cores}, Context: 4096)")
        self.tokenizer = None 

    def _init_transformers(self):
        # Load LFM2 Model (Transformers)
        base_model_name = self.config['model']['base']
        adapter_path = self.config['model'].get('adapter')
        
        print(f"Loading Base Model: {base_model_name}")
        
        quantization_config = None
        if self.config['model'].get('quantization') == '4bit':
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            )
            
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        if adapter_path and hasattr(self.model, "load_adapter"): 
            try:
                print(f"Loading Adapter: {adapter_path}")
                self.model = PeftModel.from_pretrained(self.model, adapter_path)
            except Exception as e:
                print(f"Warning: Could not load adapter from {adapter_path}: {e}")

    def _get_tool_definitions(self) -> list:
        """Define tools for LFM2 function calling (optimized for length)."""
        return [
            {
                "name": "search_paper",
                "description": "Find papers. Use MULTIPLE times.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Keywords (2-4 words)"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

    def _parse_tool_calls(self, text: str) -> list:
        """Parse tool calls from LFM2 output."""
        import ast
        tool_calls = []
        
        # DEBUG: Log raw text for analysis
        print(f"[DEBUG] Parsing text for tools: {text[:100]}...")

        # 1. Try standard LFM2 format with special tokens
        pattern_token = r'<\|tool_call_start\|>\s*\[(.*?)\]\s*<\|tool_call_end\|>'
        matches = re.findall(pattern_token, text, re.DOTALL)
        
        # 2. If no special tokens, try finding the list text directly [func(...)]
        # This handles GGUF models that might skip special tokens (e.g. Unsloth versions)
        if not matches:
            fallback_pattern = r'\[\s*\w+\s*\(.*?\)\s*\]'
            fallback_matches = re.findall(fallback_pattern, text, re.DOTALL)
            if fallback_matches:
                print("[DEBUG] Found tool calls via fallback text pattern")
                matches = [m.strip('[]') for m in fallback_matches]
        
        # If still no matches, try finding raw function calls without list brackets
        if not matches:
             raw_call_pattern = r'search_paper\s*\(.*?\)'
             raw_matches = re.findall(raw_call_pattern, text)
             if raw_matches:
                 print("[DEBUG] Found raw function calls")
                 matches = [", ".join(raw_matches)]

        for match in matches:
            # Parse Pythonic function calls like: search_paper(query="Mamba")
            func_pattern = r'(\w+)\((.*?)\)'
            func_matches = re.findall(func_pattern, match)
            
            for func_name, args_str in func_matches:
                try:
                    # Parse keyword arguments
                    args = {}
                    arg_pattern = r'(\w+)\s*=\s*["\']([^"\']+)["\']'
                    arg_matches = re.findall(arg_pattern, args_str)
                    for arg_name, arg_value in arg_matches:
                        args[arg_name] = arg_value
                    
                    if args:
                        tool_calls.append({"name": func_name, "arguments": args})
                except Exception as e:
                    print(f"[Agent] Failed to parse tool call: {e}")
                    continue
        
        return tool_calls

    def search_with_tools(self, user_idea: str, paper_searcher) -> list:
        """
        Use LFM2 Tool Use to dynamically search for papers.
        LLM decides what to search based on the research idea.
        """
        tools = self._get_tool_definitions()
        tools_json = json.dumps(tools, ensure_ascii=False)
        
        # Build system prompt with tools (LFM2 ChatML format)
        system_prompt = f"""You are an expert research assistant. Find relevant academic papers.

You have access to a paper search tool. Use it to find papers for:
1. Core concepts (models, methods)
2. Cutting-edge alternatives (e.g., Mamba, RWKV, xLSTM)
3. Comparison targets (e.g., "faster than X")
4. Seminal papers

Call search_paper multiple times with DIFFERENT queries.
Queries must be SHORT (2-4 words).

List of tools: <|tool_list_start|>{tools_json}<|tool_list_end|>"""

        user_prompt = f"Find relevant academic papers for this research idea: {user_idea}"
        
        # Construct prompt in LFM2 ChatML format
        prompt = f"""<|startoftext|><|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant
"""
        
        all_papers = []
        seen_ids = set()
        max_iterations = 5
        
        print("\n[Agent] Analyzing research idea with LFM2 Tool Use...")
        
        for iteration in range(max_iterations):
            # Generate response
            if self.model_type == 'gguf':
                if hasattr(self.model, "reset"):
                    self.model.reset()  # Force reset to avoid KV cache fragmentation/overflow
                    
                output = self.model(
                    prompt,
                    max_tokens=256,
                    temperature=0.3,
                    min_p=0.15,
                    repeat_penalty=1.05,
                    echo=False,
                    stop=["<|im_end|>", "</s>"]
                )
                response_text = output['choices'][0]['text'].strip()
            else:
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=256,
                        temperature=0.3,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id
                    )
                response_text = self.tokenizer.decode(
                    outputs[0][inputs.input_ids.shape[1]:], 
                    skip_special_tokens=False
                ).strip()
            
            # DEBUG: Print raw LLM output
            print(f"\n[DEBUG] Iteration {iteration + 1} - LLM Response:")
            print(f"[DEBUG] {response_text[:500]}...")
            print(f"[DEBUG] Contains tool_call_start: {'<|tool_call_start|>' in response_text}")
            
            # Check for tool calls
            tool_calls = self._parse_tool_calls(response_text)
            
            if not tool_calls:
                print(f"[Agent] LLM finished searching after {iteration + 1} iterations (no tool calls found)")
                break
            
            # Execute tool calls
            tool_responses = []
            for call in tool_calls:
                if call["name"] == "search_paper":
                    query = call["arguments"].get("query", "")
                    if query:
                        print(f"[Agent] Tool call: search_paper(query=\"{query}\")")
                        # 3 papers search, but only top 2 used in prompt
                        papers = paper_searcher.search_papers(query, limit=3, min_citations=0)
                        
                        # Add new papers
                        for paper in papers:
                            if paper.paper_id not in seen_ids:
                                all_papers.append(paper)
                                seen_ids.add(paper.paper_id)
                        
                        # Format response (Minimal format to save tokens)
                        results = [{"t": p.title, "y": p.year} for p in papers[:2]]
                        tool_responses.append(json.dumps(results, ensure_ascii=False))
            
            if not tool_responses:
                break
            
            # Build next prompt with tool responses
            tool_response_text = "; ".join(tool_responses)
            prompt += f"""{response_text}<|im_end|>
<|im_start|>tool
<|tool_response_start|>{tool_response_text}<|tool_response_end|><|im_end|>
<|im_start|>assistant
"""
        
        print(f"[Agent] Found {len(all_papers)} papers via LFM2 Tool Use")
        
        # Sort by citation count
        all_papers.sort(key=lambda p: p.citation_count, reverse=True)
        
        return all_papers

    def expand_queries(self, user_idea: str, base_queries: list = None) -> list:
        """
        Use LLM to expand search queries with related concepts.
        """
        prompt = f"""### Instruction:
You are a research assistant. Given a research idea, generate diverse academic search queries.

Research Idea: "{user_idea}"

Generate 5-8 search queries that include:
1. Core concepts mentioned (e.g., RNN, LSTM, Transformer)
2. Cutting-edge related techniques (e.g., if RNN → Mamba, RWKV, xLSTM, State Space Models)
3. Comparison/efficiency keywords (e.g., efficient, linear complexity, parallel)
4. Seminal papers keywords (e.g., "attention is all you need")
5. **Latest research keywords (e.g., "2025", "2026", "review 2024")**

Return ONLY a JSON array of strings. No explanation.
Example output: ["LSTM efficiency", "Mamba state space model 2025", "RNN vs Transformer speed 2026"]

### Response:
"""
        try:
            if self.model_type == 'gguf':
                output = self.model(
                    prompt,
                    max_tokens=256,
                    temperature=0.3,
                    min_p=0.15,
                    repeat_penalty=1.05,
                    echo=False,
                    stop=["</s>", "[/INST]", "<|im_end|>", "\n\n"]
                )
                raw_output = output['choices'][0]['text'].strip()
            else:
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=256,
                        temperature=0.3,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id
                    )
                raw_output = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
            
            # Parse JSON array from output
            raw_output = self._clean_output(raw_output)
            
            # Try to extract JSON array
            match = re.search(r'\[.*?\]', raw_output, re.DOTALL)
            if match:
                queries = json.loads(match.group())
                if isinstance(queries, list):
                    # Combine with base queries
                    if base_queries:
                        seen = set(q.lower() for q in base_queries)
                        for q in queries:
                            if isinstance(q, str) and q.lower() not in seen:
                                base_queries.append(q)
                                seen.add(q.lower())
                        return base_queries[:10]  # Max 10 queries
                    return queries[:8]
            
            print("[LLM] Could not parse query expansion output, using base queries only")
            return base_queries or []
            
        except Exception as e:
            print(f"[LLM] Query expansion failed: {e}")
            return base_queries or []

    def cluster_papers(self, papers: List[Paper], n_clusters=3) -> Dict[int, List[Paper]]:
        """
        Cluster papers based on abstract embeddings to organize the narrative.
        """
        if not papers:
            return {}
            
        n_clusters = min(n_clusters, len(papers))
        
        abstracts = [p.abstract if p.abstract else p.title for p in papers]
        embeddings = self.embedder.encode(abstracts)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(embeddings)
        
        clusters = {i: [] for i in range(n_clusters)}
        for paper, label in zip(papers, labels):
            clusters[label].append(paper)
            
        return clusters

    def generate_related_work(self, user_idea: str, papers: List[Paper]) -> str:
        """
        Generate Related Work section.
        """
        # 1. Cluster papers to find structure
        clusters = self.cluster_papers(papers)
        
        context_text = ""
        for cid, group in clusters.items():
            context_text += f"\n[Theme {cid+1}]\n"
            for p in group:
                key = generate_bibtex_key(p)
                abstract_preview = (p.abstract[:300] + "...") if p.abstract else "(No Abstract)"
                context_text += f"[{key}] {p.title}\nAbstract: {abstract_preview}\n\n"
                
        # 2. Construct Prompt (Preserving our Agent prompt style)
        prompt = f"""### Instruction:
You are an expert researcher. Write a 'Related Work' section for a new paper based on the User Idea.
Discuss the references provided below. Group them by themes.
Use citation keys like [AuthorYearKeyword] strictly from the provided list.
Do not hallucinate citations.

[User Idea]
{user_idea}

[References]
{context_text}

### Response:
"""
        
        # 3. Generate
        gen_config = self.config.get('generation', {})
        max_new_tokens = gen_config.get('max_new_tokens', 1024)
        
        if self.model_type == 'gguf':
            # GGUF Inference (Updated with user recommended params)
            if hasattr(self.model, "reset"):
                self.model.reset()
                
            output = self.model(
                prompt,
                max_tokens=max_new_tokens,
                temperature=0.3, # User recommendation
                min_p=0.15,      # User recommendation for LFM2
                repeat_penalty=1.05,
                echo=False,
                stop=["</s>", "[/INST]", "<|im_end|>"] 
            )
            raw_output = output['choices'][0]['text'].strip()
            return self._clean_output(raw_output)
            
        else:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=gen_config.get('temperature', 0.7),
                    top_p=gen_config.get('top_p', 0.9),
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )
                
            generated_text = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            return self._clean_output(generated_text.strip())

    def _clean_output(self, text: str) -> str:
        """
        Clean LLM output by removing internal reasoning tags.
        """
        # Remove <think>...</think> blocks (including multiline)
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # Remove <response> and </response> tags but keep content
        text = re.sub(r'</?response>', '', text)
        
        # Remove any other common reasoning markers
        text = re.sub(r'\[Internal thought\].*?\[/Internal thought\]', '', text, flags=re.DOTALL)
        
        # Clean up extra whitespace and newlines
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
        text = text.strip()
        
        return text
