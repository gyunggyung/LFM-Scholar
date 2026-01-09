[🇰🇷 한국어](README.md) | **🇺🇸 English**

# LFM-Scholar 🎓

> 🔒 **AI agent that automatically organizes related research** while keeping your ideas safe locally

Just throw in a rough research idea, and it automatically finds related studies and creates a **Related Work section draft**.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Local First](https://img.shields.io/badge/🔒-Local_First-orange.svg)](#)

## ✨ Features

| Feature | Description |
|:---|:---|
| 🔒 **Local-First** | Ideas and generated text are processed locally (only search APIs are called externally) |
| 🔍 **Multi-API Search** | Semantic Scholar → OpenAlex → arXiv 3-stage automatic fallback |
| 🎯 **Smart Multi-Query** | Automatic recognition of model names+years, abbreviations (RNN, LSTM, etc.) |
| 📚 **Auto Citation** | Automatic BibTeX citation generation |
| ⚠️ **Hallucination Detection** | Detection and warning of suspicious citations |

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/gyunggyung/LFM-Scholar.git
cd LFM-Scholar
pip install -r requirements.txt
```

> **🪟 Windows Users**: Please install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) before running `pip install`.

### Usage & Example

```bash
# Basic usage (LFM2-2.6B model)
python src/main.py --idea "I want to make RNN models like LSTM and GRU faster than Transformers"

# Fast mode (LFM2.5-1.2B model) and specify output file
python src/main.py --idea "I want to make RNN models like LSTM and GRU faster than Transformers" --model-variant lfm2.5 --output related_work_25.md

# Check results
cat related_work.md
```

**Input**: Rough idea  
**Output**: 20+ related papers + Related Work draft + BibTeX

### Model Variants

| Option | Model | Characteristics |
|:---:|:---|:---|
| `--model-variant lfm2` | LFM2-2.6B (default) | ✅ High quality, diverse query generation |
| `--model-variant lfm2.5` | LFM2.5-1.2B | ⚡ Fast speed, low memory, less hallucination |

> **💡 Recommendation**: Use `lfm2` (default) for quality, `lfm2.5` for quick drafts

**Example Output:**

```
# Auto-extracted search queries
['RNN', 'LSTM', 'GRU', 'want make rnn models lstm']

# Found key papers
- [cho2014learning] GRU original paper ✅
- [greff2015lstm] LSTM: A Search Space Odyssey ✅
- [shiri2023comprehensive] CNN, RNN, LSTM, GRU comparison (2023) ✅
```

Generated `related_work.md`:

```markdown
## Related Work

Recurrent Neural Networks (RNNs) have been foundational in sequence modeling...
Long Short-Term Memory (LSTM) networks \cite{hochreiter1997long} addressed the
vanishing gradient problem...
```

## ⚙️ Configuration

`config.yaml` settings:

```yaml
semantic_scholar_api_key: ""  # Optional (works without it)
model:
  type: "gguf"
  variant: "lfm2"  # 'lfm2' (2.6B, high quality) or 'lfm2.5' (1.2B, fast)
  
  # LFM2: Fine-tuned 2.6B model (default)
  lfm2:
    base: "gyung/LFM-CiteAgent-2.6B-GGUF"
    file: "LFM2-2.6B-Exp.Q4_K_M.gguf"
    
  # LFM2.5: Fine-tuned 1.2B model (fast)
  lfm2.5:
    base: "gyung/LFM2.5-CiteAgent-1.2B-v1-GGUF"
    file: "LFM2.5-1.2B-Instruct.Q4_K_M.gguf"
```

## 🔄 Search Strategy (Fallback)

```
1. Semantic Scholar (highest quality, rate limited)
      ↓ on failure
2. OpenAlex (no rate limit)
      ↓ on failure  
3. arXiv (latest preprints)
```

## 📁 Project Structure

```
LFM-Scholar/
├── src/
│   ├── main.py              # Main entry point
│   └── agent/
│       ├── local_llm.py     # Local LLM inference
│       ├── search_tool.py   # Multi-API search
│       └── verifier.py      # Hallucination detection
├── benchmarks/              # Model benchmark results
├── config.yaml              # Configuration file
├── requirements.txt
└── README.md
```

## ⚠️ Known Limitations

- **Recent paper search limitations**: Papers published within days or weeks may not be searchable due to API indexing delays
- **Keyword-based search**: Searches based on keywords in input (new fields may require manual keyword provision)
- **Possible duplicate citations**: Same paper may be cited in different themes (manual review recommended)

## 🗺️ Roadmap

### ✅ v1.2 (Current)
- [x] Multi-API Fallback (Semantic Scholar → OpenAlex → arXiv)
- [x] Multi-query search (pattern-based + LLM expansion)
- [x] Recent papers (2024+) priority search logic
- [x] Hallucination detection feature
- [x] **Model Variant selection** (`--model-variant lfm2/lfm2.5`)
- [x] LFM2.5 fine-tuning and integration (fast inference option)

### 🔜 v2.0 (Next)
- [ ] **Assistant Mode**: Overleaf integration for automatic citation insertion into existing text
- [ ] **Knowledge Injection**: Improve search quality with core paper DB
- [ ] **Windows Overleaf Automation**: Selenium + Chrome DevTools

### 📋 Long-term
- [ ] Local vector DB (offline search)
- [ ] SFT training (citation position identification)
- [ ] Additional LFM2.5 training for quality improvement

## 🤝 Contributing

Issues and PRs are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [**citeAgent**](https://github.com/KyuDan1/citeAgent) by [@KyuDan1](https://github.com/KyuDan1) - Inspiration and foundation for the search approach of this project
- [**Step-DeepResearch**](https://arxiv.org/abs/2512.20491) - Reading this paper gave me confidence that small models can assist academic research
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [OpenAlex API](https://openalex.org/)
- [arXiv API](https://arxiv.org/help/api/)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gyunggyung">@gyunggyung</a>
</p>
