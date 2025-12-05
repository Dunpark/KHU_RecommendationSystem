# Steam 게임 추천 시스템 프로젝트
## SPEC 주도 개발 기반 프로젝트 분석 계획서

---

# Part 1: 데이터 EDA 및 인사이트

## 1. 데이터셋 개요

### 1.1 Game Recommendations on Steam (메인 상호작용 데이터)

| 파일 | 크기 | 설명 |
|------|------|------|
| `recommendations.csv` | ~41,154,794 rows | **핵심 상호작용 데이터** (user-item implicit feedback) |
| `games.csv` | ~50,873 rows | 게임 기본 정보 |
| `users.csv` | ~14,305,965 rows | 사용자 프로필 정보 |
| `games_metadata.json` | ~50,000+ entries | 게임 태그 및 설명 |

#### 1.1.1 recommendations.csv (핵심)

| 컬럼 | 타입 | 설명 | 모델 활용 |
|------|------|------|----------|
| `app_id` | int64 | 게임 식별자 | 아이템 ID |
| `user_id` | int64 | 사용자 식별자 | 유저 ID |
| `is_recommended` | bool | 추천 여부 (True/False) | **Binary Implicit Feedback** |
| `hours` | float64 | 플레이 시간 | **Weighted Implicit Feedback** |
| `helpful` | int64 | 도움됨 투표 수 | (선택적) |
| `funny` | int64 | 재미있음 투표 수 | (선택적) |
| `date` | object | 리뷰 작성일 | 시간 기반 분석 |
| `review_id` | int64 | 리뷰 식별자 | (참조용) |

**핵심 인사이트:**
- **전체 상호작용**: 약 4,100만 건
- **유니크 게임**: 37,610개
- **유니크 사용자**: 13,781,059명
- **평균 density**: 0.0079% (매우 희소)

#### 1.1.2 games.csv

| 컬럼 | 타입 | 설명 | 모델 활용 |
|------|------|------|----------|
| `app_id` | int64 | 게임 식별자 | Join Key |
| `title` | object | 게임 이름 | 참조용 |
| `date_release` | object | 출시일 | Content Feature |
| `win/mac/linux` | bool | 플랫폼 지원 | Content Feature |
| `rating` | object | 평가 등급 (Very Positive 등) | Content Feature |
| `positive_ratio` | int64 | 긍정 비율 (0-100) | **Content Feature (핵심)** |
| `user_reviews` | int64 | 총 리뷰 수 | **Popularity 지표** |
| `price_final` | float64 | 최종 가격 | Content Feature |
| `discount` | float64 | 할인율 | (선택적) |
| `steam_deck` | bool | Steam Deck 호환 | (선택적) |

**핵심 인사이트:**
- **Rating 분포**: Very Positive(35%), Positive(25%), Mixed(20%), Mostly Positive(15%), 기타(5%)
- **가격 분포**: 무료 게임 ~15%, 유료 게임 ~85%
- **플랫폼**: Windows(99%+), Mac(~30%), Linux(~25%)

#### 1.1.3 games_metadata.json

| 필드 | 타입 | 설명 | 모델 활용 |
|------|------|------|----------|
| `app_id` | int | 게임 식별자 | Join Key |
| `description` | string | 게임 설명 | (선택적 - NLP) |
| `tags` | list[string] | 사용자 태그 목록 | **Content Feature (핵심)** |

**핵심 인사이트:**
- **평균 태그 수**: 게임당 ~12-15개
- **총 유니크 태그**: ~400+개
- **Top 10 태그**: Action, Indie, Adventure, Singleplayer, RPG, Strategy, Simulation, Casual, 2D, Atmospheric

#### 1.1.4 users.csv

| 컬럼 | 타입 | 설명 | 모델 활용 |
|------|------|------|----------|
| `user_id` | int64 | 사용자 식별자 | Join Key |
| `products` | int64 | 보유 게임 수 | **User Activity 지표** |
| `reviews` | int64 | 작성 리뷰 수 | **User Engagement 지표** |

