# -*- coding: utf-8 -*-
"""
Phase 1 - Task 1.6: 데이터 병합 및 통합 데이터셋 생성
"""
import pandas as pd
import numpy as np
import json
from collections import Counter
import os

print("=" * 70)
print("Phase 1 - Task 1.6: 데이터 병합 및 통합 데이터셋 생성")
print("=" * 70)

# ============================================================
# Step 1: 상호작용 집계 (파티션 기준용)
# ============================================================
print("\n[Step 1] 상호작용 집계 (청크 처리)")
print("-" * 50)

rec_file = "Game Recommendations on Steam/recommendations.csv"
app_counter = Counter()
user_counter = Counter()

for chunk in pd.read_csv(rec_file, chunksize=2_000_000, usecols=['app_id', 'user_id']):
    app_counter.update(chunk['app_id'].values)
    user_counter.update(chunk['user_id'].values)

print(f"  아이템 집계 완료: {len(app_counter):,} games")
print(f"  사용자 집계 완료: {len(user_counter):,} users")

# ============================================================
# Step 2: 아이템 파티션 기준 계산
# ============================================================
print("\n[Step 2] 아이템 파티션 기준 계산")
print("-" * 50)

app_df = pd.DataFrame({
    'app_id': list(app_counter.keys()),
    'interaction_count': list(app_counter.values())
})
app_df = app_df.sort_values('interaction_count', ascending=False).reset_index(drop=True)

# 누적 60% 기준
total_interactions = app_df['interaction_count'].sum()
app_df['cumsum'] = app_df['interaction_count'].cumsum()
app_df['cumsum_pct'] = app_df['cumsum'] / total_interactions * 100

# Popular: 누적 60% 이내
popular_threshold_idx = (app_df['cumsum_pct'] <= 60).sum()
popular_threshold = app_df.iloc[popular_threshold_idx - 1]['interaction_count'] if popular_threshold_idx > 0 else 0

app_df['item_partition'] = np.where(
    app_df['interaction_count'] >= popular_threshold,
    'Popular',
    'Long-tail'
)

n_popular = (app_df['item_partition'] == 'Popular').sum()
n_longtail = (app_df['item_partition'] == 'Long-tail').sum()

print(f"  누적 60% 임계값: {popular_threshold:,} interactions")
print(f"  Popular 아이템: {n_popular:,} ({n_popular/len(app_df)*100:.2f}%)")
print(f"  Long-tail 아이템: {n_longtail:,} ({n_longtail/len(app_df)*100:.2f}%)")

# ============================================================
# Step 3: 사용자 파티션 기준 계산
# ============================================================
print("\n[Step 3] 사용자 파티션 기준 계산")
print("-" * 50)

user_df = pd.DataFrame({
    'user_id': list(user_counter.keys()),
    'review_count': list(user_counter.values())
})
user_df = user_df.sort_values('review_count', ascending=False).reset_index(drop=True)

# 누적 60% 기준
total_reviews = user_df['review_count'].sum()
user_df['cumsum'] = user_df['review_count'].cumsum()
user_df['cumsum_pct'] = user_df['cumsum'] / total_reviews * 100

# Heavy: 누적 60% 이내
heavy_threshold_idx = (user_df['cumsum_pct'] <= 60).sum()
heavy_threshold = user_df.iloc[heavy_threshold_idx - 1]['review_count'] if heavy_threshold_idx > 0 else 0

user_df['user_partition'] = np.where(
    user_df['review_count'] >= heavy_threshold,
    'Heavy',
    'Light'
)

n_heavy = (user_df['user_partition'] == 'Heavy').sum()
n_light = (user_df['user_partition'] == 'Light').sum()

print(f"  누적 60% 임계값: {heavy_threshold} reviews")
print(f"  Heavy 사용자: {n_heavy:,} ({n_heavy/len(user_df)*100:.2f}%)")
print(f"  Light 사용자: {n_light:,} ({n_light/len(user_df)*100:.2f}%)")

