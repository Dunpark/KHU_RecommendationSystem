# -*- coding: utf-8 -*-
"""
Phase 1 - Task 1.4: Steam 2025 데이터 로드 및 매칭 분석
"""
import pandas as pd
import numpy as np

print("=" * 70)
print("Phase 1 - Task 1.4: Steam 2025 데이터 로드 및 매칭 분석")
print("=" * 70)

# ============================================================
# Step 1: 데이터 로드 (샘플 먼저)
# ============================================================
print("\n[Step 1] 데이터 로드")
print("-" * 50)

steam2025_file = "Steam Games Dataset 2025/games_march2025_cleaned.csv"

# 컬럼 확인용 샘플
sample = pd.read_csv(steam2025_file, nrows=5)
print(f"  컬럼 수: {len(sample.columns)}")
print(f"  컬럼 목록:")
for i, col in enumerate(sample.columns, 1):
    print(f"    {i:2d}. {col}")

# ============================================================
# Step 2: 핵심 컬럼만 로드
# ============================================================
print("\n[Step 2] 핵심 컬럼 로드")
print("-" * 50)

# 필요한 컬럼만 선택
useful_cols = [
    'appid', 'name', 'release_date', 'price',
    'positive', 'negative', 'estimated_owners',
    'average_playtime_forever', 'median_playtime_forever',
    'genres', 'tags', 'developers', 'publishers',
    'metacritic_score', 'recommendations', 'peak_ccu'
]

# 존재하는 컬럼만 필터링
existing_cols = [col for col in useful_cols if col in sample.columns]
print(f"  선택 컬럼: {len(existing_cols)}개")

steam2025 = pd.read_csv(steam2025_file, usecols=existing_cols)
print(f"  로드 완료: {len(steam2025):,} rows")

# ============================================================
# Step 3: 기본 통계
# ============================================================
print("\n[Step 3] 기본 통계")
print("-" * 50)

print(f"  총 게임 수: {len(steam2025):,}")
print(f"  유니크 appid: {steam2025['appid'].nunique():,}")

print(f"\n  Null 값 현황:")
for col in steam2025.columns:
    null_cnt = steam2025[col].isnull().sum()
    null_pct = null_cnt / len(steam2025) * 100
    status = "WARNING" if null_pct > 5 else "OK"
    print(f"    [{status}] {col}: {null_cnt:,} ({null_pct:.1f}%)")

# ============================================================
# Step 4: estimated_owners 분석
# ============================================================
print("\n[Step 4] estimated_owners 분석")
print("-" * 50)

if 'estimated_owners' in steam2025.columns:
    owners_dist = steam2025['estimated_owners'].value_counts().head(15)
    print(f"  estimated_owners 분포 (상위 15개):")
    for owner_range, count in owners_dist.items():
        pct = count / len(steam2025) * 100
        print(f"    {owner_range}: {count:,} ({pct:.1f}%)")

# ============================================================
# Step 5: positive/negative 분석
# ============================================================
print("\n[Step 5] positive/negative 분석")
print("-" * 50)

if 'positive' in steam2025.columns and 'negative' in steam2025.columns:
    steam2025['total_reviews'] = steam2025['positive'] + steam2025['negative']
    steam2025['positive_ratio'] = steam2025['positive'] / steam2025['total_reviews'] * 100
    steam2025['positive_ratio'] = steam2025['positive_ratio'].fillna(0)
    
    print(f"  total_reviews 통계:")
    print(f"    평균: {steam2025['total_reviews'].mean():.1f}")
    print(f"    중앙값: {steam2025['total_reviews'].median():.1f}")
    print(f"    최대: {steam2025['total_reviews'].max():,}")
    
    print(f"\n  positive_ratio 통계:")
    valid_ratio = steam2025[steam2025['total_reviews'] > 0]['positive_ratio']
    print(f"    평균: {valid_ratio.mean():.1f}%")
    print(f"    중앙값: {valid_ratio.median():.1f}%")

# ============================================================
# Step 6: playtime 분석
# ============================================================
print("\n[Step 6] playtime 분석")
print("-" * 50)

if 'average_playtime_forever' in steam2025.columns:
    # 분 단위를 시간 단위로 변환
    steam2025['avg_playtime_hours'] = steam2025['average_playtime_forever'] / 60
    
    print(f"  average_playtime (시간 단위):")
    print(f"    평균: {steam2025['avg_playtime_hours'].mean():.1f}시간")
    print(f"    중앙값: {steam2025['avg_playtime_hours'].median():.1f}시간")
    print(f"    최대: {steam2025['avg_playtime_hours'].max():.1f}시간")
    print(f"    0시간 게임: {(steam2025['avg_playtime_hours'] == 0).sum():,} ({(steam2025['avg_playtime_hours'] == 0).mean()*100:.1f}%)")

# ============================================================
# Step 7: games.csv와 매칭 분석
# ============================================================
print("\n[Step 7] games.csv와 매칭 분석")
print("-" * 50)

games = pd.read_csv("Game Recommendations on Steam/games.csv")

steam2025_ids = set(steam2025['appid'].unique())
games_ids = set(games['app_id'].unique())

common = steam2025_ids.intersection(games_ids)
only_steam2025 = steam2025_ids - games_ids
only_games = games_ids - steam2025_ids

print(f"  Steam 2025 appid 수: {len(steam2025_ids):,}")
print(f"  games.csv app_id 수: {len(games_ids):,}")
print(f"\n  매칭 결과:")
print(f"    공통 app_id: {len(common):,}")
print(f"    games.csv 기준 매칭률: {len(common)/len(games_ids)*100:.1f}%")
print(f"    Steam 2025에만 있음: {len(only_steam2025):,}")
print(f"    games.csv에만 있음: {len(only_games):,}")

# ============================================================
# Step 8: 매칭된 게임의 피처 품질
# ============================================================
print("\n[Step 8] 매칭된 게임의 피처 품질")
print("-" * 50)

matched = steam2025[steam2025['appid'].isin(common)]
print(f"  매칭된 게임 수: {len(matched):,}")

print(f"\n  매칭 게임의 Null 비율:")
for col in ['estimated_owners', 'positive', 'negative', 'average_playtime_forever', 'genres', 'tags']:
    if col in matched.columns:
        null_pct = matched[col].isnull().mean() * 100
        print(f"    {col}: {null_pct:.1f}%")

# ============================================================
# 결과 요약
# ============================================================
print("\n" + "=" * 70)
print("[결과 요약]")
print("=" * 70)
print(f"""
Steam Games Dataset 2025:
  - 총 게임 수: {len(steam2025):,}
  - 유니크 appid: {steam2025['appid'].nunique():,}

games.csv와 매칭:
  - 공통 app_id: {len(common):,}
  - 매칭률: {len(common)/len(games_ids)*100:.1f}%

핵심 피처:
  - estimated_owners: 소유자 수 구간 (Long-tail 분류용)
  - positive/negative: 정확한 평점 (Content Feature)
  - average_playtime: 참여도 지표 (시간 단위)
  - genres/tags: 추가 콘텐츠 정보
""")
print("=" * 70)