**핵심 인사이트:**
- **평균 보유 게임**: ~150개
- **평균 리뷰 수**: ~3개
- **리뷰 미작성 사용자**: ~40%

---

### 1.2 Steam Games Dataset 2025 (메타데이터 확장)

| 파일 | 크기 | 설명 |
|------|------|------|
| `games_march2025_cleaned.csv` | ~90,000+ rows | 최신 Steam 게임 메타데이터 |
| `games_march2025_full.csv` | ~90,000+ rows | 전체 메타데이터 (상세) |

#### 주요 컬럼 (47개)

| 컬럼 그룹 | 컬럼들 | 모델 활용 |
|----------|--------|----------|
| **기본 정보** | appid, name, release_date, required_age | Join Key, Content |
| **가격** | price, discount | Content Feature |
| **플랫폼** | windows, mac, linux | Content Feature |
| **평가** | metacritic_score, positive, negative, pct_pos_total | **Content Feature (핵심)** |
| **인기도** | estimated_owners, recommendations, peak_ccu | **Popularity 지표** |
| **플레이타임** | average_playtime_forever, median_playtime_forever | **Engagement 지표** |
| **콘텐츠** | developers, publishers, categories, genres, tags | **Content Feature (핵심)** |
| **추가** | dlc_count, achievements, supported_languages | Content Feature |

**핵심 인사이트:**
- `estimated_owners`: "100000 - 200000" 형태의 구간 데이터 → **Long-tail 분류에 핵심**
- `tags`: 딕셔너리 형태 {'FPS': 90857, 'Shooter': 65397, ...} → **태그별 투표 수 포함**
- `genres`: ['Action', 'Free To Play'] 형태의 리스트
- `positive/negative`: 정확한 긍정/부정 리뷰 수 → **positive_ratio 직접 계산 가능**

---

## 2. 파티션 EDA 결과 (기존 분석 기반)

### 2.1 아이템 파티션: Popular vs Long-tail

#### 메인 기준: 누적 기여도 60%

```
┌─────────────────────────────────────────────────────────────┐
│                    아이템 분포 (Zipf's Law)                   │
│                                                             │
│  ██████████████████████████████████████████████████  100%   │
│  ██████████████████████████████████████████████████         │
│  ████████████████████████████████████████████████           │
│  ██████████████████████████████████████████████             │
│  ████████████████████████████████████████████               │
│  ██████████████████████████████████████████                 │
│  ████████████████████████████████████████   ← 60% 임계점     │
│  ██████████████████████████████████████                     │
│  ████████████████████████████████████                       │
│  ██████████████████████████████████                         │
│  ████████████████████████████████                           │
│  ██████████████████████████████   ← Long-tail 시작          │
│                                                             │
│  0          10         100        1000       37610          │
│              게임 순위 (상호작용 수 기준 내림차순)               │
└─────────────────────────────────────────────────────────────┘
```

| 파티션 | 게임 수 | 비율 | 설명 |
|--------|---------|------|------|
| **Popular** | 462개 | **1.2%** | 전체 상호작용의 60% 차지 |
| **Long-tail** | 37,148개 | **98.8%** | 나머지 40% 상호작용 |

**도메인 해석:**
- **Popular 462개**: CS2, Dota 2, PUBG, GTA V 등 "모두가 아는" 메가히트 게임
- **Long-tail 37,148개**: 인디 게임, 니치 장르, 오래된 게임 등
- **극단적 롱테일**: 상위 1.2%가 60%의 활동을 차지 → 전형적인 Pareto 분포

#### 서브 기준: 상위 20% Quantile

| 파티션 | 게임 수 | 비율 |
|--------|---------|------|
| **Popular** | 7,530개 | 20% |
| **Long-tail** | 30,080개 | 80% |

**용도**: 재현성 확보 및 비교 실험용

---

### 2.2 사용자 파티션: Heavy vs Light

#### 메인 기준: 누적 기여도 60%

