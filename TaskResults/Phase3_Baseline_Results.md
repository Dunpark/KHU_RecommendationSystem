# Phase 3 – Baseline 모델 실험 결과

**작성일**: 2024.12.05  
**상태**: ✅ 완료

---

## 1. Task 목표

다양한 Baseline 모델을 구현하고 성능을 비교하여 **추천 성능의 기준선** 확립

---

## 2. 구현 모델 요약

| 모델 | 유형 | 상태 | 선행연구 근거 |
|------|------|------|-------------|
| **Popularity** | Non-personalized | ✅ | 모든 RS 연구의 기본 baseline |
| **Random** | Non-personalized | ✅ | 하한선 측정용 |
| **PopularPerTag** | Semi-personalized | ✅ | Wang(2025) 파티션별 전략 확장 |
| **TruncatedSVD** | Matrix Factorization | ✅ | Salkanović(2024) SVD 효과성 |
| **CoOccurrence** | Memory-based CF | ✅ | Amazon/Netflix 검증 방식 |

---

## 3. 모델 선정 이유 ⭐

### 3.1 Random Baseline

```
선정 이유:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 가장 단순한 baseline으로 하한선(lower bound) 역할
2. 다른 모델이 "무작위보다 얼마나 좋은가?" 측정 기준
3. 모든 추천시스템 연구에서 기본적으로 포함하는 baseline

역할:
- "최소한 Random보다는 좋아야 한다"는 기준 제공
- 우연히 맞출 확률 = 10 / 37,251 ≈ 0.03%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3.2 Most Popular per Tag

```
선정 이유:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 선행연구 착안: Wang(2025)의 "파티션별 Popularity" 개념 확장
2. 순수 Popularity보다 약간의 개인화 제공
3. 태그 데이터 활용 (97.6% 게임에 태그 존재, 평균 12.8개)
4. Long-tail 커버리지 향상 기대 (태그별 분산)

특징:
- Content 정보(태그)를 활용한 Popularity 변형
- Phase 4 (Content-based)와의 자연스러운 연결
- "태그별로 다양한 인기 게임" 추천 → Coverage 향상 기대
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3.3 TruncatedSVD

```
선정 이유:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. sklearn 기본 제공 → 설치 문제 없음
2. ALS와 유사한 Matrix Factorization 개념
3. 대규모 Sparse Matrix에서 매우 빠름
4. 선행연구 착안: Salkanović(2024)에서 SVD 계열이 Steam 데이터에 효과적

특징:
- CF 계열 baseline으로 "협업 신호"의 효과 측정
- User/Item Latent Factors 학습
- n_components=50으로 차원 축소
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3.4 Item Co-occurrence

```
선정 이유:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. "이 게임을 한 사람들은 이 게임도 했습니다" (Amazon, Netflix 검증)
2. ItemKNN과 유사하지만 계산이 훨씬 간단
3. Top-K Co-occurrence만 저장하여 메모리 효율적
4. Steam 데이터에서 직관적 (같이 플레이 = 유사한 취향)

특징:
- 사용자 그룹의 집단 지성 반영
- ItemKNN의 효율적 근사
- 17,908개 아이템에 대해 Co-occurrence 계산
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 4. 실험 결과 ⭐⭐⭐

### 4.1 전체 결과 표

| 모델 | Recall@5 | Recall@10 | Recall@20 | NDCG@10 | Coverage@5 |
|------|----------|-----------|-----------|---------|------------|
| **Random** | 0.0000 | 0.0002 | 0.0008 | 0.0001 | **0.7398** |
| **Popularity** | 0.0279 | 0.0450 | 0.0746 | 0.0220 | 0.0003 |
| **PopularPerTag** | 0.0279 | 0.0450 | 0.0746 | 0.0220 | 0.0057 |
| **TruncatedSVD** | 0.0274 | 0.0443 | 0.0740 | 0.0217 | 0.0035 |
| **CoOccurrence** | **0.0292** | **0.0513** | **0.0898** | **0.0242** | 0.0061 |

### 4.2 시각적 비교

```
Recall@10 순위:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. CoOccurrence  ████████████████████████████  0.0513  [Best]
2. Popularity    ██████████████████████        0.0450
3. PopularPerTag ██████████████████████        0.0450
4. TruncatedSVD  █████████████████████         0.0443
5. Random        █                             0.0002  [Baseline]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Coverage@5 순위:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Random        ████████████████████████████  73.98%  (무의미)
2. CoOccurrence  ██                            0.61%   [Best]
3. PopularPerTag █                             0.57%
4. TruncatedSVD  █                             0.35%
5. Popularity    ▏                             0.03%   [Worst]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. 결과 해석 ⭐⭐⭐

### 5.1 Random Baseline 분석

```
결과:
- Recall@10 = 0.0002 (0.02%)
- Coverage@5 = 73.98%

해석:
- 예상대로 Recall이 거의 0 (무작위 추천)
- Coverage가 높은 이유: 무작위로 다양한 아이템 선택
- 핵심: 다른 모델들이 Random보다 225배 이상 좋음 (0.0450 / 0.0002)
  → 모델들이 의미 있는 추천을 하고 있음을 확인
```

### 5.2 Popularity vs PopularPerTag

```
결과:
- Recall@10: 둘 다 0.0450 (동일)
- Coverage@5: Popularity 0.03% vs PopularPerTag 0.57% (19배 향상!)

해석:
- Recall은 동일하지만 Coverage가 크게 향상
- 태그별 다양한 인기 게임을 추천하므로 다양성 확보
- Long-tail 커버리지 개선 효과 확인

