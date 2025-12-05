# 🎮 Steam 게임 추천시스템 프로젝트 - 진행 현황 및 이어하기 가이드

**최종 업데이트**: 2024.12.05  
**현재 단계**: Phase 3 완료 → Phase 4 (Content-based 모델) 진행 예정

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [진행 규칙 및 스타일](#2-진행-규칙-및-스타일)
3. [완료된 Phase/Task 현황](#3-완료된-phasetask-현황)
4. [핵심 데이터 및 수치](#4-핵심-데이터-및-수치)
5. [Baseline 실험 결과 요약](#5-baseline-실험-결과-요약)
6. [생성된 파일 목록](#6-생성된-파일-목록)
7. [연구 질문 (RQ)](#7-연구-질문-rq)
8. [다음 단계 (Phase 4)](#8-다음-단계-phase-4)
9. [주의사항 및 규칙](#9-주의사항-및-규칙)
10. [이어하기 프롬프트](#10-이어하기-프롬프트)

---

## 1. 프로젝트 개요

### 1.1 프로젝트 정보
- **과목**: 경희대학교 빅데이터응용학과 3학년 추천시스템
- **주제**: Steam 게임 추천시스템 - Long-tail 아이템 추천 성능 개선
- **핵심 목표**: Hybrid 모델을 통한 Long-tail 게임 추천 성능 향상

### 1.2 데이터셋
| 데이터셋 | 파일명 | 크기 | 설명 |
|----------|--------|------|------|
| **Game Recommendations on Steam** | recommendations.csv | 1.88GB, 41M rows | 사용자-아이템 상호작용 |
| | games.csv | 50,872 rows | 게임 기본 메타데이터 |
| | users.csv | 14.3M rows | 사용자 프로필 |
| | games_metadata.json | 50,872 rows | 태그/설명 (JSONL) |
| **Steam Games Dataset 2025** | games_march2025_cleaned.csv | 89,618 rows | 확장 메타데이터 |

### 1.3 핵심 연구 방향
1. **Long-tail 아이템 문제**: 98.77%의 게임이 Long-tail (상호작용 40%)
2. **Light 사용자 문제**: 81.87%의 사용자가 Light (리뷰 < 4개)
3. **Hybrid 접근**: CF + Content-based 결합으로 Long-tail 커버리지 향상

---

## 2. 진행 규칙 및 스타일

### 2.1 SPEC-driven Development
- 모든 분석/모델링은 **사전 계획(SPEC)** 기반으로 진행
- 이전 Task 결과를 다음 Task에 논리적으로 연결
- 선행연구 기반 방법론 적용

### 2.2 TDD (Task-Driven Development) 스타일
각 Task는 다음 구조를 따름:

```
1. Task 목표 요약 (무엇을, 왜)
2. 계획/접근 방법
3. 코드/분석 실행
4. 핵심 결과 (정량적)
5. 결과 해석 (정성적, RQ 연결)
6. 다음 Task에 미치는 영향
```

### 2.3 결과 저장 규칙
- **모든 Task 결과**: `TaskResults/` 폴더에 `.md` 파일로 저장
- **파일 명명 규칙**: `Phase{N}_Task{N.M}_{내용}.md`
- **예시**: `Phase3_Baseline_Results.md`

### 2.4 사용자 확인 규칙
- 각 Task 완료 후 **사용자 확인 가이드라인** 제공
- 다음 Task 진행 전 사용자 승인 요청

---

## 3. 완료된 Phase/Task 현황

### 3.1 Phase 1: 데이터 준비 및 EDA ✅ 완료

| Task | 내용 | 상태 | 핵심 결과 |
|------|------|------|----------|
| **1.1** | recommendations.csv 기본 검증 | ✅ | 41M rows, 84.5% 추천, 평균 201시간 |
| **1.2** | games.csv, users.csv 검증 | ✅ | 50,872 games, 14.3M users |
| **1.3** | games_metadata.json 태그 분석 | ✅ | 441개 유니크 태그, 97.6% 태그 보유 |
| **1.4** | Steam 2025 데이터 매칭 분석 | ✅ | 70.5% 매칭률, estimated_owners 확보 |
| **1.5** | Zipf's Law / Pareto 분석 | ✅ | 상위 1% → 55.6% 상호작용 |
| **1.6** | 데이터 병합 및 통합 데이터셋 생성 | ✅ | merged_items.csv, merged_users.csv |

### 3.2 Phase 2: 파티션 정의 및 검증 ✅ 완료

| Task | 내용 | 상태 | 핵심 결과 |
|------|------|------|----------|
| **2.1** | 파티션 교차 분석 | ✅ | 4개 그룹 분포 확인 |
| **2.2** | Train/Valid/Test 분할 | ✅ | 80/10/10 (사용자 기반) |
| **2.3** | Sparse Matrix 구축 | ✅ | 11M users × 37K items |
| **2.4** | 실험 데이터셋 최종 준비 | ✅ | LOO 분할 + evaluation.py |

### 3.3 Phase 3: Baseline 모델 구현 및 실험 ✅ 완료

| Task | 내용 | 상태 | 핵심 결과 |
|------|------|------|----------|
| **3.1** | Popularity 모델 구현 | ✅ | Recall@10=0.0450, Coverage@5=0.03% |
| **3.2** | ItemKNN 모델 구현 | ❌ 취소 | 대규모 데이터에서 성능 문제 |
| **3.3** | ALS 모델 구현 | ❌ 취소 | Visual Studio 필요 (implicit 라이브러리) |
| **3.4** | 추가 Baseline 구현 | ✅ | Random, PopularPerTag, TruncatedSVD, CoOccurrence |

### 3.4 Phase 4~6: 대기 중

| Phase | 내용 | 상태 |
|-------|------|------|
| **Phase 4** | Content-based 모델 구현 및 실험 | 🔜 **다음** |
| **Phase 5** | Hybrid 모델 구현 및 실험 | ⏳ 대기 |
| **Phase 6** | 결과 종합 해석 및 리포트 설계 | ⏳ 대기 |

---

## 4. 핵심 데이터 및 수치

### 4.1 데이터 규모

| 항목 | 값 |
|------|-----|
| 총 상호작용 (리뷰) | **41,154,794** |
| 유니크 아이템 (recommendations.csv 기준) | **37,610** |
| 유니크 사용자 (recommendations.csv 기준) | **13,781,059** |
| 전체 아이템 (games.csv 기준) | **50,872** |
| 전체 사용자 (users.csv 기준) | **14,306,064** |

### 4.2 파티션 기준 (누적 60%)

#### 아이템 파티션
| 분류 | 기준 | 개수 | 비율 | 상호작용 비율 |
|------|------|------|------|--------------|
| **Popular** | interaction_count ≥ **18,507** | 462개 | 0.91% | **60%** |
| **Long-tail** | interaction_count < 18,507 | 50,410개 | 99.09% | 40% |

#### 사용자 파티션
| 분류 | 기준 | 인원 | 비율 |
|------|------|------|------|
| **Heavy** | review_count ≥ **4** | 2,593,061명 | 18.13% |
| **Light** | review_count < 4 | 11,713,003명 | 81.87% |

### 4.3 Pareto 분포 핵심 수치

| 분포 | 핵심 수치 |
|------|----------|
| 아이템 상위 1% | 전체 상호작용의 **55.6%** |
| 아이템 상위 10% | 전체 상호작용의 **91.6%** |
| 사용자 상위 10% | 전체 리뷰의 **47.8%** |
| 리뷰 1개만 작성한 사용자 | **55%** |

### 4.4 데이터 품질

| 항목 | 값 |
|------|-----|
| 태그 보유 게임 | 97.6% |
| Steam 2025 매칭률 | 70.5% |
| Null 값 | 대부분 0% |
| 추천 비율 (is_recommended=True) | 84.5% |

### 4.5 LOO (Leave-One-Out) 평가 데이터셋

| 항목 | 값 |
|------|-----|
| LOO Train 상호작용 | **21,908,632** |
| LOO Test 상호작용 | **4,967,282** |
| LOO 평가 대상 사용자 | **4,967,282명** |
| LOO Sparse Matrix | **4,967,282 users × 37,251 items** |

---

## 5. Baseline 실험 결과 요약 ⭐

### 5.1 전체 결과 표

| 모델 | Recall@5 | Recall@10 | Recall@20 | NDCG@10 | Coverage@5 |
|------|----------|-----------|-----------|---------|------------|
| **Random** | 0.0000 | 0.0002 | 0.0008 | 0.0001 | **0.7398** |
| **Popularity** | 0.0279 | 0.0450 | 0.0746 | 0.0220 | 0.0003 |
| **PopularPerTag** | 0.0279 | 0.0450 | 0.0746 | 0.0220 | 0.0057 |
| **TruncatedSVD** | 0.0274 | 0.0443 | 0.0740 | 0.0217 | 0.0035 |
| **CoOccurrence** | **0.0292** | **0.0513** | **0.0898** | **0.0242** | **0.0061** |

### 5.2 핵심 발견

```
1. Best Baseline: CoOccurrence
   - Recall@10 = 0.0513 (Popularity 대비 +14%)
   - Coverage@5 = 0.61% (Popularity 대비 20배)

2. 태그 활용 효과: PopularPerTag
   - Recall은 동일하지만 Coverage 19배 향상 (0.03% → 0.57%)
   - Content 정보가 다양성에 기여함 확인

3. Long-tail 문제 지속:
   - 최고 모델도 227개 아이템만 추천 (Coverage 0.61%)
   - 전체 37,251개 중 99.4%는 추천 기회 없음
   - Content-based 모델 필요
```

### 5.3 모델 선정 이유 (암기 필요)

| 모델 | 선정 이유 |
|------|----------|
| **Random** | 하한선 측정, 다른 모델의 개선 효과 검증 기준 |
| **Popularity** | 모든 RS 연구의 기본 baseline |
| **PopularPerTag** | Wang(2025) "파티션별 Popularity" 확장, 태그 활용 |
| **TruncatedSVD** | Salkanović(2024) SVD 효과성, sklearn 기본 제공 |
| **CoOccurrence** | Amazon/Netflix 검증 방식, ItemKNN 대안 |

### 5.4 RQ 연결

| RQ | Phase 3에서 확인된 내용 |
|----|------------------------|
| **RQ1** | Popularity 모델 Coverage 0.03% → Long-tail 추천 불가 확인 |
| **RQ2** | CoOccurrence가 CF 신호 활용에 효과적 |
| **RQ3** | 태그 정보(PopularPerTag)가 Coverage 향상에 기여 |

---

## 6. 생성된 파일 목록

### 6.1 통합 데이터셋 (모델링용)

| 파일명 | 행 수 | 컬럼 수 | 설명 |
|--------|-------|---------|------|
| **merged_items.csv** | 50,872 | 20 | 아이템 통합 데이터 |
| **merged_users.csv** | 14,306,064 | 5 | 사용자 통합 데이터 |

#### merged_items.csv 컬럼
```
기본 정보: app_id, title, date_release
플랫폼: win, mac, linux, steam_deck
평가: rating, positive_ratio, user_reviews, price_final, discount
상호작용: interaction_count, item_partition
태그: tags_str, num_tags, description_len
Steam 2025: estimated_owners_mid, steam2025_positive_ratio, steam2025_genres
```

#### merged_users.csv 컬럼
```
user_id, products, reviews, review_count, user_partition
```

### 6.2 분석 스크립트 (Phase 1~2)

| 파일명 | 설명 |
|--------|------|
| task1_1_eda.py | recommendations.csv EDA |
| task1_2_games_users_eda.py | games.csv, users.csv EDA |
| task1_3_metadata_eda.py | games_metadata.json 태그 분석 |
| task1_4_steam2025_eda.py | Steam 2025 데이터 분석 |
| task1_5_zipf_analysis.py | Zipf's Law / Pareto 분석 |
| task1_6_data_merge.py | 데이터 병합 |
| task2_1_partition_cross_analysis.py | 파티션 교차 분석 |
| task2_2_train_valid_test_split.py | Train/Valid/Test 분할 |
| task2_3_sparse_matrix.py | Sparse Matrix 구축 |
| task2_4_experiment_setup.py | LOO 분할 + 평가 함수 |

### 6.3 모델 스크립트 및 파일 (Phase 3) ⭐

| 파일명 | 설명 |
|--------|------|
| **models/popularity_model.py** | Popularity 모델 구현 |
| **models/popularity_model.pkl** | 학습된 Popularity 모델 |
| **models/baseline_models.py** | 4개 Baseline 모델 (Random, PopularPerTag, TruncatedSVD, CoOccurrence) |
| **models/baseline_results.pkl** | Baseline 평가 결과 저장 |
| models/itemknn_model.py | ItemKNN (취소됨) |
| models/als_model.py | ALS (취소됨) |
| **evaluation.py** | 평가 함수 모듈 (Recall, NDCG, Coverage, Novelty) |

### 6.4 TaskResults 폴더

```
TaskResults/
├── Phase1_Task1.1_recommendations_eda.md
├── Phase1_Task1.2_games_users_eda.md
├── Phase1_Task1.3_metadata_tags_eda.md
├── Phase1_Task1.4_steam2025_eda.md
├── Phase1_Task1.5_zipf_pareto_analysis.md
├── Phase1_Task1.6_data_merge.md
├── Phase2_Task2.1_partition_cross_analysis.md
├── Phase2_Task2.2_train_valid_test_split.md
├── Phase2_Task2.3_sparse_matrix.md
├── Phase2_Task2.4_experiment_setup.md
└── Phase3_Baseline_Results.md       ⭐ Phase 3 결과
```

### 6.5 data_split 폴더 (평가 데이터)

```
data_split/
├── train_interactions.csv     (32.9M - Cold User 평가용)
├── valid_interactions.csv     (4.1M)
├── test_interactions.csv      (4.1M)
├── train_sparse_binary.npz    (11M users Sparse Matrix)
├── train_sparse_weighted.npz  (Hours 가중치)
├── id_mappings.pkl            (전체 ID 매핑)
├── loo_train.csv              (21.9M - LOO 평가용) ⭐
├── loo_test.csv               (4.97M) ⭐
├── loo_train_sparse.npz       (4.96M users Sparse Matrix) ⭐
├── loo_mappings.pkl           (LOO ID 매핑) ⭐
├── loo_test_indexed.csv
└── loo_test_with_partition.csv
```

### 6.6 기타 문서

| 파일명 | 설명 |
|--------|------|
| ProjectPlan.md | 프로젝트 초기 계획 |
| AnalysisPlan.md | 분석 계획 (SPEC) |
| **ProjectReport_Phase1-2.md** | Phase 1-2 프로젝트 보고서 |
| **UsedConcepts.md** | 사용된 개념/기법 정리 |
| **.gitignore** | Git 제외 파일 목록 |
| **ProcessUpdate.md** | 현재 파일 (진행 현황) |

---

## 7. 연구 질문 (RQ)

### RQ1: Long-tail 아이템 추천
> "Long-tail 게임에 대해 Content 피처(태그, 장르)가 추천 성능을 얼마나 향상시키는가?"

- **Phase 3 결과**: Popularity Coverage 0.03% → Long-tail 추천 거의 불가능 확인
- **Phase 4 방향**: Content-based로 Long-tail 커버리지 확보

### RQ2: Light 사용자 추천
> "리뷰가 적은 Light 사용자에게 Hybrid 모델이 CF 대비 얼마나 효과적인가?"

- **Phase 3 결과**: CoOccurrence가 CF 신호 활용에 효과적 (Recall@10=0.0513)
- **Phase 4 방향**: Cold User에 대한 Content-based 추천

### RQ3: Hybrid 가중치 최적화
> "Popular/Long-tail, Heavy/Light 그룹별로 CF와 Content의 최적 가중치는?"

- **Phase 3 결과**: 태그(PopularPerTag)가 Coverage 19배 향상
- **Phase 5 방향**: CoOccurrence + Content Hybrid 실험

---

## 8. 다음 단계 (Phase 4)

### 8.1 Phase 4 목표
**Content-based 모델 구현 및 실험**

### 8.2 예정 Task

| Task | 내용 | 설명 |
|------|------|------|
| **4.1** | Tag-based Content Model | 태그 기반 아이템 유사도 계산 |
| **4.2** | TF-IDF Content Model | 태그 TF-IDF 벡터화 + 코사인 유사도 |
| **4.3** | Content-based 평가 | Recall, NDCG, Coverage 측정 |
| **4.4** | 파티션별 성능 분석 | Popular/Long-tail, Heavy/Light 그룹별 분석 |

### 8.3 Phase 4 핵심 활용 데이터

| 데이터 | 컬럼 | 설명 |
|--------|------|------|
| **merged_items.csv** | `tags_str` | 게임 태그 (97.6% 보유, 평균 12.8개) |
| | `steam2025_genres` | 장르 정보 |
| | `item_partition` | Popular/Long-tail 레이블 |
| **loo_train.csv** | user_id, app_id | LOO Train 상호작용 |
| **loo_test.csv** | user_id, app_id | LOO Test 상호작용 |

### 8.4 Phase 4 예상 산출물
- `models/content_model.py` - Content-based 모델 구현
- `TaskResults/Phase4_Content_Results.md` - 결과 보고서
- 파티션별 성능 비교 분석

### 8.5 Phase 4에서 검증할 가설

```
가설 1: Content-based 모델은 Long-tail 아이템 Coverage를 크게 향상시킬 것
       - 예상: Coverage 0.61% → 5%+ 향상

가설 2: 태그 유사도 기반 추천은 Recall도 유지할 것
       - 예상: CoOccurrence 수준 (Recall@10 ≈ 0.05) 유지

가설 3: Long-tail×Light 그룹에서 Content-based가 특히 효과적일 것
       - 이유: CF 신호 부족 → Content 신호 활용
```

---

## 9. 주의사항 및 규칙

### 9.1 대용량 파일 처리
```python
# recommendations.csv (1.88GB, 41M rows)는 반드시 청크 기반 처리
for chunk in pd.read_csv(file, chunksize=1_000_000):
    # 처리
```

### 9.2 메모리 효율화
```python
# 데이터 타입 최적화
dtype_dict = {
    'app_id': 'int32',
    'user_id': 'int32',
    'hours': 'float32'
}
df = pd.read_csv(file, dtype=dtype_dict)
```

### 9.3 파티션 기준 (고정)
- **Popular 아이템**: interaction_count ≥ 18,507
- **Long-tail 아이템**: interaction_count < 18,507
- **Heavy 사용자**: review_count ≥ 4
- **Light 사용자**: review_count < 4

### 9.4 결과 저장 규칙
- 모든 Task 결과 → `TaskResults/Phase{N}_Task{N.M}_{내용}.md`
- 정량적 결과 + 정성적 해석 포함
- RQ와 연결한 시사점 기술

### 9.5 PowerShell 주의사항
- `&&` 토큰 사용 불가 (Windows PowerShell)
- 긴 Python 코드는 `.py` 파일로 저장 후 실행
- 한글 인코딩: `encoding='utf-8'` 필수

### 9.6 모델 평가 지표

| 지표 | 설명 | Phase 3 Best |
|------|------|--------------|
| Recall@K | 추천 목록 내 실제 선호 아이템 비율 | 0.0513 (CoOccur@10) |
| NDCG@K | 순위 가중 정확도 | 0.0242 (CoOccur@10) |
| Coverage@K | 추천된 유니크 아이템 비율 | 0.0061 (CoOccur@5) |
| Novelty | Long-tail 아이템 추천 비율 | (Phase 4에서 측정) |

### 9.7 취소된 모델 이유 (참고)

| 모델 | 취소 이유 |
|------|----------|
| **ItemKNN** | 대규모 Sparse Matrix에서 유사도 계산 시간 과다 |
| **ALS (implicit)** | Visual Studio 필요 (C++ 빌드 환경) |

---

## 10. 이어하기 프롬프트

다른 컴퓨터에서 Cursor를 실행할 때 아래 프롬프트를 복사하여 사용하세요:

---

### 📝 이어하기 프롬프트 (복사용) - Phase 4 시작

```
지금부터 경희대 빅데이터응용학과 3학년 추천시스템 프로젝트를 이어서 진행합니다.

## 프로젝트 현황
- ProcessUpdate.md 파일을 읽고 현재 진행 상황을 파악해주세요.
- Phase 1 (데이터 준비 및 EDA) ✅ 완료
- Phase 2 (파티션 정의 및 검증) ✅ 완료
- Phase 3 (Baseline 모델) ✅ 완료
- 다음 단계는 Phase 4 (Content-based 모델)입니다.

## Phase 3 핵심 결과 (암기 필요)
- Best Baseline: CoOccurrence (Recall@10=0.0513, Coverage@5=0.61%)
- 문제: 최고 모델도 Coverage 0.61% (227개 아이템만 추천)
- 목표: Content-based로 Long-tail Coverage 확대

## 진행 규칙
1. SPEC-driven Development: 이전 Task 결과를 다음 Task에 논리적으로 연결
2. TDD 스타일: Task 목표 → 계획 → 실행 → 결과 → 해석 → 다음 영향
3. 모든 Task 결과는 TaskResults/ 폴더에 .md 파일로 저장
4. 각 Task 완료 후 사용자 확인 가이드라인 제공

## 핵심 데이터 경로
- merged_items.csv: 아이템 통합 (tags_str 컬럼 활용)
- data_split/loo_train.csv: LOO Train (21.9M)
- data_split/loo_test.csv: LOO Test (4.97M)
- data_split/loo_mappings.pkl: ID 매핑

## 다음 작업
Phase 4를 진행해주세요. 먼저 ProcessUpdate.md, TaskResults/Phase3_Baseline_Results.md를 확인한 후 시작해주세요.
```

---

### 📝 전체 맥락 복원 프롬프트 (상세 버전)

```
경희대 빅데이터응용학과 추천시스템 프로젝트를 이어서 진행합니다.

## 1. 현재 상태
- Phase 1 완료 (6개 Task)
- Phase 2 완료 (4개 Task)
- Phase 3 완료 (Baseline 5개 모델)
- Phase 4 진행 예정 (Content-based)

## 2. 필수 확인 파일
1. ProcessUpdate.md - 전체 진행 현황
2. AnalysisPlan.md - 분석 계획 (SPEC)
3. TaskResults/Phase3_Baseline_Results.md - Baseline 결과 (중요!)
4. TaskResults/*.md - 각 Task 결과

## 3. Phase 3 Baseline 결과 (암기 필수)
| 모델 | Recall@10 | Coverage@5 |
|------|-----------|------------|
| Random | 0.0002 | 73.98% |
| Popularity | 0.0450 | 0.03% |
| PopularPerTag | 0.0450 | 0.57% |
| TruncatedSVD | 0.0443 | 0.35% |
| CoOccurrence | **0.0513** | **0.61%** |

## 4. 핵심 수치 (암기 필요)
- 총 상호작용: 41,154,794
- Popular 아이템: 462개 (0.91%) → 상호작용 60%
- Long-tail 아이템: 50,410개 (99.09%) → 상호작용 40%
- Heavy 사용자: 2,593,061명 (18.13%)
- Light 사용자: 11,713,003명 (81.87%)
- 파티션 임계값: 아이템 18,507 interactions / 사용자 4 reviews

## 5. 연구 질문 (RQ)
- RQ1: Long-tail 게임에 Content 피처가 추천 성능을 얼마나 향상?
- RQ2: Light 사용자에게 Hybrid 모델이 CF 대비 얼마나 효과적?
- RQ3: 그룹별 CF와 Content의 최적 가중치는?

## 6. Phase 4 목표
- Content-based 모델 (태그 기반)로 Long-tail Coverage 확대
- CoOccurrence (Recall@10=0.0513) 수준 Recall 유지
- Coverage 0.61% → 5%+ 향상 목표

## 7. 진행 규칙
- 모든 결과: TaskResults/Phase{N}_Task{N.M}_{내용}.md
- 각 Task: 목표 → 계획 → 실행 → 결과 → 해석 → 다음 영향
- Task 완료 후 사용자 확인 요청

이 맥락을 기반으로 Phase 4를 시작해주세요.
```

---

## 📊 빠른 참조 표

### 파티션 기준
| 분류 | 기준 |
|------|------|
| Popular | interaction_count ≥ 18,507 |
| Long-tail | interaction_count < 18,507 |
| Heavy | review_count ≥ 4 |
| Light | review_count < 4 |

### Phase 순서
```
Phase 1 ✅ → Phase 2 ✅ → Phase 3 ✅ → Phase 4 🔜 → Phase 5 → Phase 6
EDA        파티션검증    Baseline     Content    Hybrid    리포트
```

### Baseline 성능 순위 (Recall@10 기준)
```
1. CoOccurrence  0.0513  ████████████████████  [Best]
2. Popularity    0.0450  █████████████████
3. PopularPerTag 0.0450  █████████████████
4. TruncatedSVD  0.0443  ████████████████
5. Random        0.0002  ▏                     [Baseline]
```

### 핵심 파일
```
merged_items.csv           - 모델링용 아이템 데이터 (tags_str 중요)
data_split/loo_train.csv   - LOO Train 상호작용
data_split/loo_test.csv    - LOO Test 상호작용
data_split/loo_mappings.pkl - ID 매핑
models/baseline_results.pkl - Baseline 결과 저장
```

---

**마지막 작업**: Phase 3 – Baseline 모델 5개 구현 및 평가 완료  
**Best Baseline**: CoOccurrence (Recall@10=0.0513, Coverage@5=0.61%)  
**다음 작업**: Phase 4 – Content-based 모델 구현 (태그 기반 추천)
