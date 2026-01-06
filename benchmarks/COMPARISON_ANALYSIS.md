# LFM-CiteAgent 종합 비교 분석

**날짜:** 2026-01-07  
**테스트 프롬프트:** `"I want to make RNN models like LSTM and GRU faster than Transformers"`

---

## 1. 모델 버전 비교 (v1 vs v2)

### 학습 데이터
| 버전 | 학습 데이터 수 |
|------|----------------|
| v1 | 97개 |
| v2 | 937개 (9.66배 증가) |

### LFM2-2.6B
| 지표 | v1 | v2 | 평가 |
|------|-----|-----|------|
| 출력 길이 | 180줄 / 8KB | 141줄 / 6.5KB | ⚠️ v1 우세 |
| 테마 수 | 18개 | 11개 | ⚠️ v1 우세 |
| 검색 논문 | 22개 | 14개 | ⚠️ v1 우세 |
| 검증 인용 | 14개 | 9개 | ⚠️ v1 우세 |

### LFM2.5-1.2B
| 지표 | v1 | v2 | 평가 |
|------|-----|-----|------|
| 출력 길이 | 116줄 / 6KB | 20줄 / 1.5KB | ❌ v1 압도 |
| BibTeX | 10개 | **비어있음** | ❌ v1 압도 |

**결론:** v2는 학습 데이터 10배 증가에도 성능 하락. **v1 유지 결정**

---

## 2. Rate Limit 전략 비교

### 전략 설명
| 전략 | 설명 |
|------|------|
| 현재 (12초 대기) | 429 에러 시 2s→4s→6s 대기 후 OpenAlex fallback |
| 간소화 (1초 대기) | 429 에러 시 1초만 대기 후 바로 OpenAlex fallback |

### 테스트 결과
| 지표 | 현재 (12초) | 간소화 (1초) | 승자 |
|------|------------|-------------|------|
| 라인 수 | 114줄 | **176줄** | ✅ 간소화 |
| 파일 크기 | 7.2KB | **7.9KB** | ✅ 간소화 |
| BibTeX 인용 | 8개 | **15개** | ✅ 간소화 |
| 대기 시간 | 12초 | **1초** | ✅ 간소화 |

### 품질 분석 (주제 적합성)

**현재 전략 (12초):**
- ✅ 관련: 4~5개 / 8개 (50~62%)
- 핵심 논문: 0개
- 노이즈: 2~3개 (hate speech, music classification)

**간소화 전략 (1초):**
- ✅ 관련: 9~10개 / 15개 (60~67%)
- 핵심 논문: **2개** (beck2025tiled - xLSTM 커널, buestánandrade2023comparison - LSTM/GRU/Transformer 비교)
- 노이즈: 1개 (R language)

**결론:** 간소화 전략이 속도도 빠르고 품질도 우수. **간소화 전략 채택**

---

## 3. 최종 설정

### config.yaml
```yaml
# 모델 버전: v1 유지
lfm2:
  base: "gyung/LFM-CiteAgent-2.6B-GGUF"  # v1
lfm2.5:
  base: "gyung/LFM2.5-CiteAgent-1.2B-v1-GGUF"  # v1
```

### search_tool.py
```python
# Rate limit 전략: 간소화 (1초 대기 후 바로 fallback)
max_retries = 1
wait_time = 1  # seconds
```

---

## 4. 관련 벤치마크 파일

| 파일 | 설명 |
|------|------|
| `LFM2-2.6B-CiteAgent_result.md` | LFM2-2.6B v1 기준 결과 |
| `LFM2.5-1.2B-CiteAgent_result.md` | LFM2.5-1.2B v1 기준 결과 |
| `LFM2-2.6B-v2_result.md` | LFM2-2.6B v2 결과 |
| `LFM2.5-1.2B-v2_result.md` | LFM2.5-1.2B v2 결과 |
| `test_current_strategy.md` | 현재 전략 (12초 대기) 결과 |
| `test_fast_fallback_strategy.md` | 간소화 전략 (1초 대기) 결과 |
