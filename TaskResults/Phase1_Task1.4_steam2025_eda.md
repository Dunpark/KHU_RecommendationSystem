# Phase 1 – Task 1.4: Steam 2025 데이터 로드 및 매칭 분석

**작성일**: 2024.12.04  
**상태**: ✅ 완료

---

## 1. Task 목표

Steam Games Dataset 2025의 확장 메타데이터를 분석하고, 기존 `games.csv`와의 매칭률 확인

---

## 2. 실행 환경

- **실행 스크립트**: `task1_4_steam2025_eda.py`
- **데이터 파일**: `Steam Games Dataset 2025/games_march2025_cleaned.csv`

---

## 3. 핵심 결과

### 3.1 기본 정보

| 항목 | 값 |
|------|-----|
| **총 게임 수** | 89,618 |
| **유니크 appid** | 89,618 |
| **컬럼 수** | **47개** |
| **Null 값** | 핵심 컬럼 모두 0% ✅ |

### 3.2 컬럼 목록 (47개)

```
기본 정보: appid, name, release_date, required_age, price, dlc_count
설명: detailed_description, about_the_game, short_description, reviews
이미지/링크: header_image, website, support_url, support_email
플랫폼: windows, mac, linux
평가: metacritic_score, metacritic_url, achievements, recommendations, notes
언어: supported_languages, full_audio_languages
패키지: packages
제작: developers, publishers
분류: categories, genres
미디어: screenshots, movies
평점: user_score, score_rank, positive, negative
소유: estimated_owners
플레이타임: average_playtime_forever, average_playtime_2weeks, median_playtime_forever, median_playtime_2weeks
기타: discount, peak_ccu, tags
최근 평가: pct_pos_total, num_reviews_total, pct_pos_recent, num_reviews_recent
```

### 3.3 games.csv와 매칭 분석 ⚠️

| 항목 | 값 |
|------|-----|
| Steam 2025 appid 수 | 89,618 |
| games.csv app_id 수 | 50,872 |
| **공통 app_id** | **35,876** |
| **games.csv 기준 매칭률** | **70.5%** |
| Steam 2025에만 있음 | 53,742 |
| games.csv에만 있음 | 14,996 |

```
⚠️ 주의: games.csv의 29.5% (14,996개)가 Steam 2025에 없음
→ 이 게임들은 Steam 2025 확장 피처 사용 불가
```

### 3.4 estimated_owners 분포 (Long-tail 핵심 지표)

| 소유자 구간 | 게임 수 | 비율 | 분류 |
|------------|---------|------|------|
| 0 - 0 | 8,418 | 9.4% | 데이터 없음 |
| **0 - 20,000** | **59,320** | **66.2%** | **Long-tail** |
| 20,000 - 50,000 | 9,683 | 10.8% | Long-tail |
| 50,000 - 100,000 | 4,552 | 5.1% | Mid-tier |
| 100,000 - 200,000 | 3,005 | 3.4% | Mid-tier |
| 200,000 - 500,000 | 2,469 | 2.8% | Mid-tier |
| 500,000 - 1,000,000 | 1,038 | 1.2% | Popular |
| 1,000,000 - 2,000,000 | 574 | 0.6% | Popular |
| 2,000,000+ | 558 | 0.6% | **Mega Popular** |

```
Long-tail (< 50K owners): 77,421개 (86.4%)
Popular (≥ 500K owners): 2,171개 (2.4%)
→ 전형적인 Long-tail 분포 확인
```

### 3.5 positive/negative (리뷰 평점) 분석

| 지표 | 값 |
|------|-----|
| total_reviews 평균 | 1,479.7 |
| total_reviews 중앙값 | **13.0** |
| total_reviews 최대 | 8,615,921 |
| positive_ratio 평균 | 75.4% |
| positive_ratio 중앙값 | 81.4% |

```
평균(1,479) >> 중앙값(13) → 극단적 Long-tail
대부분의 게임이 13개 이하의 리뷰만 보유
```

### 3.6 playtime 분석 ⚠️

| 지표 | 값 |
|------|-----|
| average_playtime 평균 | 1.9시간 |
| average_playtime 중앙값 | **0.0시간** |
| average_playtime 최대 | 24,383.3시간 |
| **0시간 게임 비율** | **91.1%** |