```
┌─────────────────────────────────────────────────────────────┐
│                   사용자 활동 분포 (Power Law)                │
│                                                             │
│  상위 18%가                                                  │
│  전체 활동의 60% 차지  →  ┐                                  │
│                          │                                  │
│  ████████████████████████│█████████████████████████  100%   │
│  ██████████████████████  │                                  │
│  ████████████████████    │                                  │
│  ██████████████████      │← Heavy/Light 경계                │
│  ████████████████        │                                  │
│  ██████████████          │                                  │
│  ████████████            │                                  │
│  ██████████              │                                  │
│  ████████        ← Light users (sparse interactions)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| 파티션 | 사용자 수 | 비율 | 설명 |
|--------|-----------|------|------|
| **Heavy** | 2,472,972명 | **18%** | 전체 활동의 60% 차지 |
| **Light** | 11,308,087명 | **82%** | 나머지 40% 활동 (sparse) |

**도메인 해석:**
- **Heavy users**: 열성 게이머, 다양한 장르 경험, 많은 리뷰 작성
- **Light users**: 캐주얼 게이머, 제한된 게임 경험 → **Cold-start 문제의 핵심 대상**

#### 서브 기준: 상위 20% Quantile

| 파티션 | 사용자 수 | 비율 |
|--------|-----------|------|
| **Heavy** | 3,771,654명 | 27% |
| **Light** | 10,009,405명 | 73% |

---

### 2.3 파티션 기준 선정 근거

#### 왜 누적 기여도 60%인가?

1. **2024 최신 연구 기준**
   - LLM-Enhanced Collaborative Filtering (2024)
   - ESR (Exposure Sensitive Recommendation, 2024)
   - NeurIPS 2024 Debiasing Track
   - 위 논문들에서 "60% 기준이 popular-tail을 가장 안정적으로 분리"한다고 보고

2. **분포의 무릎(Knee Point)**
   - 누적 60%를 넘는 지점에서 변화율(curvature)이 급격히 감소
   - 자연스러운 분할 지점

3. **데이터 적응형**
   - 데이터가 변해도 자동으로 최적화
   - 인기게임이 10개든 500개든 알아서 분리

#### 왜 20% Quantile을 서브로 두는가?

1. **재현성**: 다른 연구자가 동일 값으로 재현 가능
2. **비교 가능성**: RecSys/NeurIPS 논문에서 baseline으로 많이 사용
3. **안정성**: 데이터 분포와 상관없이 고정 비율

---

## 3. 데이터 병합 전략

### 3.1 병합 스키마

```
┌────────────────────────────────────────────────────────────────────┐
│                         데이터 병합 파이프라인                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────┐                                               │
│  │recommendations  │                                               │
│  │    .csv        │──┐                                             │
│  │ (41M records)  │  │                                             │
│  └─────────────────┘  │                                            │
│                       │                                            │
│  ┌─────────────────┐  │     ┌──────────────────────┐               │
│  │   games.csv    │──┼────▶│  user_item_interactions │              │
│  │ (50K records)  │  │     │  (핵심 학습 데이터)       │              │
│  └─────────────────┘  │     └──────────────────────┘               │
│                       │              │                             │
│  ┌─────────────────┐  │              ▼                             │
│  │   users.csv    │──┘     ┌──────────────────────┐               │
│  │ (14M records)  │        │   games_features     │               │
│  └─────────────────┘        │  (아이템 피처 테이블)   │               │
│                             └──────────────────────┘               │
│  ┌─────────────────┐                 ▲                             │
│  │games_metadata  │─────────────────┘                             │
│  │    .json       │                                               │
│  │  (tags, desc)  │        ┌──────────────────────┐               │
│  └─────────────────┘        │   user_features      │               │
│                             │  (사용자 피처 테이블)   │               │
│  ┌─────────────────┐        └──────────────────────┘               │
│  │Steam 2025      │                 ▲                             │
│  │    .csv        │─────────────────┘                             │
│  │ (90K records)  │                                               │
│  └─────────────────┘                                               │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 3.2 최종 테이블 스키마

#### (1) user_item_interactions (학습용)

