# -*- coding: utf-8 -*-
"""
Phase 2 - Task 2.2: Train/Valid/Test 분할
사용자 기반 랜덤 분할 (동일 사용자 상호작용이 분산되지 않도록)
"""
import pandas as pd
import numpy as np
from collections import Counter
import os

print("=" * 70)
print("Phase 2 - Task 2.2: Train/Valid/Test 분할")
print("=" * 70)

np.random.seed(42)  # 재현성

# ============================================================
# Step 1: 파티션 정보 로드
# ============================================================
print("\n[Step 1] 파티션 정보 로드")
print("-" * 50)

items = pd.read_csv("merged_items.csv", usecols=['app_id', 'item_partition'])
users = pd.read_csv("merged_users.csv", usecols=['user_id', 'user_partition'])

item_partition_dict = dict(zip(items['app_id'], items['item_partition']))
user_partition_dict = dict(zip(users['user_id'], users['user_partition']))

print(f"  아이템 파티션 로드: {len(item_partition_dict):,}")
print(f"  사용자 파티션 로드: {len(user_partition_dict):,}")

# ============================================================
# Step 2: 사용자 ID 분할 (80/10/10)
# ============================================================
print("\n[Step 2] 사용자 ID 분할 (Train 80% / Valid 10% / Test 10%)")
print("-" * 50)

# recommendations.csv에 있는 사용자만 대상
rec_file = "Game Recommendations on Steam/recommendations.csv"

# 먼저 유니크 사용자 수집
print("  유니크 사용자 수집 중...")
unique_users = set()
for chunk in pd.read_csv(rec_file, chunksize=2_000_000, usecols=['user_id']):
    unique_users.update(chunk['user_id'].unique())

unique_users = np.array(list(unique_users))
np.random.shuffle(unique_users)

n_users = len(unique_users)
n_train = int(n_users * 0.8)
n_valid = int(n_users * 0.1)

train_users = set(unique_users[:n_train])
valid_users = set(unique_users[n_train:n_train + n_valid])
test_users = set(unique_users[n_train + n_valid:])

print(f"  총 사용자: {n_users:,}")
print(f"  Train 사용자: {len(train_users):,} ({len(train_users)/n_users*100:.1f}%)")
print(f"  Valid 사용자: {len(valid_users):,} ({len(valid_users)/n_users*100:.1f}%)")
print(f"  Test 사용자: {len(test_users):,} ({len(test_users)/n_users*100:.1f}%)")

# ============================================================
# Step 3: 상호작용 분할 및 저장
# ============================================================
print("\n[Step 3] 상호작용 분할 및 저장")
print("-" * 50)

# 출력 디렉토리
os.makedirs("data_split", exist_ok=True)

train_rows = []
valid_rows = []
test_rows = []

print("  청크 처리 및 분할 중...")
for chunk in pd.read_csv(rec_file, chunksize=2_000_000):
    # Train
    train_mask = chunk['user_id'].isin(train_users)
    train_rows.append(chunk[train_mask])
    
    # Valid
    valid_mask = chunk['user_id'].isin(valid_users)
    valid_rows.append(chunk[valid_mask])
    
    # Test
    test_mask = chunk['user_id'].isin(test_users)
    test_rows.append(chunk[test_mask])

# 합치기
train_df = pd.concat(train_rows, ignore_index=True)
valid_df = pd.concat(valid_rows, ignore_index=True)
test_df = pd.concat(test_rows, ignore_index=True)

print(f"\n  분할 결과:")
print(f"    Train: {len(train_df):,} rows ({len(train_df)/(len(train_df)+len(valid_df)+len(test_df))*100:.1f}%)")
print(f"    Valid: {len(valid_df):,} rows ({len(valid_df)/(len(train_df)+len(valid_df)+len(test_df))*100:.1f}%)")
print(f"    Test: {len(test_df):,} rows ({len(test_df)/(len(train_df)+len(valid_df)+len(test_df))*100:.1f}%)")

# 저장
print("\n  파일 저장 중...")
train_df.to_csv("data_split/train_interactions.csv", index=False)
valid_df.to_csv("data_split/valid_interactions.csv", index=False)
test_df.to_csv("data_split/test_interactions.csv", index=False)

print(f"    data_split/train_interactions.csv 저장 완료")
print(f"    data_split/valid_interactions.csv 저장 완료")
print(f"    data_split/test_interactions.csv 저장 완료")

# ============================================================
# Step 4: 파티션 분포 확인
# ============================================================
print("\n[Step 4] 파티션 분포 확인")
print("-" * 50)

def get_partition_dist(df, item_dict, user_dict):
    """그룹별 상호작용 분포 계산"""
    df = df.copy()
    df['item_part'] = df['app_id'].map(item_dict).fillna('Long-tail')
    df['user_part'] = df['user_id'].map(user_dict).fillna('Light')
    df['group'] = df['item_part'] + '_' + df['user_part']
    
    dist = df['group'].value_counts(normalize=True) * 100
    return dist

print("\n  [아이템 파티션 분포]")
print(f"  {'분할':<10} {'Popular':>12} {'Long-tail':>12}")
print("  " + "-" * 36)

