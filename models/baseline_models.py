# -*- coding: utf-8 -*-
"""
Phase 3 - Baseline 모델 종합 구현
1. Random Baseline
2. Most Popular per Tag
3. TruncatedSVD
4. Item Co-occurrence
"""
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, load_npz
from sklearn.decomposition import TruncatedSVD
from collections import defaultdict, Counter
import pickle
import os
import math
import json

print("=" * 70)
print("Phase 3 - Baseline 모델 종합 실험")
print("=" * 70)

# ============================================================
# 공통 함수
# ============================================================
def recall_at_k(recommended, actual, k):
    if len(actual) == 0:
        return 0.0
    recommended_k = set(recommended[:k])
    actual_set = set(actual)
    return len(recommended_k & actual_set) / len(actual_set)

def ndcg_at_k(recommended, actual, k):
    if len(actual) == 0:
        return 0.0
    actual_set = set(actual)
    dcg = sum(1.0 / math.log2(i + 2) for i, item in enumerate(recommended[:k]) if item in actual_set)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(actual_set), k)))
    return dcg / idcg if idcg > 0 else 0.0

def evaluate_model(model_name, recommend_func, test_users, test_user_items, k_list=[5, 10, 20]):
    """모델 평가 공통 함수"""
    results = {}
    all_recommended_items = set()
    
    for k in k_list:
        recalls = []
        ndcgs = []
        
        for user_id in test_users:
            actual_items = test_user_items[user_id]
            rec_items = recommend_func(user_id, k)
            
            if len(rec_items) == 0:
                continue
            
            recalls.append(recall_at_k(rec_items, actual_items, k))
            ndcgs.append(ndcg_at_k(rec_items, actual_items, k))
            
            if k == k_list[0]:
                all_recommended_items.update(rec_items)
        
        results[f'Recall@{k}'] = np.mean(recalls) if recalls else 0.0
        results[f'NDCG@{k}'] = np.mean(ndcgs) if ndcgs else 0.0
    
    results['Coverage@5'] = len(all_recommended_items) / n_items
    results['n_recommended_items'] = len(all_recommended_items)
    
    return results

# ============================================================
# 데이터 로드
# ============================================================
print("\n[Step 1] 데이터 로드")
print("-" * 50)

# LOO Train/Test
loo_train = pd.read_csv("data_split/loo_train.csv", usecols=['user_id', 'app_id'])
loo_test = pd.read_csv("data_split/loo_test.csv", usecols=['user_id', 'app_id'])

# Sparse Matrix 및 매핑
train_sparse = load_npz("data_split/loo_train_sparse.npz")
with open("data_split/loo_mappings.pkl", 'rb') as f:
    mappings = pickle.load(f)

# 메타데이터 (태그)
items_meta = pd.read_csv("merged_items.csv", usecols=['app_id', 'tags_str'])

print(f"  LOO Train: {len(loo_train):,} rows")
print(f"  LOO Test: {len(loo_test):,} rows")
print(f"  Sparse Matrix: {train_sparse.shape}")

n_users, n_items = train_sparse.shape
user_to_idx = mappings['user_to_idx']
idx_to_item = mappings['idx_to_item']
item_to_idx = mappings['item_to_idx']

# 테스트 데이터 준비 (샘플링)
sample_size = 10000
test_sample = loo_test.sample(n=min(sample_size, len(loo_test)), random_state=42)
test_users = test_sample['user_id'].unique()

test_user_items = defaultdict(list)
for _, row in test_sample.iterrows():
    test_user_items[row['user_id']].append(row['app_id'])

# Train에서 사용자별 상호작용
train_user_items = defaultdict(set)
for _, row in loo_train[loo_train['user_id'].isin(test_users)].iterrows():
    train_user_items[row['user_id']].add(row['app_id'])

print(f"  평가 대상 사용자: {len(test_users):,}명")

# 아이템 인기도
item_popularity = loo_train['app_id'].value_counts().to_dict()
all_items = list(item_popularity.keys())

# ============================================================
# Model 1: Random Baseline
# ============================================================
print("\n" + "=" * 70)
print("[Model 1] Random Baseline")
print("=" * 70)

print("""
선정 이유:
  - 가장 단순한 baseline으로 하한선(lower bound) 역할
  - 다른 모델이 "무작위보다 얼마나 좋은가?" 측정 기준
  - 모든 추천시스템 연구에서 기본적으로 포함하는 baseline
""")

np.random.seed(42)

def random_recommend(user_id, k):
    exclude = train_user_items.get(user_id, set())
    candidates = [item for item in all_items if item not in exclude]
    return list(np.random.choice(candidates, size=min(k, len(candidates)), replace=False))

random_results = evaluate_model("Random", random_recommend, test_users, test_user_items)

