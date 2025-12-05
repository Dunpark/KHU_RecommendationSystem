# Phase 2 – Task 2.4: 실험 데이터셋 최종 준비

**작성일**: 2024.12.05  
**상태**: ✅ 완료

---

## 1. Task 목표

Leave-One-Out 분할 생성 + 평가 함수 구현 → CF 모델 평가 가능하게

---

## 2. 실행 환경

- **실행 스크립트**: `task2_4_experiment_setup.py`
- **분할 방식**: Leave-One-Out (각 사용자의 마지막 상호작용을 Test로)

---

## 3. 핵심 결과

### 3.1 Leave-One-Out 분할 결과 ⭐

| 항목 | 값 |
|------|-----|
| **LOO Train** | **21,898,092 rows** |
| **LOO Test** | **4,965,184 rows** → 유효: **4,964,722** (99.99%) |
| **사용자 수** | **4,965,184** |
| **아이템 수** | **37,251** |

```
분할 과정:
1. Train 데이터 (32.9M) → 날짜순 정렬
2. 각 사용자의 마지막 상호작용 → Test
3. 나머지 → Train
4. Train에 2개 이상 상호작용 있는 사용자만 유지
```

### 3.2 LOO Sparse Matrix

| 항목 | 값 |
|------|-----|
| Shape | (4,965,184, 37,251) |
| Non-zero | 21,898,078 |
| Density | 0.012% |

### 3.3 LOO Test 파티션 분포

| 그룹 | 비율 |
|------|------|
| **Popular × Light** | **38.79%** |
| **Popular × Heavy** | **24.02%** |
| **Long-tail × Light** | **19.44%** |
| **Long-tail × Heavy** | **17.75%** |

```
💡 발견:
- LOO Test에서 Popular 비율 (62.81%) > 원본 Train (60%)
- Light 사용자 비율 (58.23%) > Heavy (41.77%)
- Leave-One-Out 분할의 특성: 활동적 사용자의 마지막 상호작용은 Popular 경향
```

---

## 4. 저장된 파일

### 4.1 LOO 데이터셋

```
data_split/
├── loo_train.csv              (21.9M rows)
├── loo_test.csv               (4.97M rows)
├── loo_train_sparse.npz       (Sparse Matrix)
├── loo_mappings.pkl           (ID 매핑)
├── loo_test_indexed.csv       (Index 변환)
└── loo_test_with_partition.csv (파티션 포함)
```

### 4.2 평가 모듈

```
evaluation.py
├── recall_at_k()
├── ndcg_at_k()
├── coverage_at_k()
├── novelty_at_k()
├── evaluate_recommendations()
└── evaluate_by_partition()
```

---

## 5. 평가 함수 설명

### 5.1 Recall@K
```python
def recall_at_k(recommended, actual, k):
    """
    추천 목록 상위 K개 중 실제 선호 아이템 비율
    값: 0~1 (높을수록 좋음)
    """
```

### 5.2 NDCG@K
```python
def ndcg_at_k(recommended, actual, k):
    """
    Normalized Discounted Cumulative Gain
    순위를 고려한 추천 품질
    값: 0~1 (높을수록 좋음)
    """
```

### 5.3 Coverage@K
```python
def coverage_at_k(all_recommendations, all_items, k):
    """
    추천된 유니크 아이템 비율
    값: 0~1 (높을수록 다양한 추천)
    """
```

### 5.4 Novelty@K
```python
def novelty_at_k(all_recommendations, item_popularity, k):
    """
    추천 아이템의 평균 비인기도
    값: 높을수록 Long-tail 추천 많음
    """
```

### 5.5 평가 함수 테스트 결과

| 지표 | 값 |
|------|-----|
| Recall@5 | 0.3333 |
| Recall@10 | 0.6667 |
| NDCG@5 | 0.2346 |
| NDCG@10 | 0.3911 |

---

## 6. 실험 설정 요약

### 6.1 두 가지 평가 시나리오