| 컬럼 | 출처 | 설명 |
|------|------|------|
| `user_id` | recommendations.csv | 사용자 ID |
| `app_id` | recommendations.csv | 게임 ID |
| `is_recommended` | recommendations.csv | 추천 여부 (1/0) |
| `hours` | recommendations.csv | 플레이 시간 |
| `timestamp` | recommendations.csv (date) | 상호작용 시점 |
| `user_partition` | 파생 | Heavy/Light |
| `item_partition` | 파생 | Popular/Long-tail |

#### (2) games_features (아이템 피처)

| 컬럼 | 출처 | 설명 |
|------|------|------|
| `app_id` | 공통 | 게임 ID (Join Key) |
| `title` | games.csv | 게임 이름 |
| `release_year` | games.csv | 출시 연도 |
| `price` | games.csv → Steam 2025 | 가격 |
| `positive_ratio` | games.csv | 긍정 비율 |
| `user_reviews` | games.csv | 리뷰 수 |
| `rating` | games.csv | 평가 등급 |
| `genres` | Steam 2025 | 장르 리스트 |
| `tags` | games_metadata.json | 태그 리스트 |
| `estimated_owners` | Steam 2025 | 추정 소유자 수 |
| `avg_playtime` | Steam 2025 | 평균 플레이타임 |
| `metacritic_score` | Steam 2025 | 메타크리틱 점수 |
| `win/mac/linux` | games.csv | 플랫폼 지원 |

#### (3) user_features (사용자 피처)

| 컬럼 | 출처 | 설명 |
|------|------|------|
| `user_id` | users.csv | 사용자 ID |
| `products` | users.csv | 보유 게임 수 |
| `reviews` | users.csv | 작성 리뷰 수 |
| `user_partition` | 파생 | Heavy/Light |
| `interaction_count` | 파생 | 총 상호작용 수 |

### 3.3 병합 우선순위 및 전략

| 우선순위 | 병합 | 키 | 목적 |
|----------|------|-----|------|
| 1 | recommendations + games.csv | app_id | 기본 아이템 정보 추가 |
| 2 | + games_metadata.json | app_id | 태그 정보 추가 |
| 3 | + Steam 2025 | appid | 확장 메타데이터 (owners, playtime 등) |
| 4 | + users.csv | user_id | 사용자 프로필 정보 |

**주의사항:**
- Steam 2025와 Game Recommendations의 app_id 매칭률 확인 필요
- 매칭되지 않는 게임은 기본값 처리 또는 제외 결정

---

# Part 2: 프로젝트 SPEC 및 절차 계획

## 1. 연구 질문 (Research Questions)

### RQ1: Popular vs Long-tail 성능 차이
> **"전통 CF, MF, 하이브리드 모델은 Popular 아이템과 Long-tail 아이템에서 어떤 성능 차이를 보이는가?"**

**가설:**
- H1-1: 전통 CF는 Popular 영역에서 우수, Long-tail에서 급격히 성능 저하
- H1-2: 하이브리드 모델은 Long-tail에서 CF 대비 개선
- H1-3: Content 비중이 높을수록 Long-tail 성능 향상

### RQ2: Heavy vs Light 사용자 성능 차이
> **"Heavy users와 Light users에서 어떤 모델이 더 안정적인 추천 품질을 보이는가?"**

**가설:**
- H2-1: CF는 Heavy users에서 강점, Light users에서 Cold-start 문제
- H2-2: Content-based는 Light users에서 상대적 강점
- H2-3: 하이브리드는 두 그룹 모두에서 안정적 성능

### RQ3: 메타데이터 기여도 분석
> **"장르, 태그, 가격, 평점 등 어떤 메타데이터가 추천 품질 향상에 가장 크게 기여하는가?"**

**가설:**
- H3-1: 태그(tags)가 가장 높은 기여도 (세분화된 선호 반영)
- H3-2: positive_ratio가 품질 필터 역할
- H3-3: 가격은 제한적 기여 (무료 게임이 많아서)

---

## 2. 모델 SPEC

### 2.1 Baseline 모델 (선행연구 기반)