for name, df in [('Train', train_df), ('Valid', valid_df), ('Test', test_df)]:
    df_temp = df.copy()
    df_temp['item_part'] = df_temp['app_id'].map(item_partition_dict).fillna('Long-tail')
    pop_pct = (df_temp['item_part'] == 'Popular').mean() * 100
    lt_pct = (df_temp['item_part'] == 'Long-tail').mean() * 100
    print(f"  {name:<10} {pop_pct:>11.2f}% {lt_pct:>11.2f}%")

print("\n  [사용자 파티션 분포]")
print(f"  {'분할':<10} {'Heavy':>12} {'Light':>12}")
print("  " + "-" * 36)

for name, df in [('Train', train_df), ('Valid', valid_df), ('Test', test_df)]:
    df_temp = df.copy()
    df_temp['user_part'] = df_temp['user_id'].map(user_partition_dict).fillna('Light')
    hv_pct = (df_temp['user_part'] == 'Heavy').mean() * 100
    lt_pct = (df_temp['user_part'] == 'Light').mean() * 100
    print(f"  {name:<10} {hv_pct:>11.2f}% {lt_pct:>11.2f}%")

print("\n  [4개 그룹 분포]")
groups = ['Popular_Heavy', 'Popular_Light', 'Long-tail_Heavy', 'Long-tail_Light']
print(f"  {'분할':<10}", end="")
for g in groups:
    print(f" {g:>15}", end="")
print()
print("  " + "-" * 75)

for name, df in [('Train', train_df), ('Valid', valid_df), ('Test', test_df)]:
    dist = get_partition_dist(df, item_partition_dict, user_partition_dict)
    print(f"  {name:<10}", end="")
    for g in groups:
        pct = dist.get(g, 0)
        print(f" {pct:>14.2f}%", end="")
    print()

# ============================================================
# Step 5: 데이터셋별 통계
# ============================================================
print("\n[Step 5] 데이터셋별 통계")
print("-" * 50)

print("\n  [유니크 ID 수]")
print(f"  {'분할':<10} {'Users':>15} {'Items':>15}")
print("  " + "-" * 42)

for name, df in [('Train', train_df), ('Valid', valid_df), ('Test', test_df)]:
    n_users = df['user_id'].nunique()
    n_items = df['app_id'].nunique()
    print(f"  {name:<10} {n_users:>15,} {n_items:>15,}")

print("\n  [상호작용 통계]")
print(f"  {'분할':<10} {'총 상호작용':>15} {'평균 hours':>12} {'추천율':>10}")
print("  " + "-" * 50)

for name, df in [('Train', train_df), ('Valid', valid_df), ('Test', test_df)]:
    n_inter = len(df)
    avg_hours = df['hours'].mean()
    rec_rate = df['is_recommended'].mean() * 100
    print(f"  {name:<10} {n_inter:>15,} {avg_hours:>11.1f}h {rec_rate:>9.1f}%")

# ============================================================
# Step 6: Cold-start 분석
# ============================================================
print("\n[Step 6] Cold-start 분석")
print("-" * 50)

train_users_set = set(train_df['user_id'].unique())
train_items_set = set(train_df['app_id'].unique())

# Valid에서 Cold-start
valid_cold_users = valid_df[~valid_df['user_id'].isin(train_users_set)]
valid_cold_items = valid_df[~valid_df['app_id'].isin(train_items_set)]

print("\n  [Valid 데이터 Cold-start]")
print(f"    Cold User (Train에 없음): {len(valid_cold_users):,} ({len(valid_cold_users)/len(valid_df)*100:.2f}%)")
print(f"    Cold Item (Train에 없음): {len(valid_cold_items):,} ({len(valid_cold_items)/len(valid_df)*100:.2f}%)")

# Test에서 Cold-start
test_cold_users = test_df[~test_df['user_id'].isin(train_users_set)]
test_cold_items = test_df[~test_df['app_id'].isin(train_items_set)]

print("\n  [Test 데이터 Cold-start]")
print(f"    Cold User (Train에 없음): {len(test_cold_users):,} ({len(test_cold_users)/len(test_df)*100:.2f}%)")
print(f"    Cold Item (Train에 없음): {len(test_cold_items):,} ({len(test_cold_items)/len(test_df)*100:.2f}%)")

# ============================================================
# 결과 요약
# ============================================================
print("\n" + "=" * 70)
print("[결과 요약]")
print("=" * 70)
print(f"""
분할 결과:
  - Train: {len(train_df):,} rows ({len(train_df)/(len(train_df)+len(valid_df)+len(test_df))*100:.1f}%)
  - Valid: {len(valid_df):,} rows ({len(valid_df)/(len(train_df)+len(valid_df)+len(test_df))*100:.1f}%)
  - Test: {len(test_df):,} rows ({len(test_df)/(len(train_df)+len(valid_df)+len(test_df))*100:.1f}%)

저장 파일:
  - data_split/train_interactions.csv
  - data_split/valid_interactions.csv
  - data_split/test_interactions.csv

Cold-start (사용자 기반 분할):
  - Valid Cold Users: {len(valid_cold_users)/len(valid_df)*100:.2f}%
  - Test Cold Users: {len(test_cold_users)/len(test_df)*100:.2f}%
  - Valid/Test의 모든 사용자가 Train에 없음 (사용자 기반 분할)
  - 아이템은 Train에 있을 수 있음 (아이템 기반 분할 아님)
""")
print("=" * 70)