print("결과:")
for metric, value in random_results.items():
    if isinstance(value, float):
        print(f"  {metric}: {value:.4f}")
    else:
        print(f"  {metric}: {value:,}")

# ============================================================
# Model 2: Most Popular per Tag
# ============================================================
print("\n" + "=" * 70)
print("[Model 2] Most Popular per Tag")
print("=" * 70)

print("""
선정 이유:
  - Wang(2025)의 "파티션별 Popularity" 개념 확장
  - 순수 Popularity보다 약간의 개인화 제공
  - 태그 데이터 활용 (97.6% 게임에 태그 존재)
  - Long-tail 커버리지 향상 기대 (태그별 분산)
""")

# 태그-아이템 매핑
tag_items = defaultdict(list)
item_tags = {}

for _, row in items_meta.iterrows():
    app_id = row['app_id']
    if pd.notna(row['tags_str']) and row['tags_str']:
        tags = row['tags_str'].split(',')
        item_tags[app_id] = tags
        for tag in tags:
            tag_items[tag.strip()].append(app_id)

# 태그별 인기 아이템 (상위 100개)
tag_popular = {}
for tag, items in tag_items.items():
    items_with_pop = [(item, item_popularity.get(item, 0)) for item in items]
    items_with_pop.sort(key=lambda x: x[1], reverse=True)
    tag_popular[tag] = [item for item, _ in items_with_pop[:100]]

print(f"  유니크 태그 수: {len(tag_items):,}")

def popular_per_tag_recommend(user_id, k):
    exclude = train_user_items.get(user_id, set())
    user_items = list(train_user_items.get(user_id, []))
    
    if not user_items:
        # 상호작용 없으면 전체 인기 아이템
        return [item for item in all_items if item not in exclude][:k]
    
    # 사용자가 플레이한 게임의 태그 수집
    user_tags = Counter()
    for item in user_items:
        if item in item_tags:
            user_tags.update(item_tags[item])
    
    # 상위 태그에서 인기 아이템 수집
    candidates = []
    for tag, count in user_tags.most_common(10):
        if tag in tag_popular:
            for item in tag_popular[tag]:
                if item not in exclude and item not in candidates:
                    candidates.append(item)
                    if len(candidates) >= k * 2:
                        break
    
    # 부족하면 전체 인기 아이템 추가
    if len(candidates) < k:
        for item in all_items:
            if item not in exclude and item not in candidates:
                candidates.append(item)
                if len(candidates) >= k:
                    break
    
    return candidates[:k]

tag_pop_results = evaluate_model("PopularPerTag", popular_per_tag_recommend, test_users, test_user_items)

print("결과:")
for metric, value in tag_pop_results.items():
    if isinstance(value, float):
        print(f"  {metric}: {value:.4f}")
    else:
        print(f"  {metric}: {value:,}")

# ============================================================
# Model 3: TruncatedSVD
# ============================================================
print("\n" + "=" * 70)
print("[Model 3] TruncatedSVD (sklearn)")
print("=" * 70)

print("""
선정 이유:
  - sklearn 기본 제공 (설치 문제 없음)
  - ALS와 유사한 Matrix Factorization 개념
  - 대규모 Sparse Matrix에서 매우 빠름
  - Salkanović(2024)에서 SVD 계열이 Steam 데이터에 효과적
""")

# 샘플링하여 학습 (메모리 제한)
sample_users = 50000
if n_users > sample_users:
    sample_idx = np.random.choice(n_users, sample_users, replace=False)
    train_sample_sparse = train_sparse[sample_idx]
else:
    sample_idx = np.arange(n_users)
    train_sample_sparse = train_sparse

print(f"  학습 샘플: {train_sample_sparse.shape[0]:,} users")

# SVD 학습
n_components = 50
print(f"  SVD 학습 중 (n_components={n_components})...")
svd = TruncatedSVD(n_components=n_components, random_state=42)
user_factors = svd.fit_transform(train_sample_sparse)  # users × factors
item_factors = svd.components_.T  # items × factors

print(f"  User factors: {user_factors.shape}")
print(f"  Item factors: {item_factors.shape}")

# 샘플 user idx 매핑
sample_user_to_idx = {mappings['idx_to_user'][idx]: i for i, idx in enumerate(sample_idx)}

def svd_recommend(user_id, k):
    exclude = train_user_items.get(user_id, set())
    
    # 사용자가 SVD 학습에 포함되었는지 확인
    if user_id not in sample_user_to_idx:
        # 포함 안 되면 인기 아이템
        return [item for item in all_items if item not in exclude][:k]
    
    user_idx = sample_user_to_idx[user_id]
    
    # 점수 계산
    scores = user_factors[user_idx] @ item_factors.T
    
    # 이미 상호작용한 아이템 제외
    for item in exclude:
        if item in item_to_idx:
            scores[item_to_idx[item]] = -np.inf
    
    # Top-K
    top_k_idx = np.argpartition(scores, -k)[-k:]
    top_k_idx = top_k_idx[np.argsort(scores[top_k_idx])[::-1]]
    
    return [idx_to_item[idx] for idx in top_k_idx if scores[idx] > -np.inf][:k]