# ============================================================
# Step 4: games.csv 로드
# ============================================================
print("\n[Step 4] games.csv 로드")
print("-" * 50)

games = pd.read_csv("Game Recommendations on Steam/games.csv")
print(f"  games.csv: {len(games):,} games")

# ============================================================
# Step 5: games_metadata.json 로드 (태그)
# ============================================================
print("\n[Step 5] games_metadata.json 로드")
print("-" * 50)

metadata_list = []
with open("Game Recommendations on Steam/games_metadata.json", 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        metadata_list.append({
            'app_id': data['app_id'],
            'tags': data.get('tags', []),
            'description_len': len(data.get('description', '')) if data.get('description') else 0
        })

metadata = pd.DataFrame(metadata_list)
# 태그를 문자열로 변환 (나중에 사용 편의)
metadata['tags_str'] = metadata['tags'].apply(lambda x: '|'.join(x) if isinstance(x, list) else '')
metadata['num_tags'] = metadata['tags'].apply(lambda x: len(x) if isinstance(x, list) else 0)
print(f"  metadata: {len(metadata):,} games")

# ============================================================
# Step 6: Steam 2025 데이터 로드 (핵심 피처만)
# ============================================================
print("\n[Step 6] Steam 2025 데이터 로드")
print("-" * 50)

steam2025_cols = ['appid', 'estimated_owners', 'positive', 'negative', 'genres']
steam2025 = pd.read_csv("Steam Games Dataset 2025/games_march2025_cleaned.csv", usecols=steam2025_cols)
steam2025 = steam2025.rename(columns={'appid': 'app_id'})

# estimated_owners 파싱 (범위 → 중간값)
def parse_owners(owners_str):
    if pd.isna(owners_str):
        return np.nan
    try:
        parts = owners_str.replace(',', '').split(' - ')
        low = int(parts[0])
        high = int(parts[1]) if len(parts) > 1 else low
        return (low + high) / 2
    except:
        return np.nan

steam2025['estimated_owners_mid'] = steam2025['estimated_owners'].apply(parse_owners)
steam2025['steam2025_positive_ratio'] = steam2025['positive'] / (steam2025['positive'] + steam2025['negative']) * 100
steam2025['steam2025_positive_ratio'] = steam2025['steam2025_positive_ratio'].fillna(0)

print(f"  Steam 2025: {len(steam2025):,} games")
print(f"  estimated_owners 파싱 완료")

# ============================================================
# Step 7: 아이템 데이터 병합
# ============================================================
print("\n[Step 7] 아이템 데이터 병합")
print("-" * 50)

# 1차: games + interaction_count + partition
items = games.merge(
    app_df[['app_id', 'interaction_count', 'item_partition']],
    on='app_id',
    how='left'
)
# 상호작용 없는 게임 처리
items['interaction_count'] = items['interaction_count'].fillna(0).astype(int)
items['item_partition'] = items['item_partition'].fillna('Long-tail')

print(f"  games + interactions: {len(items):,}")

# 2차: + metadata (tags)
items = items.merge(
    metadata[['app_id', 'tags_str', 'num_tags', 'description_len']],
    on='app_id',
    how='left'
)
items['tags_str'] = items['tags_str'].fillna('')
items['num_tags'] = items['num_tags'].fillna(0).astype(int)

print(f"  + metadata: {len(items):,}")

# 3차: + Steam 2025 (optional)
items = items.merge(
    steam2025[['app_id', 'estimated_owners_mid', 'steam2025_positive_ratio', 'genres']],
    on='app_id',
    how='left'
)
items = items.rename(columns={'genres': 'steam2025_genres'})

matched_steam2025 = items['estimated_owners_mid'].notna().sum()
print(f"  + Steam 2025: {len(items):,} (매칭: {matched_steam2025:,}, {matched_steam2025/len(items)*100:.1f}%)")

# ============================================================
# Step 8: 사용자 데이터 병합
# ============================================================
print("\n[Step 8] 사용자 데이터 병합")
print("-" * 50)

users = pd.read_csv("Game Recommendations on Steam/users.csv")
print(f"  users.csv: {len(users):,}")

# review_count + partition 병합
users = users.merge(
    user_df[['user_id', 'review_count', 'user_partition']],
    on='user_id',
    how='left'
)
users['review_count'] = users['review_count'].fillna(0).astype(int)
users['user_partition'] = users['user_partition'].fillna('Light')

print(f"  + partition: {len(users):,}")

# ============================================================
# Step 9: 저장
# ============================================================
print("\n[Step 9] 통합 데이터셋 저장")
print("-" * 50)

# 저장 전 컬럼 최적화
items_save_cols = [
    'app_id', 'title', 'date_release', 'win', 'mac', 'linux',
    'rating', 'positive_ratio', 'user_reviews', 'price_final', 'discount', 'steam_deck',
    'interaction_count', 'item_partition',
    'tags_str', 'num_tags', 'description_len',
    'estimated_owners_mid', 'steam2025_positive_ratio', 'steam2025_genres'
]

users_save_cols = [
    'user_id', 'products', 'reviews',
    'review_count', 'user_partition'
]

items[items_save_cols].to_csv("merged_items.csv", index=False)
users[users_save_cols].to_csv("merged_users.csv", index=False)

print(f"  merged_items.csv: {len(items):,} rows, {len(items_save_cols)} cols")
print(f"  merged_users.csv: {len(users):,} rows, {len(users_save_cols)} cols")

# ============================================================
# Step 10: 검증 및 요약
# ============================================================
print("\n[Step 10] 검증 및 요약")
print("-" * 50)

print("\n[아이템 데이터 요약]")
print(f"  총 아이템: {len(items):,}")
print(f"  Popular: {(items['item_partition'] == 'Popular').sum():,} ({(items['item_partition'] == 'Popular').mean()*100:.2f}%)")
print(f"  Long-tail: {(items['item_partition'] == 'Long-tail').sum():,} ({(items['item_partition'] == 'Long-tail').mean()*100:.2f}%)")
print(f"  태그 있음: {(items['num_tags'] > 0).sum():,} ({(items['num_tags'] > 0).mean()*100:.1f}%)")
print(f"  Steam2025 매칭: {items['estimated_owners_mid'].notna().sum():,} ({items['estimated_owners_mid'].notna().mean()*100:.1f}%)")

print("\n[사용자 데이터 요약]")
print(f"  총 사용자: {len(users):,}")
print(f"  Heavy: {(users['user_partition'] == 'Heavy').sum():,} ({(users['user_partition'] == 'Heavy').mean()*100:.2f}%)")
print(f"  Light: {(users['user_partition'] == 'Light').sum():,} ({(users['user_partition'] == 'Light').mean()*100:.2f}%)")

print("\n[파티션 교차 분석 준비]")
# 아이템 파티션별 상호작용 비율
popular_items = set(items[items['item_partition'] == 'Popular']['app_id'])
longtail_items = set(items[items['item_partition'] == 'Long-tail']['app_id'])

popular_interactions = sum(cnt for app, cnt in app_counter.items() if app in popular_items)
longtail_interactions = sum(cnt for app, cnt in app_counter.items() if app in longtail_items)
total = popular_interactions + longtail_interactions

print(f"  Popular 아이템 상호작용: {popular_interactions:,} ({popular_interactions/total*100:.1f}%)")
print(f"  Long-tail 아이템 상호작용: {longtail_interactions:,} ({longtail_interactions/total*100:.1f}%)")

print("\n" + "=" * 70)
print("[완료]")
print("=" * 70)
print(f"""
생성 파일:
  1. merged_items.csv ({len(items):,} games, {len(items_save_cols)} features)
  2. merged_users.csv ({len(users):,} users, {len(users_save_cols)} features)

파티션 기준:
  - Popular 아이템: interaction_count >= {popular_threshold:,}
  - Heavy 사용자: review_count >= {heavy_threshold}
""")
print("=" * 70)

