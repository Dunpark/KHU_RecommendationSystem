# -*- coding: utf-8 -*-
"""
Phase 1 - Task 1.2: games.csv, users.csv 로드 및 검증
"""
import pandas as pd
import numpy as np

print("=" * 70)
print("Phase 1 - Task 1.2: games.csv, users.csv 로드 및 검증")
print("=" * 70)

# ============================================================
# Part 1: games.csv 분석
# ============================================================
print("\n" + "=" * 70)
print("[Part 1] games.csv 분석")
print("=" * 70)

games = pd.read_csv("Game Recommendations on Steam/games.csv")

print(f"\n[1.1] 기본 정보")
print(f"  Shape: {games.shape}")
print(f"  유니크 app_id: {games['app_id'].nunique():,}")

print(f"\n[1.2] 컬럼 구조")
print(f"  컬럼 ({len(games.columns)}개): {list(games.columns)}")

print(f"\n[1.3] 데이터 타입")
for col in games.columns:
    print(f"    - {col}: {games[col].dtype}")

print(f"\n[1.4] Null 값 현황")
null_info = games.isnull().sum()
for col in games.columns:
    null_cnt = null_info[col]
    null_pct = null_cnt / len(games) * 100
    status = "WARNING" if null_pct > 0 else "OK"
    print(f"    [{status}] {col}: {null_cnt:,} ({null_pct:.2f}%)")

print(f"\n[1.5] rating 분포")
print(games['rating'].value_counts())

print(f"\n[1.6] positive_ratio 통계")
print(f"    평균: {games['positive_ratio'].mean():.1f}")
print(f"    중앙값: {games['positive_ratio'].median():.1f}")
print(f"    최소: {games['positive_ratio'].min()}")
print(f"    최대: {games['positive_ratio'].max()}")

print(f"\n[1.7] price_final 분포")
print(f"    무료 게임 (price=0): {(games['price_final'] == 0).sum():,} ({(games['price_final'] == 0).mean()*100:.1f}%)")
print(f"    유료 게임 (price>0): {(games['price_final'] > 0).sum():,} ({(games['price_final'] > 0).mean()*100:.1f}%)")
print(f"    평균 가격 (유료만): ${games[games['price_final'] > 0]['price_final'].mean():.2f}")
print(f"    최대 가격: ${games['price_final'].max():.2f}")

print(f"\n[1.8] user_reviews 분포")
print(f"    평균: {games['user_reviews'].mean():.1f}")
print(f"    중앙값: {games['user_reviews'].median():.1f}")
print(f"    최대: {games['user_reviews'].max():,}")
# 구간별 분포
bins = [0, 10, 100, 1000, 10000, 100000, float('inf')]
labels = ['0-10', '11-100', '101-1K', '1K-10K', '10K-100K', '100K+']
games['review_bin'] = pd.cut(games['user_reviews'], bins=bins, labels=labels)
print(f"\n    구간별 분포:")
print(games['review_bin'].value_counts().sort_index())

print(f"\n[1.9] 플랫폼 지원")
print(f"    Windows: {games['win'].sum():,} ({games['win'].mean()*100:.1f}%)")
print(f"    Mac: {games['mac'].sum():,} ({games['mac'].mean()*100:.1f}%)")
print(f"    Linux: {games['linux'].sum():,} ({games['linux'].mean()*100:.1f}%)")

# ============================================================
# Part 2: users.csv 분석
# ============================================================
print("\n" + "=" * 70)
print("[Part 2] users.csv 분석")
print("=" * 70)

users = pd.read_csv("Game Recommendations on Steam/users.csv")

print(f"\n[2.1] 기본 정보")
print(f"  Shape: {users.shape}")
print(f"  유니크 user_id: {users['user_id'].nunique():,}")

print(f"\n[2.2] 컬럼 구조")
print(f"  컬럼: {list(users.columns)}")
for col in users.columns:
    print(f"    - {col}: {users[col].dtype}")

print(f"\n[2.3] Null 값 현황")
for col in users.columns:
    null_cnt = users[col].isnull().sum()
    null_pct = null_cnt / len(users) * 100
    status = "WARNING" if null_pct > 0 else "OK"
    print(f"    [{status}] {col}: {null_cnt:,} ({null_pct:.2f}%)")

print(f"\n[2.4] products (보유 게임 수) 통계")
print(f"    평균: {users['products'].mean():.1f}")
print(f"    중앙값: {users['products'].median():.1f}")
print(f"    최소: {users['products'].min()}")
print(f"    최대: {users['products'].max():,}")

# 구간별 분포
bins = [0, 10, 50, 100, 500, 1000, float('inf')]
labels = ['1-10', '11-50', '51-100', '101-500', '501-1K', '1K+']
users['products_bin'] = pd.cut(users['products'], bins=bins, labels=labels)
print(f"\n    구간별 분포:")
print(users['products_bin'].value_counts().sort_index())

print(f"\n[2.5] reviews (작성 리뷰 수) 통계")
print(f"    평균: {users['reviews'].mean():.2f}")
print(f"    중앙값: {users['reviews'].median():.1f}")
print(f"    최소: {users['reviews'].min()}")
print(f"    최대: {users['reviews'].max():,}")
print(f"    리뷰 0개 사용자: {(users['reviews'] == 0).sum():,} ({(users['reviews'] == 0).mean()*100:.1f}%)")

# 구간별 분포
bins = [-1, 0, 1, 5, 10, 50, 100, float('inf')]
labels = ['0', '1', '2-5', '6-10', '11-50', '51-100', '100+']
users['reviews_bin'] = pd.cut(users['reviews'], bins=bins, labels=labels)
print(f"\n    구간별 분포:")
print(users['reviews_bin'].value_counts().sort_index())

# ============================================================
# Part 3: 교차 검증
# ============================================================
print("\n" + "=" * 70)
print("[Part 3] 교차 검증")
print("=" * 70)

print(f"\n[3.1] Task 1.1 결과와 비교")
print(f"  games.csv app_id 수: {games['app_id'].nunique():,}")
print(f"  users.csv user_id 수: {users['user_id'].nunique():,}")
print(f"  (참고) recommendations.csv 예상 - app_id: ~37,610 / user_id: ~13,781,059")

# ============================================================
# 결과 요약
# ============================================================
print("\n" + "=" * 70)
print("[결과 요약]")
print("=" * 70)
print(f"""
games.csv:
  - 총 게임 수: {len(games):,}
  - 유니크 app_id: {games['app_id'].nunique():,}
  - 무료 게임 비율: {(games['price_final'] == 0).mean()*100:.1f}%
  - 평균 positive_ratio: {games['positive_ratio'].mean():.1f}

users.csv:
  - 총 사용자 수: {len(users):,}
  - 평균 보유 게임: {users['products'].mean():.1f}개
  - 평균 리뷰 수: {users['reviews'].mean():.2f}개
  - 리뷰 미작성 사용자: {(users['reviews'] == 0).mean()*100:.1f}%
""")
print("=" * 70)

