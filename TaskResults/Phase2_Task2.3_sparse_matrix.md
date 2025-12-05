# Phase 2 – Task 2.3: Sparse Matrix 구축

**작성일**: 2024.12.05  
**상태**: ✅ 완료 (⚠️ 평가 전략 수정 필요)

---

## 1. Task 목표

Train 데이터를 기반으로 **User-Item Sparse Matrix** 구축 (CSR 포맷)

---

## 2. 실행 환경

- **실행 스크립트**: `task2_3_sparse_matrix.py`
- **입력 데이터**: `data_split/train_interactions.csv`

---

## 3. 핵심 결과

### 3.1 행렬 규모

| 항목 | 값 |
|------|-----|
| **사용자 수 (n_users)** | **11,024,847** |
| **아이템 수 (n_items)** | **37,530** |
| **행렬 크기** | 11,024,847 × 37,530 = **413B cells** |
| **실제 상호작용** | **32,922,924** |
| **희소율 (Sparsity)** | **99.992043%** |

### 3.2 Binary Matrix

| 항목 | 값 |
|------|-----|
| Shape | (11,024,847, 37,530) |
| Non-zero | 32,922,924 |
| Density | 0.007957% |
| Memory (data) | **125.59 MB** |

### 3.3 Weighted Matrix (Hours 가중치)

| 항목 | 값 |
|------|-----|
| Shape | (11,024,847, 37,530) |
| Non-zero | 32,922,924 |
| Weight 평균 | 4.391 |
| Weight 최소 | 1.000 |
| Weight 최대 | 7.909 |
| Memory (data) | **125.59 MB** |

```
가중치 공식: weight = 1 + log(1 + hours)
→ 0시간도 최소 1의 가중치
→ 플레이 시간이 길수록 높은 가중치 (로그 스케일)
```

### 3.4 저장된 파일

```
data_split/
├── train_sparse_binary.npz    (Binary Matrix)
├── train_sparse_weighted.npz  (Hours 가중치 Matrix)
├── id_mappings.pkl            (ID ↔ Index 매핑)
├── valid_indexed.csv          (Index 변환된 Valid)
└── test_indexed.csv           (Index 변환된 Test)
```

---

## 4. ⚠️ 중요 발견: 평가 전략 문제

### 4.1 Valid/Test Index 변환 결과

| 분할 | 원본 | 유효 (Train 사용자) | 제외 |
|------|------|-------------------|------|
| **Valid** | 4,110,632 | **0 (0.00%)** | 4,110,632 |
| **Test** | 4,121,223 | **0 (0.00%)** | 4,121,223 |

```
⚠️ 문제:
Task 2.2에서 사용자 기반 분할을 수행 → Valid/Test의 모든 사용자가 Train에 없음
→ CF 모델로 Valid/Test 평가 불가!
```

### 4.2 원인 분석

```
사용자 기반 분할 (Task 2.2):
- Train: 사용자 A, B, C의 모든 상호작용
- Valid: 사용자 D, E의 모든 상호작용
- Test: 사용자 F, G의 모든 상호작용

→ Valid/Test 사용자가 Train에 없음 (Cold User 100%)
→ User-based CF는 새로운 사용자 임베딩 생성 불가
→ Item-based CF도 사용자 프로파일 없이는 추천 불가
```

### 4.3 해결 방안 ⭐

#### 방안 1: Leave-One-Out 평가 (권장)
```python
# 각 사용자의 마지막 상호작용을 Test로 사용
# 나머지를 Train으로 사용
for user in users:
    train = user_interactions[:-1]
    test = user_interactions[-1]
```

#### 방안 2: 시간 기반 분할
```python
# 날짜 기준으로 분할 (같은 사용자도 시간에 따라 분리)
train = interactions[date < cutoff_date]
test = interactions[date >= cutoff_date]
```

#### 방안 3: 현재 분할 유지 + Content-based 평가
```
- CF 모델: 평가 불가 (Cold User)
- Content-based: 평가 가능 (사용자 무관)
- Popularity: 평가 가능 (사용자 무관)
- Hybrid: Content 부분만 평가 가능
```

---

## 5. 검증 결과

### 5.1 로드 테스트