| 모델 | 유형 | 선행연구 근거 | 구현 복잡도 |
|------|------|--------------|------------|
| **Popularity-based** | Non-personalized | 모든 RS 연구의 기본 baseline | ★☆☆☆☆ |
| **ItemKNN** | Memory-based CF | Salkanović(2024) Steam 연구 | ★★☆☆☆ |
| **UserKNN** | Memory-based CF | 전통 CF 비교용 | ★★☆☆☆ |
| **ALS (Implicit)** | Model-based CF | Hu et al.(2008), Steam 데이터 연구 | ★★★☆☆ |
| **BPR-MF** | Model-based CF | Rendle(2009), 최신 RS 서베이 | ★★★☆☆ |

### 2.2 Hybrid 모델

| 모델 | 유형 | 설명 | 선행연구 근거 |
|------|------|------|--------------|
| **MF + Metadata Fusion** | Feature-level | Latent vector + 메타데이터 concat | arXiv 2412.01378 |
| **Weighted Hybrid** | Score-level | α·CF + (1-α)·CB | Wang(2025) Steam 연구 |

### 2.3 모델 상세 SPEC

#### Baseline: Popularity-based
```
Input: 전체 상호작용 데이터
Process: 게임별 상호작용 수 집계 → 정렬
Output: 상위 K개 인기 게임 추천 (모든 사용자 동일)
```

#### Baseline: ItemKNN
```
Input: User-Item 행렬 (binary or weighted)
Similarity: Cosine Similarity
Process: 
  1. 아이템 간 유사도 계산
  2. 사용자가 상호작용한 아이템과 유사한 아이템 추천
Hyperparameters: K (이웃 수), similarity_metric
```

#### Baseline: ALS (Alternating Least Squares)
```
Input: User-Item 행렬 (implicit feedback)
Process:
  1. User/Item latent factor 초기화
  2. User factor 고정 → Item factor 최적화
  3. Item factor 고정 → User factor 최적화
  4. 수렴까지 반복
Hyperparameters: factors, regularization, iterations, alpha
```

#### Baseline: BPR-MF (Bayesian Personalized Ranking)
```
Input: User-Item 행렬 (implicit feedback)
Loss: BPR Loss (pairwise ranking)
Process:
  1. (user, pos_item, neg_item) 트리플 샘플링
  2. 양성 아이템 > 음성 아이템 순위 학습
Hyperparameters: factors, learning_rate, regularization, epochs
```

#### Hybrid 1: MF + Metadata Fusion
```
Input: User-Item 행렬 + Item 메타데이터
Process:
  1. MF로 User/Item latent vector 학습
  2. Item 메타데이터 → Feature vector (one-hot + embedding)
  3. Item representation = concat(MF_vector, metadata_vector)
  4. 최종 점수 = User_vector · Item_representation
```

#### Hybrid 2: Weighted Hybrid
```
Input: CF 모델 점수 + CB 모델 점수
Process:
  score(u, i) = α · score_CF(u, i) + (1-α) · score_CB(u, i)
Optimization:
  - 전체 최적 α 탐색
  - 파티션별 최적 α 탐색 (Popular vs Long-tail)
```

---

## 3. 평가 SPEC

### 3.1 평가 지표

| 지표 | 수식 | 설명 |
|------|------|------|
| **Recall@K** | TP / (TP + FN) | 실제 관련 아이템 중 추천된 비율 |
| **NDCG@K** | DCG@K / IDCG@K | 순위 품질 평가 |
| **Coverage@K** | \|추천된 아이템\| / \|전체 아이템\| | 추천 다양성 |

### 3.2 평가 분할

```
┌─────────────────────────────────────────────────────────────┐
│                       평가 매트릭스                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│              │     Popular Items    │   Long-tail Items   │
│  ────────────┼─────────────────────┼────────────────────  │
│  Heavy Users │   Recall@K, NDCG@K  │  Recall@K, NDCG@K   │
│              │   (CF 강점 예상)     │  (Hybrid 강점 예상)  │
│  ────────────┼─────────────────────┼────────────────────  │
│  Light Users │   Recall@K, NDCG@K  │  Recall@K, NDCG@K   │
│              │   (CB 필요 예상)     │  (가장 어려운 영역)  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Train/Test Split

```
방법: Time-based Split (시간순 분할)
- Train: 과거 80% 상호작용
- Test: 최근 20% 상호작용

