# -*- coding: utf-8 -*-
"""
Phase 1 - Task 1.5: 상호작용 분포 EDA (Zipf's Law 확인)
"""
import pandas as pd
import numpy as np
from collections import Counter

print("=" * 70)
print("Phase 1 - Task 1.5: 상호작용 분포 EDA (Zipf's Law 확인)")
print("=" * 70)

rec_file = "Game Recommendations on Steam/recommendations.csv"

# ============================================================
# Step 1: 청크 기반 집계
# ============================================================
print("\n[Step 1] 청크 기반 집계 (41M rows)")
print("-" * 50)

app_counter = Counter()
user_counter = Counter()
total_rows = 0
chunk_size = 1_000_000

print("  청크 처리 중...")
for i, chunk in enumerate(pd.read_csv(rec_file, chunksize=chunk_size, usecols=['app_id', 'user_id'])):
    app_counter.update(chunk['app_id'].values)
    user_counter.update(chunk['user_id'].values)
    total_rows += len(chunk)
    if (i + 1) % 10 == 0:
        print(f"    {total_rows:,} rows 처리 완료...")

print(f"\n  총 처리: {total_rows:,} rows")
print(f"  유니크 app_id: {len(app_counter):,}")
print(f"  유니크 user_id: {len(user_counter):,}")

# ============================================================
# Step 2: 아이템 인기도 분포 (app_id별 상호작용 수)
# ============================================================
print("\n[Step 2] 아이템 인기도 분포")
print("-" * 50)

app_interactions = pd.Series(dict(app_counter))
app_interactions = app_interactions.sort_values(ascending=False)

print(f"  상호작용 수 통계:")
print(f"    평균: {app_interactions.mean():.1f}")
print(f"    중앙값: {app_interactions.median():.1f}")
print(f"    최소: {app_interactions.min()}")
print(f"    최대: {app_interactions.max():,}")
print(f"    표준편차: {app_interactions.std():.1f}")

print(f"\n  상위 10개 게임 (인기 게임):")
for i, (app_id, cnt) in enumerate(app_interactions.head(10).items(), 1):
    print(f"    {i}. app_id={app_id}: {cnt:,} interactions")

print(f"\n  하위 10개 게임 (Long-tail):")
for i, (app_id, cnt) in enumerate(app_interactions.tail(10).items(), 1):
    print(f"    {i}. app_id={app_id}: {cnt} interactions")

# 구간별 분포
print(f"\n  상호작용 수 구간별 게임 수:")
bins = [0, 10, 100, 1000, 10000, 100000, np.inf]
labels = ['1-10', '11-100', '101-1K', '1K-10K', '10K-100K', '100K+']
app_bins = pd.cut(app_interactions, bins=bins, labels=labels)
for label in labels:
    count = (app_bins == label).sum()
    pct = count / len(app_interactions) * 100
    print(f"    {label}: {count:,} ({pct:.1f}%)")

# ============================================================
# Step 3: 사용자 활동량 분포 (user_id별 상호작용 수)
# ============================================================
print("\n[Step 3] 사용자 활동량 분포")
print("-" * 50)

user_interactions = pd.Series(dict(user_counter))
user_interactions = user_interactions.sort_values(ascending=False)

print(f"  상호작용 수 통계:")
print(f"    평균: {user_interactions.mean():.2f}")
print(f"    중앙값: {user_interactions.median():.1f}")
print(f"    최소: {user_interactions.min()}")
print(f"    최대: {user_interactions.max():,}")
print(f"    표준편차: {user_interactions.std():.2f}")

print(f"\n  상위 10명 사용자 (Heavy User):")
for i, (user_id, cnt) in enumerate(user_interactions.head(10).items(), 1):
    print(f"    {i}. user_id={user_id}: {cnt} reviews")

# 구간별 분포
print(f"\n  리뷰 수 구간별 사용자 수:")
bins = [0, 1, 2, 5, 10, 20, 50, 100, np.inf]
labels = ['1', '2', '3-5', '6-10', '11-20', '21-50', '51-100', '100+']
user_bins = pd.cut(user_interactions, bins=bins, labels=labels)
for label in labels:
    count = (user_bins == label).sum()
    pct = count / len(user_interactions) * 100
    print(f"    {label}: {count:,} ({pct:.1f}%)")

# ============================================================
# Step 4: Pareto 분석 (누적 분포)
# ============================================================
print("\n[Step 4] Pareto 분석 (누적 분포)")
print("-" * 50)

# 아이템 Pareto
print("\n  [아이템 Pareto - 상위 N% 게임이 전체 상호작용의 몇 %?]")
app_sorted = app_interactions.sort_values(ascending=False)
app_cumsum = app_sorted.cumsum()
app_total = app_sorted.sum()

