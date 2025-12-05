# -*- coding: utf-8 -*-
"""
Phase 1 - Task 1.3: games_metadata.json 로드 및 태그 분석
"""
import json
from collections import Counter

print("=" * 70)
print("Phase 1 - Task 1.3: games_metadata.json 로드 및 태그 분석")
print("=" * 70)

metadata_file = "Game Recommendations on Steam/games_metadata.json"

# ============================================================
# Step 1: 데이터 로드
# ============================================================
print("\n[Step 1] 데이터 로드")
print("-" * 50)

metadata_list = []
with open(metadata_file, "r", encoding="utf-8") as f:
    for line in f:
        metadata_list.append(json.loads(line))

print(f"  총 게임 수: {len(metadata_list):,}")

# 샘플 확인
print(f"\n  샘플 데이터 (첫 번째 게임):")
sample = metadata_list[0]
print(f"    Keys: {list(sample.keys())}")
print(f"    app_id: {sample['app_id']}")
print(f"    description 길이: {len(sample.get('description', ''))}")
print(f"    tags 수: {len(sample.get('tags', []))}")
print(f"    tags 샘플: {sample.get('tags', [])[:5]}")

# ============================================================
# Step 2: 기본 통계
# ============================================================
print("\n[Step 2] 기본 통계")
print("-" * 50)

# 필드별 분석
has_description = sum(1 for item in metadata_list if item.get('description', ''))
has_tags = sum(1 for item in metadata_list if item.get('tags', []))
empty_tags = sum(1 for item in metadata_list if not item.get('tags', []))

print(f"  description 있는 게임: {has_description:,} ({has_description/len(metadata_list)*100:.1f}%)")
print(f"  tags 있는 게임: {has_tags:,} ({has_tags/len(metadata_list)*100:.1f}%)")
print(f"  tags 없는 게임: {empty_tags:,} ({empty_tags/len(metadata_list)*100:.1f}%)")

# 게임당 태그 수 분포
tags_per_game = [len(item.get('tags', [])) for item in metadata_list]
print(f"\n  게임당 태그 수:")
print(f"    평균: {sum(tags_per_game)/len(tags_per_game):.1f}")
print(f"    최소: {min(tags_per_game)}")
print(f"    최대: {max(tags_per_game)}")

# 구간별 분포
bins = {
    "0개": 0,
    "1-5개": 0,
    "6-10개": 0,
    "11-15개": 0,
    "16-20개": 0,
    "20개+": 0
}
for cnt in tags_per_game:
    if cnt == 0:
        bins["0개"] += 1
    elif cnt <= 5:
        bins["1-5개"] += 1
    elif cnt <= 10:
        bins["6-10개"] += 1
    elif cnt <= 15:
        bins["11-15개"] += 1
    elif cnt <= 20:
        bins["16-20개"] += 1
    else:
        bins["20개+"] += 1

print(f"\n  태그 수 구간별 분포:")
for bin_name, count in bins.items():
    pct = count / len(metadata_list) * 100
    print(f"    {bin_name}: {count:,} ({pct:.1f}%)")

# ============================================================
# Step 3: 태그 분석
# ============================================================
print("\n[Step 3] 태그 분석")
print("-" * 50)

# 모든 태그 수집
all_tags = []
for item in metadata_list:
    if item.get('tags'):
        all_tags.extend(item['tags'])

tag_counts = Counter(all_tags)
print(f"  총 태그 등장 횟수: {len(all_tags):,}")
print(f"  유니크 태그 수: {len(tag_counts):,}")

# Top 30 태그
print(f"\n  Top 30 태그:")
for i, (tag, count) in enumerate(tag_counts.most_common(30), 1):
    pct = count / len(metadata_list) * 100
    print(f"    {i:2d}. {tag}: {count:,} ({pct:.1f}%)")

# ============================================================
# Step 4: 태그 카테고리 분석
# ============================================================
print("\n[Step 4] 태그 카테고리 분석")
print("-" * 50)

# 주요 장르 태그
genre_tags = ['Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 
              'Sports', 'Racing', 'Puzzle', 'Casual', 'Indie']
print(f"\n  장르 태그:")
for tag in genre_tags:
    count = tag_counts.get(tag, 0)
    pct = count / len(metadata_list) * 100
    print(f"    {tag}: {count:,} ({pct:.1f}%)")

# 플레이 모드 태그
mode_tags = ['Singleplayer', 'Multiplayer', 'Co-op', 'Online Co-Op', 
             'Local Co-Op', 'PvP', 'MMO', 'Local Multiplayer']
print(f"\n  플레이 모드 태그:")
for tag in mode_tags:
    count = tag_counts.get(tag, 0)
    pct = count / len(metadata_list) * 100
    print(f"    {tag}: {count:,} ({pct:.1f}%)")

# 테마/분위기 태그
theme_tags = ['Atmospheric', 'Story Rich', 'Horror', 'Funny', 'Cute',
              'Dark', 'Relaxing', 'Sci-fi', 'Fantasy', 'Anime']
print(f"\n  테마/분위기 태그:")
for tag in theme_tags:
    count = tag_counts.get(tag, 0)
    pct = count / len(metadata_list) * 100
    print(f"    {tag}: {count:,} ({pct:.1f}%)")

# ============================================================
# Step 5: games.csv와 매칭 확인
# ============================================================
print("\n[Step 5] games.csv와 매칭 확인")
print("-" * 50)

import pandas as pd
games = pd.read_csv("Game Recommendations on Steam/games.csv")

metadata_app_ids = set(item['app_id'] for item in metadata_list)
games_app_ids = set(games['app_id'].unique())

common = metadata_app_ids.intersection(games_app_ids)
only_metadata = metadata_app_ids - games_app_ids
only_games = games_app_ids - metadata_app_ids

print(f"  metadata app_id 수: {len(metadata_app_ids):,}")
print(f"  games.csv app_id 수: {len(games_app_ids):,}")
print(f"  공통 app_id: {len(common):,} ({len(common)/len(games_app_ids)*100:.1f}%)")
print(f"  metadata에만 있음: {len(only_metadata):,}")
print(f"  games.csv에만 있음: {len(only_games):,}")

# ============================================================
# 결과 요약
# ============================================================
print("\n" + "=" * 70)
print("[결과 요약]")
print("=" * 70)
print(f"""
games_metadata.json:
  - 총 게임 수: {len(metadata_list):,}
  - 태그 있는 게임: {has_tags:,} ({has_tags/len(metadata_list)*100:.1f}%)
  - 유니크 태그 수: {len(tag_counts):,}
  - 게임당 평균 태그: {sum(tags_per_game)/len(tags_per_game):.1f}개
  - games.csv 매칭률: {len(common)/len(games_app_ids)*100:.1f}%

Top 5 태그:
  1. {tag_counts.most_common(5)[0][0]}: {tag_counts.most_common(5)[0][1]:,}
  2. {tag_counts.most_common(5)[1][0]}: {tag_counts.most_common(5)[1][1]:,}
  3. {tag_counts.most_common(5)[2][0]}: {tag_counts.most_common(5)[2][1]:,}
  4. {tag_counts.most_common(5)[3][0]}: {tag_counts.most_common(5)[3][1]:,}
  5. {tag_counts.most_common(5)[4][0]}: {tag_counts.most_common(5)[4][1]:,}
""")
print("=" * 70)