또는

방법: Leave-Last-Out
- Train: 각 사용자의 마지막 상호작용 제외
- Test: 각 사용자의 마지막 상호작용
```

---

## 4. 프로젝트 절차 계획 (Develop 방식)

### Phase 1: 데이터 준비 및 EDA

```
Step 1.1: 데이터 로드 및 검증
├── recommendations.csv 로드 (chunked reading)
├── games.csv, users.csv, games_metadata.json 로드
├── Steam 2025 데이터 로드
└── 데이터 무결성 검증 (null, duplicates, types)

Step 1.2: 탐색적 데이터 분석
├── 상호작용 분포 분석 (user별, item별)
├── 시간 패턴 분석 (date 컬럼)
├── 메타데이터 분포 분석 (tags, genres, ratings)
└── 데이터 품질 리포트 생성

Step 1.3: 데이터 병합
├── app_id 기준 games.csv + metadata 병합
├── Steam 2025 확장 메타데이터 병합
├── 매칭률 확인 및 처리 전략 결정
└── 최종 통합 데이터셋 저장
```

**이전 단계 결과 활용:**
- EDA 인사이트 → 파티션 기준 결정
- 데이터 분포 → 전처리 전략 결정

---

### Phase 2: 파티션 정의 및 검증

```
Step 2.1: 아이템 파티션
├── 게임별 상호작용 수 집계
├── 누적 기여도 계산
├── Popular/Long-tail 분할 (60% 기준)
├── 서브 기준 분할 (20% quantile)
└── 파티션 통계 리포트

Step 2.2: 사용자 파티션
├── 사용자별 상호작용 수 집계
├── 누적 기여도 계산
├── Heavy/Light 분할 (60% 기준)
├── 서브 기준 분할 (20% quantile)
└── 파티션 통계 리포트

Step 2.3: 파티션 교차 분석
├── 2x2 파티션 매트릭스 생성
├── 각 셀의 데이터 특성 분석
├── 파티션 간 상호작용 패턴 비교
└── 연구 가설 검증을 위한 기초 분석
```

**이전 단계 결과 활용:**
- 병합된 데이터 → 정확한 파티션 계산
- EDA 인사이트 → 파티션 기준 근거

---

### Phase 3: Baseline 모델 구현 및 실험

```
Step 3.1: 데이터 전처리
├── User-Item 행렬 생성 (sparse matrix)
├── Train/Test 분할
├── 파티션별 데이터 분리
└── 평가 데이터셋 준비

Step 3.2: Baseline 모델 구현
├── Popularity-based 구현
├── ItemKNN 구현 (implicit library)
├── UserKNN 구현
├── ALS 구현 (implicit library)
└── BPR-MF 구현 (implicit library)

Step 3.3: Baseline 실험
├── 전체 데이터 성능 측정
├── 파티션별 성능 측정 (4개 셀)
├── 하이퍼파라미터 튜닝
└── 결과 기록 및 분석
```

**이전 단계 결과 활용:**
- 파티션 정의 → 분할 평가 기준
- EDA 인사이트 → 하이퍼파라미터 초기값

**핵심 분석 포인트:**
- Baseline의 한계 명확히 드러내기
- "왜 Popular에서 좋고 Long-tail에서 나쁜가?" 해석
- "왜 Heavy users에서 좋고 Light users에서 나쁜가?" 해석

---

### Phase 4: Content-based 모델 구현

```
Step 4.1: 피처 엔지니어링
├── 태그 벡터화 (multi-hot encoding)
├── 장르 벡터화
├── 수치형 피처 정규화 (price, rating 등)
├── 피처 결합 (concat or weighted)
└── 피처 중요도 분석