svd_results = evaluate_model("TruncatedSVD", svd_recommend, test_users, test_user_items)

print("결과:")
for metric, value in svd_results.items():
    if isinstance(value, float):
        print(f"  {metric}: {value:.4f}")
    else:
        print(f"  {metric}: {value:,}")

# ============================================================
# Model 4: Item Co-occurrence
# ============================================================
print("\n" + "=" * 70)
print("[Model 4] Item Co-occurrence")
print("=" * 70)

print("""
선정 이유:
  - "이 게임을 한 사람들은 이 게임도 했습니다" (Amazon, Netflix 검증)
  - ItemKNN과 유사하지만 계산이 훨씬 간단
  - Top-K Co-occurrence만 저장하여 메모리 효율적
  - Steam 데이터에서 직관적 (같이 플레이 = 유사)
""")

# Co-occurrence 계산 (샘플 기반)
print("  Co-occurrence 계산 중...")

# 사용자별 아이템 리스트
user_items_list = defaultdict(list)
for _, row in loo_train.iterrows():
    user_items_list[row['user_id']].append(row['app_id'])

# 아이템 쌍 Co-occurrence (샘플 사용자만)
cooccur = defaultdict(Counter)
sample_user_ids = np.random.choice(list(user_items_list.keys()), 
                                   min(100000, len(user_items_list)), replace=False)

for user_id in sample_user_ids:
    items = user_items_list[user_id]
    for i, item1 in enumerate(items):
        for item2 in items[i+1:]:
            cooccur[item1][item2] += 1
            cooccur[item2][item1] += 1

# 각 아이템별 Top-50 Co-occurrence 저장
item_cooccur_top = {}
for item, counter in cooccur.items():
    item_cooccur_top[item] = [i for i, _ in counter.most_common(50)]

print(f"  Co-occurrence 계산 완료: {len(item_cooccur_top):,} items")

def cooccur_recommend(user_id, k):
    exclude = train_user_items.get(user_id, set())
    user_items = list(train_user_items.get(user_id, []))
    
    if not user_items:
        return [item for item in all_items if item not in exclude][:k]
    
    # 사용자가 플레이한 게임의 Co-occurrence 합산
    candidates = Counter()
    for item in user_items:
        if item in item_cooccur_top:
            for co_item in item_cooccur_top[item]:
                if co_item not in exclude:
                    candidates[co_item] += 1
    
    # 인기도 가중치 추가 (tie-breaking)
    for item in candidates:
        candidates[item] += item_popularity.get(item, 0) * 0.0001
    
    result = [item for item, _ in candidates.most_common(k)]
    
    # 부족하면 인기 아이템 추가
    if len(result) < k:
        for item in all_items:
            if item not in exclude and item not in result:
                result.append(item)
                if len(result) >= k:
                    break
    
    return result[:k]

cooccur_results = evaluate_model("CoOccurrence", cooccur_recommend, test_users, test_user_items)

print("결과:")
for metric, value in cooccur_results.items():
    if isinstance(value, float):
        print(f"  {metric}: {value:.4f}")
    else:
        print(f"  {metric}: {value:,}")

# ============================================================
# 결과 종합
# ============================================================
print("\n" + "=" * 70)
print("[결과 종합]")
print("=" * 70)

all_results = {
    'Random': random_results,
    'PopularPerTag': tag_pop_results,
    'TruncatedSVD': svd_results,
    'CoOccurrence': cooccur_results
}

# 이전 Popularity 결과 추가
all_results['Popularity'] = {
    'Recall@5': 0.0279,
    'Recall@10': 0.0450,
    'Recall@20': 0.0746,
    'NDCG@5': 0.0165,
    'NDCG@10': 0.0220,
    'NDCG@20': 0.0295,
    'Coverage@5': 0.0003
}

print("\n| 모델 | Recall@5 | Recall@10 | Recall@20 | NDCG@10 | Coverage@5 |")
print("|------|----------|-----------|-----------|---------|------------|")
for model, results in all_results.items():
    print(f"| {model} | {results.get('Recall@5', 0):.4f} | {results.get('Recall@10', 0):.4f} | {results.get('Recall@20', 0):.4f} | {results.get('NDCG@10', 0):.4f} | {results.get('Coverage@5', 0):.4f} |")

# 결과 저장
with open("models/baseline_results.pkl", 'wb') as f:
    pickle.dump(all_results, f)

print("\n결과 저장: models/baseline_results.pkl")
print("=" * 70)

