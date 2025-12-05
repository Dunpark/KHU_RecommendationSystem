# Phase 1 – Task 1.2: games.csv, users.csv 로드 및 검증

**작성일**: 2024.12.04  
**상태**: ✅ 완료

---

## 1. Task 목표

게임 메타데이터(`games.csv`)와 사용자 프로필(`users.csv`) 파일의 구조와 품질을 파악하고, Task 1.1의 `recommendations.csv`와 교차 검증

---

## 2. 실행 환경

- **실행 스크립트**: `task1_2_games_users_eda.py`
- **데이터 파일**: 
  - `Game Recommendations on Steam/games.csv`
  - `Game Recommendations on Steam/users.csv`

---

## 3. 핵심 결과

### 3.1 games.csv 분석

#### 기본 정보

| 항목 | 값 |
|------|-----|
| **총 행 수** | 50,872 |
| **유니크 app_id** | 50,872 |
| **컬럼 수** | 13개 |
| **Null 값** | 모든 컬럼 0% ✅ |

#### 컬럼 구조

| 컬럼 | 타입 | 설명 | 모델 활용 |
|------|------|------|----------|
| `app_id` | int64 | 게임 ID | Join Key |
| `title` | object | 게임 이름 | 참조용 |
| `date_release` | object | 출시일 | Content Feature |
| `win` | bool | Windows 지원 | Content Feature |
| `mac` | bool | Mac 지원 | Content Feature |
| `linux` | bool | Linux 지원 | Content Feature |
| `rating` | object | 평가 등급 | **Content Feature (핵심)** |
| `positive_ratio` | int64 | 긍정 비율 | **Content Feature (핵심)** |
| `user_reviews` | int64 | 총 리뷰 수 | **Popularity 지표** |
| `price_final` | float64 | 최종 가격 | Content Feature |
| `price_original` | float64 | 원래 가격 | (참조용) |
| `discount` | float64 | 할인율 | (참조용) |
| `steam_deck` | bool | Steam Deck 호환 | (선택적) |

#### rating 분포

| rating | 개수 | 비율 |
|--------|------|------|
| Positive | 13,502 | 26.5% |
| Very Positive | 13,139 | 25.8% |
| Mixed | 12,157 | 23.9% |
| Mostly Positive | 8,738 | 17.2% |
| Mostly Negative | 1,849 | 3.6% |
| Overwhelmingly Positive | 1,110 | 2.2% |
| Negative | 303 | 0.6% |
| Very Negative | 60 | 0.1% |
| Overwhelmingly Negative | 14 | 0.03% |

#### positive_ratio 통계

| 지표 | 값 |
|------|-----|
| 평균 | 77.1 |
| 중앙값 | 81.0 |
| 최소 | 0 |
| 최대 | 100 |

#### price_final 분포

| 구분 | 개수 | 비율 |
|------|------|------|
| 무료 게임 (price=0) | 9,105 | **17.9%** |
| 유료 게임 (price>0) | 41,767 | 82.1% |
| 평균 가격 (유료) | $10.50 | - |
| 최대 가격 | $299.99 | - |

#### user_reviews 분포 ⚠️

| 지표 | 값 |
|------|-----|
| 평균 | 1,824.4 |
| 중앙값 | **49.0** |
| 최대 | 7,494,460 |

```
평균(1,824) >> 중앙값(49) → 극단적인 Long-tail 분포
```

| 구간 | 게임 수 |
|------|---------|
| 0-10 | 2,566 |
| 11-100 | 30,132 |
| 101-1K | 12,862 |
| 1K-10K | 4,164 |
| 10K-100K | 1,011 |
| 100K+ | 137 |

#### 플랫폼 지원

| 플랫폼 | 지원 게임 수 | 비율 |
|--------|-------------|------|
| Windows | 50,076 | 98.4% |
| Mac | 13,018 | 25.6% |
| Linux | 9,041 | 17.8% |

---

### 3.2 users.csv 분석

#### 기본 정보

| 항목 | 값 |
|------|-----|
| **총 행 수** | 14,306,064 |
| **유니크 user_id** | 14,306,064 |
| **컬럼 수** | 3개 |
| **Null 값** | 모든 컬럼 0% ✅ |

#### 컬럼 구조

| 컬럼 | 타입 | 설명 | 모델 활용 |
|------|------|------|----------|
| `user_id` | int64 | 사용자 ID | Join Key |
| `products` | int64 | 보유 게임 수 | **User Activity 지표** |
| `reviews` | int64 | 작성 리뷰 수 | **User Engagement 지표** |

#### products (보유 게임 수) 통계

| 지표 | 값 |
|------|-----|
| 평균 | 116.4 |
| 중앙값 | 55.0 |
| 최소 | 0 |
| 최대 | 32,214 |

| 구간 | 사용자 수 | 비율 |
|------|----------|------|
| 1-10 | 1,511,254 | 10.6% |
| 11-50 | 5,078,003 | 35.5% |
| 51-100 | 3,062,706 | 21.4% |
| 101-500 | 4,029,247 | 28.2% |
| 501-1K | 357,403 | 2.5% |
| 1K+ | 128,133 | 0.9% |

#### reviews (작성 리뷰 수) 통계

