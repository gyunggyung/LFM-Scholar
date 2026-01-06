# LFM2 Local Agent Benchmark Report

이 문서는 로컬 환경(CPU)에서 LFM2 모델의 다양한 버전을 테스트한 비교 분석 결과를 담고 있습니다.

## 1. 테스트 개요
- **목표**: LFM-CiteAgent 파이프라인(검색 -> 인용 -> 생성)이 로컬 GGUF 모델로 정상 작동하는지 검증하고, 최적의 모델을 선정.
- **테스트 환경**: Local Windows PC (CPU Only), `llama-cpp-python`
- **테스트 프롬프트**: "Transformer models in NLP"

## 2. 모델별 결과 요약

| 모델명 | 파일명 | 실행 결과 | 특징 및 평가 |
| :--- | :--- | :--- | :--- |
| **gyung/LFM-CiteAgent-2.6B-GGUF** | `LFM2-2.6B-FineTuned_result.md` | **성공 (Best)** | **[강력 추천]**<br>- **구조**: 논문을 주제별로 완벽하게 범주화(Categorized)함.<br>- **형식**: `[Key] Title` 포맷을 정확히 준수.<br>- **안정성**: Unsloth 파인튜닝으로 호환성 문제 해결됨. |
| **unsloth/LFM2-2.6B-Exp-GGUF** | `LFM2-2.6B-UnslothBase_result.md` | **성공** | - **구조**: `[Theme X]` 형태의 단순 나열식.<br>- **형식**: 서술형 에세이 스타일에 가까움. 리스트업 지시를 일부 따르지 않음.<br>- **안정성**: 실행은 안정적임. |
| **LiquidAI/LFM2-1.2B-GGUF** | `LFM2-1.2B_result.md` | **성공** | - **구조**: 가장 단순함. 내용의 깊이는 얕음.<br>- **형식**: 넘버링 오류(3.5, 3.6...)가 발생하는 등 불안정함.<br>- **속도**: 가장 빠름. |
| **LiquidAI/LFM2-2.6B-Exp-GGUF** | (생성 실패) | **실패** | - **에러**: `AttributeError: 'LlamaModel' object has no attribute 'sampler'`<br>- **원인**: Original Base 모델의 메타데이터가 최신 `llama-cpp-python`과 호환되지 않음. |

## 3. 최종 결론
사용자가 직접 Unsloth로 파인튜닝하고 GGUF로 변환한 **`gyung/LFM-CiteAgent-2.6B-GGUF` 모델이 성능과 호환성 면에서 가장 우수**합니다. 본 프로젝트의 기본 모델로 채택합니다.

## 4. 참고 파일
- [Fine-Tuned 결과 (Best)](./LFM2-2.6B-FineTuned_result.md)
- [Unsloth Base 결과](./LFM2-2.6B-UnslothBase_result.md)
- [1.2B 결과](./LFM2-1.2B_result.md)
