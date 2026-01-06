# LFM2 vs LFM2.5 파인튜닝 모델 비교

**날짜:** 2026-01-06  
**테스트 프롬프트:** `"I want to make RNN models like LSTM and GRU faster than Transformers"`

## 모델 스펙

| 모델 | 베이스 | 파인튜닝 | 파라미터 | 사전학습 토큰 |
|------|--------|----------|----------|--------------|
| **LFM2-2.6B** | LiquidAI/LFM2-2.6B-Exp | gyung/LFM-CiteAgent-2.6B-GGUF | 2.6B | 10T |
| **LFM2.5-1.2B** | LiquidAI/LFM2.5-1.2B-Instruct | gyung/LFM2.5-CiteAgent-1.2B-v1-GGUF | 1.2B | 28T |

## 벤치마크 결과

### 논문 검색 (Phase 2)

| 지표 | LFM2-2.6B | LFM2.5-1.2B |
|------|-----------|-------------|
| 검색된 논문 | 22개 | 14개 |
| 쿼리 다양성 | ✅ 다양함 | ⚠️ 일부 반복 |

### Related Work 생성 (Phase 3)

| 지표 | LFM2-2.6B | LFM2.5-1.2B |
|------|-----------|-------------|
| 출력 길이 | 180줄 / 8KB | 116줄 / 6KB |
| 테마 수 | 18개 | 3개 |
| 검증된 인용 | ✅ 14개 | ✅ 10개 |
| Hallucination | ⚠️ 일부 | ❌ 없음 |
| BibTeX 항목 | 완성 | 완성 |

### 속도 비교

| 모델 | 로딩 | 추론 속도 |
|------|------|----------|
| LFM2-2.6B | 느림 | 보통 |
| LFM2.5-1.2B | ⚡ 빠름 | ⚡ 빠름 |

## 핵심 발견 논문 비교

### LFM2-2.6B
- Mamba, RWKV, xLSTM 비교
- State Space Models (S4)
- Linear Attention Transformers

### LFM2.5-1.2B
- SPMamba (State-space model)
- Dual-path Mamba
- Gated Linear Attention
- xLSTM Kernels

## 권장 사항

| 용도 | 권장 모델 |
|------|----------|
| **프로덕션 (품질 우선)** | LFM2-2.6B ✅ |
| **빠른 초안** | LFM2.5-1.2B ⚡ |
| **저메모리 환경** | LFM2.5-1.2B |

## 결론

| 모델 | 장점 | 단점 |
|------|------|------|
| **LFM2-2.6B** | 높은 품질, 다양한 쿼리 | 느림, 일부 Hallucination |
| **LFM2.5-1.2B** | 빠름, Hallucination 없음 | 논문 수 적음, 쿼리 반복 |

**LFM2-2.6B를 Default로 유지**하며, 빠른 초안이 필요한 경우 `--model-variant lfm2.5` 사용 권장.

## 벤치마크 파일

| 파일 | 설명 |
|------|------|
| `LFM2-2.6B-CiteAgent_result.md` | LFM2-2.6B 최신 결과 |
| `LFM2.5-1.2B-CiteAgent_result.md` | LFM2.5-1.2B 최신 결과 |
