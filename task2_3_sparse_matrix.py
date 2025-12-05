# -*- coding: utf-8 -*-
"""
Phase 2 - Task 2.3: Sparse Matrix 구축
User-Item 상호작용 행렬 (CSR 포맷)
"""
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, save_npz
import pickle
import os

print("=" * 70)
print("Phase 2 - Task 2.3: Sparse Matrix 구축")
print("=" * 70)

# ============================================================
# Step 1: Train 데이터 로드
# ============================================================
print("\n[Step 1] Train 데이터 로드")
print("-" * 50)

train = pd.read_csv("data_split/train_interactions.csv", 
                     usecols=['user_id', 'app_id', 'hours', 'is_recommended'])

print(f"  Train 상호작용: {len(train):,}")
print(f"  유니크 사용자: {train['user_id'].nunique():,}")
print(f"  유니크 아이템: {train['app_id'].nunique():,}")

# ============================================================
# Step 2: ID → Index 매핑 생성
# ============================================================
print("\n[Step 2] ID → Index 매핑 생성")
print("-" * 50)

# 유니크 ID 추출
unique_users = train['user_id'].unique()
unique_items = train['app_id'].unique()

# 매핑 딕셔너리
user_to_idx = {uid: idx for idx, uid in enumerate(unique_users)}
idx_to_user = {idx: uid for uid, idx in user_to_idx.items()}

item_to_idx = {iid: idx for idx, iid in enumerate(unique_items)}
idx_to_item = {idx: iid for iid, idx in item_to_idx.items()}

n_users = len(unique_users)
n_items = len(unique_items)

print(f"  사용자 수 (n_users): {n_users:,}")
print(f"  아이템 수 (n_items): {n_items:,}")
print(f"  행렬 크기: {n_users:,} × {n_items:,} = {n_users * n_items:,} cells")
print(f"  실제 상호작용: {len(train):,}")
print(f"  희소율 (Sparsity): {(1 - len(train) / (n_users * n_items)) * 100:.6f}%")

# ============================================================
# Step 3: Index 변환
# ============================================================
print("\n[Step 3] Index 변환")
print("-" * 50)

train['user_idx'] = train['user_id'].map(user_to_idx)
train['item_idx'] = train['app_id'].map(item_to_idx)

print(f"  user_idx 범위: 0 ~ {train['user_idx'].max()}")
print(f"  item_idx 범위: 0 ~ {train['item_idx'].max()}")

# ============================================================
# Step 4: Sparse Matrix 생성 (Binary)
# ============================================================
print("\n[Step 4] Sparse Matrix 생성 (Binary)")
print("-" * 50)

# Binary matrix (상호작용 존재 여부)
row = train['user_idx'].values
col = train['item_idx'].values
data = np.ones(len(train), dtype=np.float32)

sparse_binary = csr_matrix((data, (row, col)), shape=(n_users, n_items))

print(f"  Binary Matrix 생성 완료")
print(f"    Shape: {sparse_binary.shape}")
print(f"    Non-zero: {sparse_binary.nnz:,}")
print(f"    Density: {sparse_binary.nnz / (n_users * n_items) * 100:.6f}%")
print(f"    Memory (data): {sparse_binary.data.nbytes / 1024**2:.2f} MB")

# ============================================================
# Step 5: Sparse Matrix 생성 (Hours 가중치)
# ============================================================
print("\n[Step 5] Sparse Matrix 생성 (Hours 가중치)")
print("-" * 50)

# Hours를 로그 변환하여 가중치로 사용 (1 + log(1 + hours))
# 0시간도 최소 1의 가중치를 갖도록
train['weight'] = 1 + np.log1p(train['hours'])

data_weighted = train['weight'].values.astype(np.float32)
sparse_weighted = csr_matrix((data_weighted, (row, col)), shape=(n_users, n_items))

print(f"  Weighted Matrix 생성 완료")
print(f"    Shape: {sparse_weighted.shape}")
print(f"    Non-zero: {sparse_weighted.nnz:,}")
print(f"    Weight 통계:")
print(f"      평균: {train['weight'].mean():.3f}")
print(f"      최소: {train['weight'].min():.3f}")
print(f"      최대: {train['weight'].max():.3f}")
print(f"    Memory (data): {sparse_weighted.data.nbytes / 1024**2:.2f} MB")

# ============================================================
# Step 6: 파일 저장
# ============================================================
print("\n[Step 6] 파일 저장")
print("-" * 50)