| 지표 | 값 |
|------|-----|
| 평균 | 2.88 |
| 중앙값 | **1.0** |
| 최소 | 0 |
| 최대 | 6,045 |
| 리뷰 0개 | 525,005 (3.7%) |

| 구간 | 사용자 수 | 비율 |
|------|----------|------|
| 0 | 525,005 | 3.7% |
| 1 | 7,573,027 | **52.9%** |
| 2-5 | 4,733,023 | 33.1% |
| 6-10 | 889,778 | 6.2% |
| 11-50 | 549,615 | 3.8% |
| 51-100 | 27,421 | 0.2% |
| 100+ | 8,195 | 0.06% |

---

### 3.3 교차 검증

| 데이터 | games.csv / users.csv | recommendations.csv (Task 1.1) | 차이 |
|--------|----------------------|-------------------------------|------|
| **게임 수** | 50,872 | ~37,610 | +13,262 |
| **사용자 수** | 14,306,064 | ~13,781,059 | +525,005 |

**해석:**
- `games.csv`에는 상호작용 데이터가 없는 게임도 포함 (신규 게임, 비인기 게임)
- `users.csv`에는 추천 데이터가 없는 사용자도 포함 (리뷰 0개 사용자 3.7%)

---

## 4. 결과 해석

### 4.1 핵심 발견

#### 1️⃣ **games.csv: 극단적 Long-tail 분포 재확인**
```
user_reviews: 평균(1,824) >> 중앙값(49)
```
- 상위 137개 게임(100K+ 리뷰)이 전체 리뷰의 대부분을 차지
- 30,132개 게임(59%)이 11-100개의 리뷰만 보유
- → **RQ1 (Popular vs Long-tail)** 분석의 명확한 근거

#### 2️⃣ **users.csv: 대부분 리뷰 1개 사용자**
```
리뷰 1개 사용자: 7,573,027명 (52.9%)
리뷰 5개 이하: 12,831,055명 (89.7%)
```
- 90% 이상의 사용자가 5개 이하 리뷰
- Heavy users (10개 이상 리뷰): ~10%
- → **RQ2 (Heavy vs Light)** 분석에서 Light users가 절대 다수

#### 3️⃣ **긍정 편향: rating 분포**
```
Positive 이상: 72.3% (Positive + Very Positive + Mostly Positive + Overwhelmingly Positive)
Negative 이상: 4.4%
```
- Steam 게임 대부분이 긍정적 평가
- → `positive_ratio`를 Content Feature로 활용 시 유용

#### 4️⃣ **무료 게임 비율: 17.9%**
- 무료 게임이 상당 부분 차지
- → `price`를 Feature로 쓸 때 Binary (무료/유료) 변환 고려

### 4.2 연구 질문(RQ) 연결

| RQ | 시사점 |
|----|--------|
| **RQ1** | user_reviews 분포가 Long-tail → Popular 게임 편중 문제 확인 |
| **RQ2** | 90% 사용자가 리뷰 5개 이하 → Light users 대다수, Cold-start 심각 |
| **RQ3** | rating, positive_ratio가 유용한 Content Feature 후보 |

---

## 5. 다음 Task에 미치는 영향

### 5.1 데이터 병합 시 고려사항

1. **games.csv + recommendations.csv**: 
   - `app_id` 기준 Inner Join 시 ~37,610개 게임만 매칭
   - 나머지 ~13,000개는 상호작용 없는 게임

2. **users.csv + recommendations.csv**: 
   - `user_id` 기준 Inner Join 시 ~13,781,059명만 매칭
   - 나머지 ~500,000명은 리뷰 0개 사용자

### 5.2 Feature Engineering 계획

| Feature | 처리 방법 |
|---------|----------|
| `rating` | 순서형 인코딩 (Overwhelmingly Negative → Overwhelmingly Positive) |
| `positive_ratio` | 그대로 사용 (0-100 정규화) |
| `price_final` | Binary (무료/유료) 또는 구간화 |
| `user_reviews` | Log 변환 후 사용 (Long-tail 완화) |
| `products` | Heavy/Light 분류 기준으로 활용 |
| `reviews` | Heavy/Light 분류 기준으로 활용 |

### 5.3 Heavy/Light 사용자 분류 기준 제안

| 기준 | Heavy | Light | 근거 |
|------|-------|-------|------|
| **reviews 기준** | ≥ 10개 | < 10개 | 상위 ~10% |
| **products 기준** | ≥ 100개 | < 100개 | 중앙값 55 기준 |

---

## 6. 생성 파일

| 파일 | 경로 | 설명 |
|------|------|------|
| EDA 스크립트 | `task1_2_games_users_eda.py` | games/users 검증 코드 |

---

## 7. 체크리스트

- [x] games.csv 기본 정보 확인 (50,872 rows, 13 columns)
- [x] games.csv 컬럼별 분포 분석
- [x] games.csv Null 값 검증 (모두 0%)
- [x] users.csv 기본 정보 확인 (14,306,064 rows, 3 columns)
- [x] users.csv products/reviews 분포 분석
- [x] users.csv Null 값 검증 (모두 0%)
- [x] recommendations.csv와 교차 검증
- [x] Long-tail 분포 재확인
- [x] Heavy/Light 분류 기준 제안
- [x] 연구 질문과 연결한 해석

