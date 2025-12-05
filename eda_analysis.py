import pandas as pd
import json
import os

print('='*70)
print('Steam 게임 추천 시스템 프로젝트 - EDA 분석')
print('='*70)

# ============================================================
# 1. Game Recommendations on Steam 데이터셋
# ============================================================
print('\n' + '='*70)
print('1. Game Recommendations on Steam 데이터셋')
print('='*70)

# games.csv
print('\n[1.1 games.csv]')
games = pd.read_csv('Game Recommendations on Steam/games.csv')
print(f'Shape: {games.shape}')
print(f'Columns: {list(games.columns)}')
print(f'app_id unique: {games["app_id"].nunique()}')
print(f'\nMissing values:')
print(games.isnull().sum())
print(f'\nData types:')
print(games.dtypes)
print(f'\nBasic stats for numerical columns:')
print(games.describe())

# users.csv
print('\n' + '-'*50)
print('[1.2 users.csv]')
users = pd.read_csv('Game Recommendations on Steam/users.csv')
print(f'Shape: {users.shape}')
print(f'Columns: {list(users.columns)}')
print(f'user_id unique: {users["user_id"].nunique()}')
print(f'\nBasic stats:')
print(users.describe())

# games_metadata.json
print('\n' + '-'*50)
print('[1.3 games_metadata.json]')
metadata_list = []
with open('Game Recommendations on Steam/games_metadata.json', 'r', encoding='utf-8') as f:
    for line in f:
        metadata_list.append(json.loads(line))
print(f'Total entries: {len(metadata_list)}')
print(f'Sample entry keys: {list(metadata_list[0].keys())}')

# Tag 분석
all_tags = []
for item in metadata_list:
    if 'tags' in item:
        all_tags.extend(item['tags'])
tag_counts = pd.Series(all_tags).value_counts()
print(f'\nTotal unique tags: {len(tag_counts)}')
print(f'\nTop 20 tags:')
print(tag_counts.head(20))

# ============================================================
# 2. Steam Games Dataset 2025
# ============================================================
print('\n' + '='*70)
print('2. Steam Games Dataset 2025')
print('='*70)

# games_march2025_cleaned.csv (컬럼만 확인 - 파일이 큼)
print('\n[2.1 games_march2025_cleaned.csv]')
steam2025 = pd.read_csv('Steam Games Dataset 2025/games_march2025_cleaned.csv', nrows=1000)
print(f'Columns ({len(steam2025.columns)}): {list(steam2025.columns)}')
print(f'\nSample 1000 rows - appid unique: {steam2025["appid"].nunique()}')

# 전체 행 수 확인
total_rows = sum(1 for _ in open('Steam Games Dataset 2025/games_march2025_cleaned.csv', encoding='utf-8')) - 1
print(f'Total rows (estimated): {total_rows}')

# ============================================================
# 3. 데이터 매칭 분석
# ============================================================
print('\n' + '='*70)
print('3. 데이터셋 간 app_id 매칭 분석')
print('='*70)

# app_id 집합 생성
games_appids = set(games['app_id'].unique())
metadata_appids = set([item['app_id'] for item in metadata_list])
steam2025_appids = set(steam2025['appid'].unique())

print(f'\nGame Recommendations games.csv app_ids: {len(games_appids)}')
print(f'Game Recommendations metadata app_ids: {len(metadata_appids)}')
print(f'Steam 2025 (sample 1000) app_ids: {len(steam2025_appids)}')

# 매칭 분석
games_meta_match = games_appids.intersection(metadata_appids)
games_2025_match = games_appids.intersection(steam2025_appids)

print(f'\ngames.csv ∩ metadata: {len(games_meta_match)} ({len(games_meta_match)/len(games_appids)*100:.1f}%)')
print(f'games.csv ∩ steam2025 (sample): {len(games_2025_match)} ({len(games_2025_match)/len(games_appids)*100:.1f}%)')

# ============================================================
# 4. games.csv 상세 분석
# ============================================================
print('\n' + '='*70)
print('4. games.csv 상세 분석')
print('='*70)

print('\n[4.1 Rating 분포]')
print(games['rating'].value_counts())

print('\n[4.2 가격 분포]')
print(f"무료 게임 수: {(games['price_final'] == 0).sum()}")
print(f"유료 게임 수: {(games['price_final'] > 0).sum()}")
print(f"가격 통계:\n{games['price_final'].describe()}")

print('\n[4.3 플랫폼 분포]')
print(f"Windows: {games['win'].sum()}")
print(f"Mac: {games['mac'].sum()}")
print(f"Linux: {games['linux'].sum()}")

print('\n[4.4 출시 연도 분포]')
games['release_year'] = pd.to_datetime(games['date_release'], errors='coerce').dt.year
print(games['release_year'].value_counts().sort_index().tail(20))

print('\n[4.5 user_reviews 분포]')
print(games['user_reviews'].describe())
print(f"\nuser_reviews 구간별 분포:")
bins = [0, 10, 100, 1000, 10000, 100000, float('inf')]
labels = ['0-10', '11-100', '101-1K', '1K-10K', '10K-100K', '100K+']
games['review_bin'] = pd.cut(games['user_reviews'], bins=bins, labels=labels)
print(games['review_bin'].value_counts())

# ============================================================
# 5. users.csv 상세 분석
# ============================================================
print('\n' + '='*70)
print('5. users.csv 상세 분석')
print('='*70)

print('\n[5.1 products (보유 게임 수) 분포]')
print(users['products'].describe())
print(f"\nproducts 구간별 분포:")
bins = [0, 10, 50, 100, 500, 1000, float('inf')]
labels = ['1-10', '11-50', '51-100', '101-500', '501-1K', '1K+']
users['products_bin'] = pd.cut(users['products'], bins=bins, labels=labels)
print(users['products_bin'].value_counts())

print('\n[5.2 reviews (작성 리뷰 수) 분포]')
print(users['reviews'].describe())
print(f"\nreviews 구간별 분포:")
bins = [0, 1, 5, 10, 50, 100, float('inf')]
labels = ['0', '1-5', '6-10', '11-50', '51-100', '100+']
users['reviews_bin'] = pd.cut(users['reviews'], bins=bins, labels=labels, include_lowest=True)
print(users['reviews_bin'].value_counts())

# ============================================================
# 6. 메타데이터 태그 분석
# ============================================================
print('\n' + '='*70)
print('6. 메타데이터 태그 상세 분석')
print('='*70)

# 게임당 태그 수
tags_per_game = [len(item.get('tags', [])) for item in metadata_list]
print(f'게임당 평균 태그 수: {sum(tags_per_game)/len(tags_per_game):.1f}')
print(f'태그 없는 게임 수: {tags_per_game.count(0)}')

# 주요 장르/카테고리 태그
genre_tags = ['Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 'Sports', 
              'Racing', 'Puzzle', 'Casual', 'Indie', 'Free to Play']
print('\n장르별 게임 수:')
for tag in genre_tags:
    count = sum(1 for item in metadata_list if tag in item.get('tags', []))
    print(f'  {tag}: {count}')

print('\n' + '='*70)
print('EDA 분석 완료')
print('='*70)