```
⚠️ 91.1%의 게임이 average_playtime = 0
→ 대부분의 게임에 플레이타임 데이터 없음
→ playtime 피처는 Popular 게임에만 유효
```

### 3.7 매칭된 게임의 피처 품질

| 피처 | Null 비율 |
|------|----------|
| estimated_owners | 0.0% ✅ |
| positive | 0.0% ✅ |
| negative | 0.0% ✅ |
| average_playtime_forever | 0.0% ✅ |
| genres | 0.0% ✅ |
| tags | 0.0% ✅ |

---

## 4. 결과 해석

### 4.1 핵심 발견

#### 1️⃣ **매칭률 70.5% - 보완 전략 필요**
```
games.csv 50,872개 중 35,876개만 Steam 2025와 매칭
나머지 14,996개 (29.5%)는 확장 피처 사용 불가
```
- **해결 방안**: 매칭되지 않는 게임은 games.csv + metadata.json 피처만 사용
- **Hybrid 모델 설계 시 고려**: 피처 가용성에 따른 가중치 조절

#### 2️⃣ **estimated_owners로 Long-tail 분류 가능**
```
< 50K owners: 86.4% → Long-tail
≥ 500K owners: 2.4% → Popular
```
- `estimated_owners`는 Long-tail/Popular 분류의 **직접적 지표**
- 기존 `user_reviews` 기반 분류와 **교차 검증** 가능

#### 3️⃣ **playtime 피처의 한계**
```
91.1%의 게임이 playtime = 0
```
- 대부분의 게임에 playtime 데이터 없음
- **Popular 게임에서만 유효**한 피처
- Long-tail 분석에는 사용 제한

#### 4️⃣ **리뷰 수 극단적 Long-tail**
```
total_reviews: 평균 1,479 vs 중앙값 13 (114배 차이)
```
- `games.csv`의 user_reviews보다 더 극단적인 분포
- 상위 게임들이 리뷰 수를 압도적으로 끌어올림

### 4.2 연구 질문(RQ) 연결

| RQ | 시사점 |
|----|--------|
| **RQ1** | estimated_owners로 Popular/Long-tail 직접 분류 가능 |
| **RQ2** | playtime 91% 결측 → Heavy/Light 분류에는 recommendations.csv의 hours 사용 |
| **RQ3** | 매칭률 70.5% → 전체 게임에 적용 불가, 부분적 활용 |

---

## 5. 다음 Task에 미치는 영향

### 5.1 데이터 병합 전략 수정

| 게임 그룹 | 개수 | 사용 가능 피처 |
|----------|------|---------------|
| **매칭된 게임** | 35,876 (70.5%) | games.csv + metadata + Steam 2025 전체 |
| **매칭 안 된 게임** | 14,996 (29.5%) | games.csv + metadata만 |

### 5.2 Steam 2025에서 가져올 핵심 피처

| 피처 | 용도 | 우선순위 |
|------|------|---------|
| `estimated_owners` | Long-tail 분류 교차 검증 | ⭐⭐⭐ |
| `positive`, `negative` | 정확한 positive_ratio 계산 | ⭐⭐⭐ |
| `genres` | 장르 피처 보강 | ⭐⭐ |
| `developers`, `publishers` | 추가 Content 피처 | ⭐ |
| `average_playtime_forever` | (Popular 게임만) | ⭐ |

### 5.3 병합 시 주의사항

1. **app_id 기준 Left Join** (games.csv 기준)
2. 매칭되지 않는 14,996개 → Null 처리 또는 기본값
3. **estimated_owners 파싱**: "0 - 20000" 형태 → 숫자 변환 필요

---

## 6. 생성 파일

| 파일 | 경로 | 설명 |
|------|------|------|
| EDA 스크립트 | `task1_4_steam2025_eda.py` | Steam 2025 분석 코드 |

---

## 7. 체크리스트

- [x] Steam 2025 컬럼 구조 파악 (47개)
- [x] 기본 통계 확인 (89,618 게임)
- [x] games.csv 매칭률 확인 (70.5%)
- [x] estimated_owners 분포 분석 (Long-tail 86.4%)
- [x] positive/negative 분석
- [x] playtime 분석 (91.1% 결측 ⚠️)
- [x] 매칭된 게임 피처 품질 확인
- [x] 병합 전략 수립
- [x] 연구 질문과 연결한 해석