| 시나리오 | 데이터셋 | 적합 모델 |
|----------|----------|----------|
| **Cold User 평가** | train/valid/test (Task 2.2) | Popularity, Content |
| **Leave-One-Out 평가** | loo_train/loo_test (Task 2.4) | CF, Hybrid |

### 6.2 평가 지표 (K=5, 10, 20)

| 지표 | 의미 | 목표 |
|------|------|------|
| **Recall@K** | 추천 정확도 | 높을수록 좋음 |
| **NDCG@K** | 순위 품질 | 높을수록 좋음 |
| **Coverage@K** | 다양성 | 높을수록 Long-tail 커버 |
| **Novelty@K** | 신선도 | 높을수록 Long-tail 추천 |

### 6.3 파티션별 분리 평가

```
1. 전체 평가: 모든 사용자 대상

2. 그룹별 평가:
   - Popular × Heavy: CF 신호 풍부
   - Popular × Light: 인기 게임 선호
   - Long-tail × Heavy: 다양한 취향
   - Long-tail × Light: Cold-start 심각

3. 비교 분석:
   - CF vs Content-based: 어느 그룹에서 우위?
   - Hybrid 가중치: 그룹별 최적 조합?
```

---

## 7. 연구 질문(RQ) 연결

| RQ | 평가 방법 |
|----|----------|
| **RQ1** | Long-tail 그룹에서 Recall@K, Coverage@K 비교 |
| **RQ2** | Light 사용자 그룹에서 CF vs Content 성능 비교 |
| **RQ3** | 그룹별 Hybrid 가중치 최적화 실험 |

---

## 8. Phase 2 완료 요약 ⭐

### 8.1 Phase 2 전체 Task

| Task | 내용 | 상태 |
|------|------|------|
| 2.1 | 파티션 교차 분석 | ✅ |
| 2.2 | Train/Valid/Test 분할 | ✅ |
| 2.3 | Sparse Matrix 구축 | ✅ |
| **2.4** | **실험 데이터셋 최종 준비** | ✅ |

### 8.2 Phase 2 산출물

```
data_split/
├── train_interactions.csv     (32.9M - Cold User 평가용 Train)
├── valid_interactions.csv     (4.1M - Cold User 평가용)
├── test_interactions.csv      (4.1M - Cold User 평가용)
├── train_sparse_binary.npz    (11M users - 전체 Train Matrix)
├── train_sparse_weighted.npz  (Hours 가중치)
├── id_mappings.pkl            (전체 ID 매핑)
├── loo_train.csv              (21.9M - LOO 평가용 Train)
├── loo_test.csv               (4.97M - LOO 평가용 Test)
├── loo_train_sparse.npz       (4.96M users - LOO Matrix)
├── loo_mappings.pkl           (LOO ID 매핑)
├── loo_test_indexed.csv       (LOO Test Index)
└── loo_test_with_partition.csv (LOO Test + 파티션)

evaluation.py                   (평가 함수)
```

---

## 9. Phase 3 준비 완료

### 9.1 다음 단계: Baseline 모델 구현

| 모델 | 설명 | 평가 데이터 |
|------|------|-----------|
| **Popularity** | 인기도 기반 추천 | 둘 다 가능 |
| **ItemKNN** | 아이템 유사도 기반 | LOO |
| **ALS** | Matrix Factorization | LOO |
| **BPR** | Bayesian Personalized Ranking | LOO |

### 9.2 실험 계획

```
Phase 3: Baseline 모델 (Popularity, ItemKNN, ALS)
Phase 4: Content-based 모델 (태그 기반 유사도)
Phase 5: Hybrid 모델 (CF + Content 결합)
Phase 6: 결과 종합 및 리포트
```

---

## 10. 체크리스트

- [x] Leave-One-Out 분할 생성
- [x] LOO Sparse Matrix 생성
- [x] LOO Test Index 변환
- [x] 파티션 정보 매핑
- [x] 평가 함수 구현 (evaluation.py)
- [x] 평가 함수 테스트
- [x] 실험 설정 요약
- [x] Phase 2 완료 확인