시사점:
- 단순히 "태그 정보 추가"만으로 다양성 향상 가능
- Content 정보 활용의 가치 확인
```

### 5.3 TruncatedSVD 분석

```
결과:
- Recall@10 = 0.0443 (Popularity 대비 약간 낮음)
- Coverage@5 = 0.35%

해석:
- Latent Factor 기반 추천이 Popularity와 비슷한 성능
- 샘플링 학습 (50K users)으로 인한 성능 제한 가능성
- Coverage가 Popularity보다 높지만 기대만큼은 아님

시사점:
- MF 계열 모델이 작동하지만 Popularity를 크게 능가하지 못함
- 데이터의 극단적 Long-tail 분포가 MF 성능에 영향
```

### 5.4 CoOccurrence 분석 ⭐ (Best Performance)

```
결과:
- Recall@10 = 0.0513 (전체 최고, Popularity 대비 +14%)
- Recall@20 = 0.0898 (Popularity 대비 +20%)
- Coverage@5 = 0.61% (Popularity 대비 20배!)

해석:
- "같이 플레이한 게임" 기반 추천이 가장 효과적
- 협업 신호를 효과적으로 활용
- Coverage도 가장 높음 (Random 제외)

성공 요인:
1. 실제 사용자 행동 패턴 반영 (집단 지성)
2. 아이템 간 관계를 직접적으로 모델링
3. Steam 도메인에 적합 (게임 조합 플레이 패턴)
```

---

## 6. 핵심 발견 정리

### 6.1 성능 순위

```
Recall@10 기준:
1위: CoOccurrence (0.0513) - CF 계열 승리
2위: Popularity/PopularPerTag (0.0450) - 동률
3위: TruncatedSVD (0.0443)
5위: Random (0.0002) - 하한선

Coverage@5 기준 (Random 제외):
1위: CoOccurrence (0.61%)
2위: PopularPerTag (0.57%)
3위: TruncatedSVD (0.35%)
4위: Popularity (0.03%)
```

### 6.2 모델 유형별 특성

| 유형 | 대표 모델 | Recall | Coverage | 특징 |
|------|----------|--------|----------|------|
| **CF (협업)** | CoOccurrence | 최고 | 높음 | 협업 신호 효과적 |
| **Popularity** | Popularity | 중간 | 최저 | 인기 편향 심각 |
| **Content** | PopularPerTag | 중간 | 중간 | 다양성 향상 |
| **MF** | TruncatedSVD | 중간 | 중간 | 잠재 요인 학습 |

### 6.3 연구 질문(RQ) 연결

| RQ | 이번 실험에서 확인된 내용 |
|----|------------------------|
| **RQ1** | Popularity 모델의 Coverage 0.03% → Long-tail 추천 불가 확인 |
| **RQ2** | CoOccurrence가 CF 신호 활용에 효과적 |
| **RQ3** | 태그 정보(PopularPerTag)가 Coverage 향상에 기여 |

---

## 7. Phase 4 연결 시사점

### 7.1 Content-based 모델 필요성

```
현재 문제:
- 최고 모델(CoOccurrence)도 Coverage 0.61% (227개 아이템만 추천)
- 전체 37,251개 중 99.4%는 추천 기회 없음

해결 방향:
- Content-based로 아이템 유사도 계산
- 태그 기반 추천으로 Long-tail 커버리지 확보
- PopularPerTag의 19배 Coverage 향상 효과 확대
```

### 7.2 Hybrid 모델 설계 방향

```
최적 조합 예상:
- CF 신호 (CoOccurrence): Recall 최적화
- Content 신호 (태그 유사도): Coverage 최적화

score(u, i) = α · CoOccur(u, i) + (1-α) · ContentSim(u, i)

그룹별 α 예상:
- Popular × Heavy: α ≈ 0.8 (CF 중심)
- Long-tail × Light: α ≈ 0.2 (Content 중심)
```

---

## 8. 생성 파일

| 파일 | 설명 |
|------|------|
| `models/baseline_models.py` | 4개 모델 구현 코드 |
| `models/baseline_results.pkl` | 평가 결과 저장 |
| `models/popularity_model.py` | Popularity 모델 |
| `models/popularity_model.pkl` | 학습된 Popularity 모델 |

---

## 9. 체크리스트

- [x] Random Baseline 구현 및 평가
- [x] Most Popular per Tag 구현 및 평가
- [x] TruncatedSVD 구현 및 평가
- [x] Item Co-occurrence 구현 및 평가
- [x] 모델별 선정 이유 명시
- [x] 결과 비교 및 해석
- [x] RQ와 연결한 분석
- [x] Phase 4 시사점 도출

---

## 10. 결론

```
Phase 3 핵심 결론:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Best Baseline: CoOccurrence
   - Recall@10 = 0.0513 (Popularity 대비 +14%)
   - Coverage@5 = 0.61% (Popularity 대비 20배)
   - CF 신호의 효과성 확인

2. 태그 활용 효과: PopularPerTag
   - Recall은 동일하지만 Coverage 19배 향상
   - Content 정보의 다양성 기여 확인

3. Long-tail 문제 지속:
   - 최고 모델도 Coverage 0.61% (227개 아이템만)
   - Content-based 모델로 추가 개선 필요

4. Phase 4 방향:
   - 태그 기반 Content-based로 Coverage 확대
   - CoOccurrence + Content Hybrid 실험
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

*Phase 3 완료 – Phase 4 (Content-based) 진행 예정*