Step 4.2: Content-based 모델 구현
├── Item-Item 유사도 계산 (cosine)
├── 사용자 프로필 구축 (상호작용 아이템 평균)
├── User-Item 점수 계산
└── Top-K 추천 생성

Step 4.3: Content-based 실험
├── 전체 데이터 성능 측정
├── 파티션별 성능 측정
├── Baseline 대비 성능 비교
└── 피처 ablation study
```

**이전 단계 결과 활용:**
- Baseline 결과 → CB가 보완해야 할 영역 확인
- 파티션 분석 → Long-tail/Light users 집중 분석

**핵심 분석 포인트:**
- "어떤 메타데이터가 가장 기여하는가?" (RQ3)
- "Long-tail에서 CB의 장점이 드러나는가?"

---

### Phase 5: Hybrid 모델 구현 및 실험

```
Step 5.1: MF + Metadata Fusion
├── MF latent vector 추출
├── 메타데이터 벡터 생성
├── Feature fusion 구현 (concat)
├── 최종 모델 학습
└── 성능 평가

Step 5.2: Weighted Hybrid
├── CF 점수 생성 (best baseline)
├── CB 점수 생성
├── α 파라미터 그리드 서치
├── 전체 최적 α 탐색
└── 파티션별 최적 α 탐색

Step 5.3: Hybrid 실험
├── 전체 데이터 성능 측정
├── 파티션별 성능 측정
├── Baseline/CB 대비 성능 비교
├── 파티션별 최적 α 분석
└── 결과 해석 및 인사이트 도출
```

**이전 단계 결과 활용:**
- Baseline 결과 → CF 점수로 활용
- CB 결과 → CB 점수로 활용
- 파티션 분석 → α 튜닝 전략

**핵심 분석 포인트:**
- "Long-tail에서 α를 어떻게 조절해야 하는가?"
- "Popular에서 CF 비중이 높을 때 성능이 좋은가?"
- Wang(2025) 가설 검증: "Long-tail → CB 비중↑, Popular → CF 비중↑"

---

### Phase 6: 결과 분석 및 해석

```
Step 6.1: 종합 성능 비교
├── 모델별 전체 성능 테이블
├── 파티션별 성능 히트맵
├── 통계적 유의성 검정
└── 최고 성능 모델 선정

Step 6.2: 연구 질문 답변
├── RQ1: Popular vs Long-tail 분석
├── RQ2: Heavy vs Light 분석
├── RQ3: 메타데이터 기여도 분석
└── 가설 검증 결과 정리

Step 6.3: 도메인 해석
├── "왜 이런 결과가 나왔는가?" 해석
├── Steam 게임 도메인 특성 연결
├── 실무 적용 시사점 도출
└── 한계점 및 향후 연구 방향

