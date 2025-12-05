# -*- coding: utf-8 -*-
"""
Phase 2 - Task 2.4: 실험 데이터셋 최종 준비
Leave-One-Out 분할 + 평가 함수 구현
"""
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, save_npz
import pickle
import os
from collections import defaultdict

print("=" * 70)
print("Phase 2 - Task 2.4: 실험 데이터셋 최종 준비")
print("=" * 70)

np.random.seed(42)

# ============================================================
# Step 1: Train 데이터 로드
# ============================================================
print("\n[Step 1] Train 데이터 로드")
print("-" * 50)

train = pd.read_csv("data_split/train_interactions.csv")
print(f"  원본 Train: {len(train):,} rows")
print(f"  유니크 사용자: {train['user_id'].nunique():,}")
print(f"  유니크 아이템: {train['app_id'].nunique():,}")

# ============================================================
# Step 2: Leave-One-Out 분할 생성
# ============================================================
print("\n[Step 2] Leave-One-Out 분할 생성")
print("-" * 50)

# 각 사용자별로 마지막 상호작용을 Test로 분리
# (date 컬럼이 있으므로 시간순 정렬 후 마지막 선택)

print("  날짜 기준 정렬 중...")
train['date'] = pd.to_datetime(train['date'])
train = train.sort_values(['user_id', 'date'])

print("  Leave-One-Out 분할 중...")
# 각 사용자의 마지막 상호작용 인덱스
last_indices = train.groupby('user_id').tail(1).index

# LOO Test: 각 사용자의 마지막 상호작용
loo_test = train.loc[last_indices].copy()

# LOO Train: 나머지 상호작용
loo_train = train.drop(last_indices).copy()

print(f"\n  LOO 분할 결과:")
print(f"    LOO Train: {len(loo_train):,} rows")
print(f"    LOO Test: {len(loo_test):,} rows")
print(f"    Test 사용자 수: {loo_test['user_id'].nunique():,}")

# 최소 2개 이상 상호작용이 있는 사용자만 유지
# (Train에 1개 이상, Test에 1개)
train_user_counts = loo_train['user_id'].value_counts()
valid_users = train_user_counts[train_user_counts >= 1].index

loo_train = loo_train[loo_train['user_id'].isin(valid_users)]
loo_test = loo_test[loo_test['user_id'].isin(valid_users)]

print(f"\n  필터링 후 (Train >= 1 상호작용):")
print(f"    LOO Train: {len(loo_train):,} rows")
print(f"    LOO Test: {len(loo_test):,} rows")
print(f"    Test 사용자 수: {loo_test['user_id'].nunique():,}")

# ============================================================
# Step 3: LOO 데이터 저장
# ============================================================
print("\n[Step 3] LOO 데이터 저장")
print("-" * 50)

loo_train.to_csv("data_split/loo_train.csv", index=False)
loo_test.to_csv("data_split/loo_test.csv", index=False)

print(f"  data_split/loo_train.csv 저장 완료")
print(f"  data_split/loo_test.csv 저장 완료")

# ============================================================
# Step 4: LOO용 Sparse Matrix 생성
# ============================================================
print("\n[Step 4] LOO용 Sparse Matrix 생성")
print("-" * 50)

# 유니크 ID
unique_users = loo_train['user_id'].unique()
unique_items = loo_train['app_id'].unique()

# 매핑
loo_user_to_idx = {uid: idx for idx, uid in enumerate(unique_users)}
loo_idx_to_user = {idx: uid for uid, idx in loo_user_to_idx.items()}
loo_item_to_idx = {iid: idx for idx, iid in enumerate(unique_items)}
loo_idx_to_item = {idx: iid for iid, idx in loo_item_to_idx.items()}

n_users = len(unique_users)
n_items = len(unique_items)

print(f"  사용자 수: {n_users:,}")
print(f"  아이템 수: {n_items:,}")

# Index 변환
loo_train['user_idx'] = loo_train['user_id'].map(loo_user_to_idx)
loo_train['item_idx'] = loo_train['app_id'].map(loo_item_to_idx)

# Sparse Matrix
row = loo_train['user_idx'].values
col = loo_train['item_idx'].values
data = np.ones(len(loo_train), dtype=np.float32)

loo_sparse = csr_matrix((data, (row, col)), shape=(n_users, n_items))

print(f"  LOO Sparse Matrix: {loo_sparse.shape}")
print(f"  Non-zero: {loo_sparse.nnz:,}")

# 저장
save_npz("data_split/loo_train_sparse.npz", loo_sparse)

loo_mappings = {
    'user_to_idx': loo_user_to_idx,
    'idx_to_user': loo_idx_to_user,
    'item_to_idx': loo_item_to_idx,
    'idx_to_item': loo_idx_to_item,
    'n_users': n_users,
    'n_items': n_items
}

with open("data_split/loo_mappings.pkl", 'wb') as f:
    pickle.dump(loo_mappings, f)

print(f"  data_split/loo_train_sparse.npz 저장 완료")
print(f"  data_split/loo_mappings.pkl 저장 완료")

