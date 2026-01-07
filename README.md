# LFM-Scholar 🎓

> 🔒 **아이디어를 로컬에서 안전하게 보호하면서** 관련 연구를 자동으로 정리해주는 AI 에이전트

대충 연구 아이디어만 던지면, 기존에 나온 관련 연구들을 자동으로 찾아서 **Related Work 섹션 초안**을 작성해줍니다.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Local First](https://img.shields.io/badge/🔒-Local_First-orange.svg)](#)

## ✨ Features

| 기능 | 설명 |
|:---|:---|
| 🔒 **Local-First** | 아이디어와 생성된 텍스트는 로컬에서 처리 (검색 API만 외부 호출) |
| 🔍 **Multi-API Search** | Semantic Scholar → OpenAlex → arXiv 3단계 자동 전환 |
| 🎯 **Smart Multi-Query** | 모델명+연도, 약어(RNN, LSTM 등) 자동 인식 |
| 📚 **Auto Citation** | BibTeX 인용 자동 생성 |
| ⚠️ **Hallucination Detection** | 의심스러운 인용 감지 및 경고 |

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/gyunggyung/LFM-Scholar.git
cd LFM-Scholar
pip install -r requirements.txt
```

> **🪟 Windows 사용자**: `pip install` 전에 [Visual C++ Build Tools](https://visualstudio.microsoft.com/ko/visual-cpp-build-tools/)를 먼저 설치해주세요.

### Usage & Example

```bash
# 기본 사용 (LFM2-2.6B 모델)
python src/main.py --idea "I want to make RNN models like LSTM and GRU faster than Transformers"

# 빠른 모드 (LFM2.5-1.2B 모델) 및 출력 파일 지정
python src/main.py --idea "I want to make RNN models like LSTM and GRU faster than Transformers" --model-variant lfm2.5 --output related_work_25.md

# 결과 확인
cat related_work.md
```

**입력**: 대충 쓴 아이디어  
**출력**: 관련 논문 20개 + Related Work 초안 + BibTeX

### Model Variants

| 옵션 | 모델 | 특징 |
|:---:|:---|:---|
| `--model-variant lfm2` | LFM2-2.6B (기본값) | ✅ 높은 품질, 다양한 쿼리 생성 |
| `--model-variant lfm2.5` | LFM2.5-1.2B | ⚡ 빠른 속도, 낮은 메모리, Hallucination 적음 |

> **💡 권장**: 품질이 중요하면 `lfm2` (기본값), 빠른 초안이 필요하면 `lfm2.5`

**실행 결과 예시:**

```
# 자동 추출된 검색 쿼리
['RNN', 'LSTM', 'GRU', 'want make rnn models lstm']

# 찾아진 핵심 논문들
- [cho2014learning] GRU 원본 논문 ✅
- [greff2015lstm] LSTM: A Search Space Odyssey ✅
- [shiri2023comprehensive] CNN, RNN, LSTM, GRU 비교 (2023) ✅
```

생성된 `related_work.md`:

```markdown
## Related Work

Recurrent Neural Networks (RNNs) have been foundational in sequence modeling...
Long Short-Term Memory (LSTM) networks \cite{hochreiter1997long} addressed the
vanishing gradient problem...
```

## ⚙️ Configuration

`config.yaml` 설정:

```yaml
semantic_scholar_api_key: ""  # 선택사항 (없어도 동작)
model:
  type: "gguf"
  variant: "lfm2"  # 'lfm2' (2.6B, 고품질) 또는 'lfm2.5' (1.2B, 고속)
  
  # LFM2: 파인튜닝된 2.6B 모델 (기본값)
  lfm2:
    base: "gyung/LFM-CiteAgent-2.6B-GGUF"
    file: "LFM2-2.6B-Exp.Q4_K_M.gguf"
    
  # LFM2.5: 파인튜닝된 1.2B 모델 (빠름)
  lfm2.5:
    base: "gyung/LFM2.5-CiteAgent-1.2B-v1-GGUF"
    file: "LFM2.5-1.2B-Instruct.Q4_K_M.gguf"
```

## 🔄 Search Strategy (Fallback)

```
1. Semantic Scholar (최고 품질, Rate Limit 있음)
      ↓ 실패 시
2. OpenAlex (Rate Limit 없음)
      ↓ 실패 시  
3. arXiv (최신 preprint)
```

## 📁 Project Structure

```
LFM-Scholar/
├── src/
│   ├── main.py              # 메인 진입점
│   └── agent/
│       ├── local_llm.py     # 로컬 LLM 추론
│       ├── search_tool.py   # Multi-API 검색
│       └── verifier.py      # 환각 탐지
├── benchmarks/              # 모델 벤치마크 결과
├── config.yaml              # 설정 파일
├── requirements.txt
└── README.md
```

## ⚠️ Known Limitations

- **최신 논문 검색 한계**: 수일~수주 내 발표된 논문은 API 인덱싱 지연으로 검색 안 될 수 있음
- **키워드 기반 검색**: 입력에 포함된 키워드 기반 검색 (완전 새로운 분야는 직접 키워드 제공 필요)
- **중복 인용 가능성**: 동일 논문이 다른 테마에서 중복 인용될 수 있음 (수동 검토 권장)

## 🗺️ Roadmap

### ✅ v1.2 (Current)
- [x] Multi-API Fallback (Semantic Scholar → OpenAlex → arXiv)
- [x] 다중 쿼리 검색 (패턴 기반 + LLM 확장)
- [x] 최신 논문(2024+) 우선 검색 로직
- [x] 환각 탐지 기능
- [x] **Model Variant 선택** (`--model-variant lfm2/lfm2.5`)
- [x] LFM2.5 파인튜닝 및 통합 (빠른 추론 옵션)

### 🔜 v2.0 (Next)
- [ ] **Assistant Mode**: Overleaf 연동하여 기존 텍스트에 인용 자동 삽입
- [ ] **Knowledge Injection**: 핵심 논문 DB로 검색 품질 향상
- [ ] **Windows Overleaf 자동화**: Selenium + Chrome DevTools

### 📋 Long-term
- [ ] 로컬 벡터 DB (오프라인 검색)
- [ ] SFT 학습 (인용 위치 식별)
- [ ] LFM2.5 추가 학습으로 품질 개선

## 🤝 Contributing

Issues와 PR 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [**citeAgent**](https://github.com/KyuDan1/citeAgent) by [@KyuDan1](https://github.com/KyuDan1) - 이 프로젝트의 영감과 검색 방식의 기반이 되었습니다
- [**Step-DeepResearch**](https://arxiv.org/abs/2512.20491) - 이 논문을 읽고 작은 모델로도 학술 연구 보조가 가능하다는 확신을 얻었습니다
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [OpenAlex API](https://openalex.org/)
- [arXiv API](https://arxiv.org/help/api/)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gyunggyung">@gyunggyung</a>
</p>