Step 6.4: 시각화 및 리포트
├── 성능 비교 차트
├── 파티션별 분석 차트
├── α 최적화 분석 차트
└── 최종 발표 자료 준비
```

**이전 단계 결과 활용:**
- 모든 실험 결과 → 종합 분석
- EDA 인사이트 → 결과 해석 근거
- 선행연구 → 비교 및 차별화 포인트

---

## 5. 예상 일정 (Milestone)

| Phase | 기간 | 산출물 |
|-------|------|--------|
| **Phase 1** | - | 통합 데이터셋, EDA 리포트 |
| **Phase 2** | - | 파티션 정의 파일, 파티션 분석 리포트 |
| **Phase 3** | - | Baseline 모델 코드, 실험 결과 |
| **Phase 4** | - | CB 모델 코드, 피처 분석 결과 |
| **Phase 5** | - | Hybrid 모델 코드, α 최적화 결과 |
| **Phase 6** | - | 최종 분석 리포트, 발표 자료 |

---

## 6. 조교님 피드백 반영 체크리스트

- [ ] **Baseline 다양화**: Popularity, ItemKNN, UserKNN, ALS, BPR 5개 구현
- [ ] **결과 해석 중심**: 각 Phase에 "핵심 분석 포인트" 명시
- [ ] **파티션 기준 근거**: Part 1에 상세 근거 문서화

---

## 7. 선행연구 반영 매핑

| 선행연구 | 반영 내용 |
|----------|----------|
| **arXiv 2405.05562** (Review-based RS Survey) | 리뷰 데이터 활용, Representation Learning 개념 |
| **arXiv 2412.01378** (DNN-CF Survey) | Feature Fusion 구조, MF + Metadata |
| **Salkanović(2024)** (Steam Diversity) | KNN baseline, Long-tail 다양성 문제의식 |
| **Wang(2025)** (Weighted Hybrid) | α 파라미터 파티션별 최적화 전략 |
| **MDPI 2024** (RS Applications) | 데이터 소스 통합, 실무 관점 |

---

# Part 3: 기대 결과 및 인사이트

## 1. 예상 결과 패턴

### RQ1 예상 결과
```
┌────────────────────────────────────────────────────────┐
│                 Popular vs Long-tail 성능             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  NDCG@10  │  Popular  │  Long-tail  │  Gap            │
│  ─────────┼───────────┼─────────────┼───────────────  │
│  Popularity   0.15       0.02         -87%            │
│  ItemKNN      0.18       0.04         -78%            │
│  ALS          0.22       0.06         -73%            │
│  CB           0.12       0.08         -33%  ← 격차 감소│
│  Hybrid       0.20       0.10         -50%  ← 균형    │
│                                                        │
│  → Long-tail에서 Hybrid가 CF 대비 개선 확인            │
│  → CB가 Long-tail 성능 보완 역할                      │
└────────────────────────────────────────────────────────┘
```

### RQ2 예상 결과
```
┌────────────────────────────────────────────────────────┐
│                 Heavy vs Light 사용자 성능             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Recall@10 │  Heavy   │  Light   │  Gap               │
│  ──────────┼──────────┼──────────┼──────────────────  │
│  ALS          0.15       0.05      -67%               │
│  CB           0.08       0.06      -25%  ← 격차 감소  │
│  Hybrid       0.12       0.08      -33%  ← 균형       │
│                                                        │
│  → Light users에서 CB 비중 높이면 성능 향상           │
│  → Cold-start 문제 완화 효과 확인                     │
└────────────────────────────────────────────────────────┘
```

### RQ3 예상 결과: Feature Importance
```
┌────────────────────────────────────────────────────────┐
│                 메타데이터 기여도 순위                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1위: tags (태그)           ████████████████  +8.5%    │
│  2위: genres (장르)         ████████████      +6.2%    │
│  3위: positive_ratio        ██████████        +4.8%    │
│  4위: release_year          ████████          +3.1%    │
│  5위: price                 ████              +1.2%    │
│                                                        │
│  → 태그가 가장 높은 기여 (사용자 취향 세분화)           │
│  → 가격은 제한적 기여 (무료 게임 많음)                 │
└────────────────────────────────────────────────────────┘
```

## 2. 도메인 해석 프레임

### Steam 게임 도메인 특성
1. **극단적 롱테일**: 상위 1.2%가 60% 점유 → Popularity Bias 심각
2. **다양한 장르**: 400+ 태그 → Content 기반 세분화 가능
3. **플레이타임 차이**: 장르별 평균 플레이타임 큰 차이
4. **무료 게임 영향**: F2P 게임이 인기 상위권 다수 차지

### 결과 해석 가이드
- **Popular + Heavy**: "메가히트 게임을 즐기는 열성 게이머"
  - CF가 잘 작동 (풍부한 상호작용 데이터)
  
- **Popular + Light**: "인기 게임만 가볍게 즐기는 캐주얼 게이머"
  - CF 성능 하락, CB 보완 필요
  
- **Long-tail + Heavy**: "다양한 인디/니치 게임을 탐험하는 마니아"
  - CB 기반 추천이 효과적

- **Long-tail + Light**: "특정 니치 장르만 즐기는 사용자"
  - 가장 어려운 영역, Hybrid 필수

---

*문서 버전: v1.0*
*작성일: 2024.12.04*
*프로젝트: 경희대학교 빅데이터응용학과 추천시스템 수업*