# ============================================================
# Step 5: LOO Test Index 변환
# ============================================================
print("\n[Step 5] LOO Test Index 변환")
print("-" * 50)

loo_test['user_idx'] = loo_test['user_id'].map(loo_user_to_idx)
loo_test['item_idx'] = loo_test['app_id'].map(loo_item_to_idx).fillna(-1).astype(int)

# 유효한 Test만 (Train에 있는 아이템)
valid_test = loo_test[loo_test['item_idx'] >= 0]

print(f"  LOO Test 원본: {len(loo_test):,}")
print(f"  LOO Test 유효 (Train 아이템): {len(valid_test):,} ({len(valid_test)/len(loo_test)*100:.2f}%)")

valid_test.to_csv("data_split/loo_test_indexed.csv", index=False)
print(f"  data_split/loo_test_indexed.csv 저장 완료")

# ============================================================
# Step 6: 파티션 정보 매핑
# ============================================================
print("\n[Step 6] 파티션 정보 매핑")
print("-" * 50)

items_meta = pd.read_csv("merged_items.csv", usecols=['app_id', 'item_partition'])
users_meta = pd.read_csv("merged_users.csv", usecols=['user_id', 'user_partition'])

item_partition_dict = dict(zip(items_meta['app_id'], items_meta['item_partition']))
user_partition_dict = dict(zip(users_meta['user_id'], users_meta['user_partition']))

# LOO Test에 파티션 추가
valid_test['item_partition'] = valid_test['app_id'].map(item_partition_dict).fillna('Long-tail')
valid_test['user_partition'] = valid_test['user_id'].map(user_partition_dict).fillna('Light')
valid_test['group'] = valid_test['item_partition'] + '_' + valid_test['user_partition']

print(f"\n  LOO Test 파티션 분포:")
group_dist = valid_test['group'].value_counts(normalize=True) * 100
for group, pct in group_dist.items():
    print(f"    {group}: {pct:.2f}%")

# 파티션 정보와 함께 저장
valid_test.to_csv("data_split/loo_test_with_partition.csv", index=False)
print(f"\n  data_split/loo_test_with_partition.csv 저장 완료")

# ============================================================
# Step 7: 평가 함수 생성
# ============================================================
print("\n[Step 7] 평가 함수 생성")
print("-" * 50)

