import torch
import re
from typing import List, Dict
import os
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
        model_path = hf_hub_download(repo_id=repo_id, filename=filename)
        
        # CPU Optimization logic (from user snippet)
        physical_cores = os.cpu_count() // 2 if os.cpu_count() else 4
        
        self.model = Llama(
            model_path=model_path,
            n_ctx=4096, # Expanded context as per user reference
            n_threads=physical_cores,
            verbose=False 
        )
        print(f"LFM2 GGUF Loaded (Threads: {physical_cores})")
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
            # Transformers Inference
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
        Removes <think>...</think> blocks and <response>...</response> wrappers.
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