| 항목 | 값 |
|------|-----|
| Binary Matrix Shape | (11,024,847, 37,530) |
| n_users | 11,024,847 |
| n_items | 37,530 |

### 5.2 샘플 사용자 확인

```
샘플 사용자 (idx=0, id=51580):
  - 상호작용 아이템 수: 5
  - 상호작용 아이템: [975370, 1817190, 379720, 590380, 1649080]
```

---

## 6. 모델링 시사점

### 6.1 현재 분할의 적합 모델

| 모델 | Train 학습 | Valid/Test 평가 | 적합 여부 |
|------|-----------|-----------------|----------|
| **Popularity** | ✅ 가능 | ✅ 가능 | **적합** |
| **Content-based** | ✅ 가능 | ✅ 가능 | **적합** |
| **User-based CF** | ✅ 가능 | ❌ 불가 | 부적합 |
| **Item-based CF** | ✅ 가능 | ⚠️ 제한적 | 부분 적합 |
| **ALS/BPR** | ✅ 가능 | ❌ 불가 | 부적합 |
| **Hybrid** | ✅ 가능 | ⚠️ Content만 | 부분 적합 |

### 6.2 권장 실험 전략

```
1단계: Popularity + Content-based로 Baseline 설정
       (현재 분할로 평가 가능)

2단계: CF 모델 평가를 위한 Leave-One-Out 분할 생성
       (Task 2.4에서 수행)

3단계: Hybrid 모델 실험
       (두 가지 분할 모두에서 평가)
```

---

## 7. ID 매핑 정보

### 7.1 매핑 딕셔너리

```python
# data_split/id_mappings.pkl 내용
{
    'user_to_idx': {user_id: idx, ...},  # 11,024,847개
    'idx_to_user': {idx: user_id, ...},
    'item_to_idx': {app_id: idx, ...},   # 37,530개
    'idx_to_item': {idx: app_id, ...},
    'n_users': 11024847,
    'n_items': 37530
}
```

### 7.2 사용 예시

```python
from scipy.sparse import load_npz
import pickle

# Sparse Matrix 로드
matrix = load_npz("data_split/train_sparse_binary.npz")

# 매핑 로드
with open("data_split/id_mappings.pkl", 'rb') as f:
    mappings = pickle.load(f)

# 사용자 ID → 인덱스 변환
user_idx = mappings['user_to_idx'][user_id]

# 해당 사용자의 상호작용 조회
user_interactions = matrix[user_idx].indices
```

---

## 8. 생성 파일

| 파일 | 경로 | 설명 |
|------|------|------|
| 스크립트 | `task2_3_sparse_matrix.py` | Sparse Matrix 구축 코드 |
| **Binary Matrix** | `data_split/train_sparse_binary.npz` | 상호작용 존재 여부 |
| **Weighted Matrix** | `data_split/train_sparse_weighted.npz` | Hours 가중치 |
| **ID 매핑** | `data_split/id_mappings.pkl` | ID ↔ Index |
| Valid (Index) | `data_split/valid_indexed.csv` | (빈 파일 - Cold User) |
| Test (Index) | `data_split/test_indexed.csv` | (빈 파일 - Cold User) |

---

## 9. 체크리스트

- [x] Train 데이터 로드
- [x] User/Item ID → Index 매핑 생성
- [x] Binary Sparse Matrix 생성 (CSR)
- [x] Weighted Sparse Matrix 생성 (Hours 가중치)
- [x] 파일 저장 (.npz, .pkl)
- [x] Valid/Test Index 변환
- [x] 로드 테스트 및 검증
- [x] ⚠️ 평가 전략 문제 식별

---

## 10. 다음 Task (2.4) 권장 작업

```
Task 2.4: 실험 데이터셋 최종 준비

1. Leave-One-Out 분할 추가 생성
   - 각 사용자의 마지막 상호작용을 Test로
   - CF 모델 평가용

2. 평가 함수 구현
   - Recall@K, NDCG@K, Coverage@K, Novelty
   - 파티션별 분리 평가

3. 실험 설정 정리
   - 하이퍼파라미터 그리드
   - 평가 시나리오별 데이터셋 매칭
```