for pct in [1, 5, 10, 20, 30, 40, 50]:
    n_items = int(len(app_sorted) * pct / 100)
    interaction_pct = app_cumsum.iloc[n_items-1] / app_total * 100 if n_items > 0 else 0
    print(f"    상위 {pct}% 아이템 ({n_items:,}개) → 전체 상호작용의 {interaction_pct:.1f}%")

# 역으로: 전체 상호작용의 N%를 차지하는 아이템 비율
print("\n  [역 Pareto - 전체 상호작용의 N%를 차지하는 아이템 비율]")
for target_pct in [50, 60, 70, 80, 90]:
    target_interactions = app_total * target_pct / 100
    n_items = (app_cumsum <= target_interactions).sum() + 1
    item_pct = n_items / len(app_sorted) * 100
    print(f"    상호작용 {target_pct}% → 상위 {item_pct:.2f}% 아이템 ({n_items:,}개)")

# 사용자 Pareto
print("\n  [사용자 Pareto - 상위 N% 사용자가 전체 리뷰의 몇 %?]")
user_sorted = user_interactions.sort_values(ascending=False)
user_cumsum = user_sorted.cumsum()
user_total = user_sorted.sum()

for pct in [1, 5, 10, 20, 30, 40, 50]:
    n_users = int(len(user_sorted) * pct / 100)
    review_pct = user_cumsum.iloc[n_users-1] / user_total * 100 if n_users > 0 else 0
    print(f"    상위 {pct}% 사용자 ({n_users:,}명) → 전체 리뷰의 {review_pct:.1f}%")

# ============================================================
# Step 5: 분류 기준 제안
# ============================================================
print("\n[Step 5] 분류 기준 제안")
print("-" * 50)

# 아이템 분류: 누적 60% 기준
target_60 = app_total * 0.6
n_popular = (app_cumsum <= target_60).sum() + 1
popular_threshold = app_sorted.iloc[n_popular-1]

print(f"\n  [아이템 분류 - 누적 60% 기준]")
print(f"    Popular: 상위 {n_popular:,}개 ({n_popular/len(app_sorted)*100:.2f}%)")
print(f"    Long-tail: 나머지 {len(app_sorted)-n_popular:,}개 ({(len(app_sorted)-n_popular)/len(app_sorted)*100:.2f}%)")
print(f"    분류 임계값: {popular_threshold:,} interactions")

# 사용자 분류: 누적 60% 기준
target_60_user = user_total * 0.6
n_heavy = (user_cumsum <= target_60_user).sum() + 1
heavy_threshold = user_sorted.iloc[n_heavy-1]

print(f"\n  [사용자 분류 - 누적 60% 기준]")
print(f"    Heavy: 상위 {n_heavy:,}명 ({n_heavy/len(user_sorted)*100:.2f}%)")
print(f"    Light: 나머지 {len(user_sorted)-n_heavy:,}명 ({(len(user_sorted)-n_heavy)/len(user_sorted)*100:.2f}%)")
print(f"    분류 임계값: {heavy_threshold} reviews")

# Quantile 20% 기준 (대안)
print(f"\n  [대안 - Quantile 20% 기준]")
app_q80 = app_interactions.quantile(0.80)
user_q80 = user_interactions.quantile(0.80)
print(f"    아이템 상위 20% 임계값: {app_q80:.0f} interactions")
print(f"    사용자 상위 20% 임계값: {user_q80:.0f} reviews")

# ============================================================
# 결과 요약
# ============================================================
print("\n" + "=" * 70)
print("[결과 요약]")
print("=" * 70)
print(f"""
기본 통계:
  - 총 상호작용: {total_rows:,}
  - 유니크 아이템: {len(app_counter):,}
  - 유니크 사용자: {len(user_counter):,}
  - 평균 아이템당 상호작용: {app_interactions.mean():.1f}
  - 평균 사용자당 리뷰: {user_interactions.mean():.2f}

Pareto 분포 확인:
  - 상위 10% 아이템 → 전체 상호작용의 약 {app_cumsum.iloc[int(len(app_sorted)*0.1)-1]/app_total*100:.1f}%
  - 상위 10% 사용자 → 전체 리뷰의 약 {user_cumsum.iloc[int(len(user_sorted)*0.1)-1]/user_total*100:.1f}%

권장 분류 기준 (누적 60%):
  - Popular 아이템: {n_popular:,}개 (상위 {n_popular/len(app_sorted)*100:.2f}%)
  - Heavy 사용자: {n_heavy:,}명 (상위 {n_heavy/len(user_sorted)*100:.2f}%)
""")
print("=" * 70)