eval_code = '''# -*- coding: utf-8 -*-
"""
평가 함수 모듈
Recall@K, NDCG@K, Coverage, Novelty
"""
import numpy as np
from collections import defaultdict

def recall_at_k(recommended, actual, k):
    """
    Recall@K: 추천 목록 상위 K개 중 실제 선호 아이템 비율
    
    Args:
        recommended: 추천 아이템 리스트 (순위순)
        actual: 실제 선호 아이템 (set 또는 list)
        k: 상위 K개
    
    Returns:
        recall 값 (0~1)
    """
    if len(actual) == 0:
        return 0.0
    
    recommended_k = set(recommended[:k])
    actual_set = set(actual)
    
    hits = len(recommended_k & actual_set)
    return hits / len(actual_set)


def ndcg_at_k(recommended, actual, k):
    """
    NDCG@K: Normalized Discounted Cumulative Gain
    
    Args:
        recommended: 추천 아이템 리스트 (순위순)
        actual: 실제 선호 아이템 (set 또는 list)
        k: 상위 K개
    
    Returns:
        ndcg 값 (0~1)
    """
    if len(actual) == 0:
        return 0.0
    
    actual_set = set(actual)
    
    # DCG
    dcg = 0.0
    for i, item in enumerate(recommended[:k]):
        if item in actual_set:
            dcg += 1.0 / np.log2(i + 2)  # i+2 because rank starts from 1
    
    # IDCG (이상적인 경우)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(actual_set), k)))
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def coverage_at_k(all_recommendations, all_items, k):
    """
    Coverage@K: 추천된 유니크 아이템 비율
    
    Args:
        all_recommendations: 모든 사용자의 추천 리스트 (list of lists)
        all_items: 전체 아이템 집합
        k: 상위 K개
    
    Returns:
        coverage 값 (0~1)
    """
    recommended_items = set()
    for rec in all_recommendations:
        recommended_items.update(rec[:k])
    
    return len(recommended_items) / len(all_items)


def novelty_at_k(all_recommendations, item_popularity, k):
    """
    Novelty@K: 추천 아이템의 평균 비인기도
    
    Args:
        all_recommendations: 모든 사용자의 추천 리스트 (list of lists)
        item_popularity: {item_id: popularity_score} (인기도 높을수록 큰 값)
        k: 상위 K개
    
    Returns:
        novelty 값 (높을수록 Long-tail 추천 많음)
    """
    total_novelty = 0.0
    count = 0
    
    max_pop = max(item_popularity.values()) if item_popularity else 1
    
    for rec in all_recommendations:
        for item in rec[:k]:
            pop = item_popularity.get(item, 0)
            # 비인기도 = 1 - (정규화된 인기도)
            novelty = 1 - (pop / max_pop)
            total_novelty += novelty
            count += 1
    
    return total_novelty / count if count > 0 else 0.0


def evaluate_recommendations(recommendations, test_data, item_popularity, all_items, k_list=[5, 10, 20]):
    """
    전체 평가 수행
    
    Args:
        recommendations: {user_id: [추천 아이템 리스트]}
        test_data: {user_id: [실제 선호 아이템]}
        item_popularity: {item_id: popularity}
        all_items: 전체 아이템 집합
        k_list: 평가할 K 값들
    
    Returns:
        결과 딕셔너리
    """
    results = {}
    
    for k in k_list:
        recalls = []
        ndcgs = []
        all_recs = []
        
        for user_id, rec_list in recommendations.items():
            if user_id not in test_data:
                continue
            
            actual = test_data[user_id]
            
            recalls.append(recall_at_k(rec_list, actual, k))
            ndcgs.append(ndcg_at_k(rec_list, actual, k))
            all_recs.append(rec_list)
        
        results[f'Recall@{k}'] = np.mean(recalls)
        results[f'NDCG@{k}'] = np.mean(ndcgs)
        results[f'Coverage@{k}'] = coverage_at_k(all_recs, all_items, k)
        results[f'Novelty@{k}'] = novelty_at_k(all_recs, item_popularity, k)
    
    return results


def evaluate_by_partition(recommendations, test_df, item_popularity, all_items, k_list=[5, 10, 20]):
    """
    파티션별 분리 평가
    
    Args:
        recommendations: {user_id: [추천 아이템 리스트]}
        test_df: Test DataFrame (user_id, app_id, group 포함)
        item_popularity: {item_id: popularity}
        all_items: 전체 아이템 집합
        k_list: 평가할 K 값들
    
    Returns:
        파티션별 결과 딕셔너리
    """
    # 그룹별 test_data 생성
    group_results = {}
    
    for group in test_df['group'].unique():
        group_df = test_df[test_df['group'] == group]
        
        # test_data 구성
        test_data = defaultdict(list)
        for _, row in group_df.iterrows():
            test_data[row['user_id']].append(row['app_id'])
        
        # 해당 그룹 사용자만 필터링
        group_recs = {u: r for u, r in recommendations.items() if u in test_data}
        
        if len(group_recs) == 0:
            continue
        
        results = evaluate_recommendations(group_recs, dict(test_data), 
                                          item_popularity, all_items, k_list)
        results['n_users'] = len(group_recs)
        group_results[group] = results
    
    return group_results


if __name__ == "__main__":
    # 테스트
    print("평가 함수 테스트")
    
    # 샘플 데이터
    rec = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    actual = [3, 7, 15]
    
    print(f"  Recall@5: {recall_at_k(rec, actual, 5):.4f}")
    print(f"  Recall@10: {recall_at_k(rec, actual, 10):.4f}")
    print(f"  NDCG@5: {ndcg_at_k(rec, actual, 5):.4f}")
    print(f"  NDCG@10: {ndcg_at_k(rec, actual, 10):.4f}")
'''

with open("evaluation.py", 'w', encoding='utf-8') as f:
    f.write(eval_code)

print(f"  evaluation.py 저장 완료")

# 테스트 실행
exec(eval_code)

# ============================================================
# Step 8: 실험 설정 요약
# ============================================================
print("\n[Step 8] 실험 설정 요약")
print("-" * 50)

# 아이템 인기도 계산
item_popularity = loo_train['app_id'].value_counts().to_dict()

print(f"""
  실험 데이터셋:
    - LOO Train: {len(loo_train):,} rows ({len(unique_users):,} users, {len(unique_items):,} items)
    - LOO Test: {len(valid_test):,} rows
    
  평가 시나리오:
    1. 전체 평가: 모든 사용자 대상
    2. 파티션별 평가: 4개 그룹 분리 평가
       - Popular × Heavy
       - Popular × Light
       - Long-tail × Heavy
       - Long-tail × Light
  
  평가 지표 (K=5, 10, 20):
    - Recall@K: 추천 정확도
    - NDCG@K: 순위 품질
    - Coverage@K: 다양성
    - Novelty@K: 신선도 (Long-tail 추천 비율)
""")

# ============================================================
# 결과 요약
# ============================================================
print("\n" + "=" * 70)
print("[결과 요약]")
print("=" * 70)
print(f"""
생성 파일:
  1. data_split/loo_train.csv ({len(loo_train):,} rows)
  2. data_split/loo_test.csv ({len(loo_test):,} rows)
  3. data_split/loo_train_sparse.npz (Sparse Matrix)
  4. data_split/loo_mappings.pkl (ID 매핑)
  5. data_split/loo_test_indexed.csv (Index 변환)
  6. data_split/loo_test_with_partition.csv (파티션 포함)
  7. evaluation.py (평가 함수)

LOO 분할 통계:
  - 사용자 수: {n_users:,}
  - 아이템 수: {n_items:,}
  - Train 상호작용: {len(loo_train):,}
  - Test 상호작용: {len(valid_test):,}

Phase 2 완료! Phase 3 (Baseline 모델 구현)으로 진행 가능
""")
print("=" * 70)