os.makedirs("data_split", exist_ok=True)

# Sparse Matrix 저장 (.npz)
save_npz("data_split/train_sparse_binary.npz", sparse_binary)
save_npz("data_split/train_sparse_weighted.npz", sparse_weighted)

# 매핑 저장 (pickle)
mappings = {
    'user_to_idx': user_to_idx,
    'idx_to_user': idx_to_user,
    'item_to_idx': item_to_idx,
    'idx_to_item': idx_to_item,
    'n_users': n_users,
    'n_items': n_items
}

with open("data_split/id_mappings.pkl", 'wb') as f:
    pickle.dump(mappings, f)

print(f"  저장 완료:")
print(f"    data_split/train_sparse_binary.npz")
print(f"    data_split/train_sparse_weighted.npz")
print(f"    data_split/id_mappings.pkl")

# ============================================================
# Step 7: Valid/Test 데이터도 Index 변환
# ============================================================
print("\n[Step 7] Valid/Test 데이터 Index 변환")
print("-" * 50)

for split_name in ['valid', 'test']:
    df = pd.read_csv(f"data_split/{split_name}_interactions.csv",
                      usecols=['user_id', 'app_id', 'hours', 'is_recommended'])
    
    # Index 변환 (Train에 없는 ID는 -1)
    df['user_idx'] = df['user_id'].map(user_to_idx).fillna(-1).astype(int)
    df['item_idx'] = df['app_id'].map(item_to_idx).fillna(-1).astype(int)
    
    # 유효한 상호작용만 필터링 (Train에 있는 아이템만)
    valid_mask = (df['user_idx'] >= 0) & (df['item_idx'] >= 0)
    df_valid = df[valid_mask]
    
    print(f"\n  [{split_name.upper()}]")
    print(f"    원본: {len(df):,}")
    print(f"    유효 (Train 아이템): {len(df_valid):,} ({len(df_valid)/len(df)*100:.2f}%)")
    print(f"    제외 (Cold Item): {len(df) - len(df_valid):,}")
    
    # 저장
    df_valid.to_csv(f"data_split/{split_name}_indexed.csv", index=False)

# ============================================================
# Step 8: 검증
# ============================================================
print("\n[Step 8] 검증")
print("-" * 50)

# 저장된 파일 로드 테스트
from scipy.sparse import load_npz

loaded_binary = load_npz("data_split/train_sparse_binary.npz")
with open("data_split/id_mappings.pkl", 'rb') as f:
    loaded_mappings = pickle.load(f)

print(f"  로드 테스트:")
print(f"    Binary Matrix Shape: {loaded_binary.shape}")
print(f"    n_users: {loaded_mappings['n_users']:,}")
print(f"    n_items: {loaded_mappings['n_items']:,}")

# 샘플 사용자의 상호작용 확인
sample_user_idx = 0
sample_user_id = loaded_mappings['idx_to_user'][sample_user_idx]
sample_interactions = loaded_binary[sample_user_idx].indices

print(f"\n  샘플 사용자 (idx=0, id={sample_user_id}):")
print(f"    상호작용 아이템 수: {len(sample_interactions)}")
if len(sample_interactions) > 0:
    sample_items = [loaded_mappings['idx_to_item'][idx] for idx in sample_interactions[:5]]
    print(f"    상호작용 아이템 (처음 5개): {sample_items}")

# ============================================================
# 결과 요약
# ============================================================
print("\n" + "=" * 70)
print("[결과 요약]")
print("=" * 70)
print(f"""
Sparse Matrix 구축 완료:
  - 사용자 수: {n_users:,}
  - 아이템 수: {n_items:,}
  - 상호작용 수: {sparse_binary.nnz:,}
  - 희소율: {(1 - sparse_binary.nnz / (n_users * n_items)) * 100:.6f}%

저장 파일:
  - data_split/train_sparse_binary.npz (Binary Matrix)
  - data_split/train_sparse_weighted.npz (Hours 가중치)
  - data_split/id_mappings.pkl (ID 매핑)
  - data_split/valid_indexed.csv (Index 변환된 Valid)
  - data_split/test_indexed.csv (Index 변환된 Test)

모델 입력 형식:
  - ALS/BPR: train_sparse_binary.npz 또는 train_sparse_weighted.npz
  - 평가: valid_indexed.csv, test_indexed.csv
""")
print("=" * 70)

