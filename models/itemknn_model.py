# -*- coding: utf-8 -*-
"""
Phase 3 - Task 3.2: ItemKNN 모델
아이템 간 유사도 기반 협업 필터링
"""
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, load_npz
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import pickle
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ItemKNNModel:
    """
    아이템 기반 협업 필터링 (Item-based CF)
    
    특징:
    - 아이템 간 유사도 기반 추천
    - 사용자가 좋아한 아이템과 유사한 아이템 추천
    - Memory-based CF (모델 프리)
    """
    
    def __init__(self, k_neighbors=50, similarity_metric='cosine'):
        """
        Args:
            k_neighbors: 유사 아이템 수
            similarity_metric: 유사도 측정 방식 ('cosine')
        """
        self.k_neighbors = k_neighbors
        self.similarity_metric = similarity_metric
        
        self.item_similarity = None  # 아이템 유사도 행렬
        self.user_item_matrix = None  # User-Item 상호작용 행렬
        self.item_to_idx = None
        self.idx_to_item = None
        self.user_to_idx = None
        self.idx_to_user = None
        self.n_users = 0
        self.n_items = 0
        
    def fit(self, train_sparse, mappings):
        """
        학습: 아이템 유사도 행렬 계산
        
        Args:
            train_sparse: CSR sparse matrix (users × items)
            mappings: ID 매핑 딕셔너리
        """
        print(f"[ItemKNN] 모델 학습 시작 (k={self.k_neighbors})...")
        
        self.user_item_matrix = train_sparse
        self.user_to_idx = mappings['user_to_idx']
        self.idx_to_user = mappings['idx_to_user']
        self.item_to_idx = mappings['item_to_idx']
        self.idx_to_item = mappings['idx_to_item']
        self.n_users, self.n_items = train_sparse.shape
        
        print(f"  행렬 크기: {self.n_users:,} users × {self.n_items:,} items")
        print(f"  Non-zero: {train_sparse.nnz:,}")
        
        # 아이템-아이템 유사도 계산 (아이템 × 사용자 행렬 필요)
        print("  아이템 유사도 계산 중...")
        
        # 아이템 벡터 = 각 아이템을 좋아한 사용자들 (items × users)
        item_user_matrix = train_sparse.T.tocsr()
        
        # Cosine 유사도 (배치 처리)
        # 메모리 효율을 위해 Top-K만 저장
        print(f"  유사도 행렬 계산 중 ({self.n_items:,} items)...")
        
        # 작은 배치로 처리
        batch_size = 1000
        similarity_data = []
        similarity_rows = []
        similarity_cols = []
        
        for start_idx in range(0, self.n_items, batch_size):
            end_idx = min(start_idx + batch_size, self.n_items)
            
            # 배치의 아이템들과 전체 아이템의 유사도
            batch_matrix = item_user_matrix[start_idx:end_idx]
            batch_sim = cosine_similarity(batch_matrix, item_user_matrix)
            
            # 각 아이템에 대해 Top-K 유사 아이템만 저장
            for i in range(batch_sim.shape[0]):
                item_idx = start_idx + i
                sim_scores = batch_sim[i]
                
                # 자기 자신 제외하고 Top-K
                sim_scores[item_idx] = -1  # 자기 자신 제외
                top_k_idx = np.argpartition(sim_scores, -self.k_neighbors)[-self.k_neighbors:]
                
                for neighbor_idx in top_k_idx:
                    if sim_scores[neighbor_idx] > 0:
                        similarity_rows.append(item_idx)
                        similarity_cols.append(neighbor_idx)
                        similarity_data.append(sim_scores[neighbor_idx])
            
            if (start_idx + batch_size) % 5000 == 0 or end_idx == self.n_items:
                print(f"    진행: {end_idx:,}/{self.n_items:,} items")
        
        # Sparse 유사도 행렬 생성
        self.item_similarity = csr_matrix(
            (similarity_data, (similarity_rows, similarity_cols)),
            shape=(self.n_items, self.n_items)
        )
        
        print(f"  유사도 행렬 완료: {len(similarity_data):,} non-zero")
        print(f"  학습 완료!")
        
        return self
    
    def recommend(self, user_id, k=10, exclude_items=None):
        """
        추천 생성
        
        Args:
            user_id: 원본 사용자 ID
            k: 추천 개수
            exclude_items: 제외할 아이템 (원본 ID)
            
        Returns:
            추천 아이템 리스트 (원본 ID)
        """
        # 사용자 ID → Index
        if user_id not in self.user_to_idx:
            return []  # Cold user
        
        user_idx = self.user_to_idx[user_id]
        
        # 사용자가 상호작용한 아이템들
        user_items = self.user_item_matrix[user_idx].indices
        
        if len(user_items) == 0:
            return []
        
        # 상호작용한 아이템들의 유사 아이템 점수 합산
        scores = np.zeros(self.n_items)
        
        for item_idx in user_items:
            # 해당 아이템과 유사한 아이템들
            sim_row = self.item_similarity[item_idx].toarray().flatten()
            scores += sim_row
        
        # 이미 상호작용한 아이템 제외
        scores[user_items] = -np.inf
        
        # 추가 제외 아이템
        if exclude_items:
            for item in exclude_items:
                if item in self.item_to_idx:
                    scores[self.item_to_idx[item]] = -np.inf
        
        # Top-K 아이템 선택
        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx = top_k_idx[np.argsort(scores[top_k_idx])[::-1]]
        
        # Index → 원본 ID
        recommendations = [self.idx_to_item[idx] for idx in top_k_idx if scores[idx] > -np.inf]
        
        return recommendations[:k]
    
    def save(self, filepath):
        """모델 저장"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'item_similarity': self.item_similarity,
                'user_to_idx': self.user_to_idx,
                'idx_to_user': self.idx_to_user,
                'item_to_idx': self.item_to_idx,
                'idx_to_item': self.idx_to_item,
                'k_neighbors': self.k_neighbors,
                'n_users': self.n_users,
                'n_items': self.n_items
            }, f)
        print(f"  모델 저장: {filepath}")
    
    def load(self, filepath):
        """모델 로드"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.item_similarity = data['item_similarity']
        self.user_to_idx = data['user_to_idx']
        self.idx_to_user = data['idx_to_user']
        self.item_to_idx = data['item_to_idx']
        self.idx_to_item = data['idx_to_item']
        self.k_neighbors = data['k_neighbors']
        self.n_users = data['n_users']
        self.n_items = data['n_items']
        print(f"  모델 로드: {filepath}")
        return self


def evaluate_itemknn_model(model, test_df, train_sparse, k_list=[5, 10, 20], sample_size=10000):
    """
    ItemKNN 모델 평가
    """
    import math
    
    print("\n[ItemKNN] 모델 평가 시작...")
    
    # 샘플링
    if len(test_df) > sample_size:
        test_df = test_df.sample(n=sample_size, random_state=42)
    
    # 테스트 사용자별 정답
    test_user_items = defaultdict(list)
    for _, row in test_df.iterrows():
        test_user_items[row['user_id']].append(row['app_id'])
    
    # User-Item Matrix 설정 (추천 시 사용)
    model.user_item_matrix = train_sparse
    
    def recall_at_k(recommended, actual, k):
        if len(actual) == 0:
            return 0.0
        recommended_k = set(recommended[:k])
        actual_set = set(actual)
        hits = len(recommended_k & actual_set)
        return hits / len(actual_set)
    
    def ndcg_at_k(recommended, actual, k):
        if len(actual) == 0:
            return 0.0
        actual_set = set(actual)
        dcg = 0.0
        for i, item in enumerate(recommended[:k]):
            if item in actual_set:
                dcg += 1.0 / math.log2(i + 2)
        idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(actual_set), k)))
        if idcg == 0:
            return 0.0
        return dcg / idcg
    
    results = {}
    all_recommended_items = set()
    
    print(f"  평가 대상: {len(test_user_items):,}명")
    
    evaluated = 0
    for k in k_list:
        recalls = []
        ndcgs = []
        
        for user_id, actual_items in test_user_items.items():
            rec_items = model.recommend(user_id, k)
            
            if len(rec_items) == 0:
                continue  # Cold user 스킵
            
            recalls.append(recall_at_k(rec_items, actual_items, k))
            ndcgs.append(ndcg_at_k(rec_items, actual_items, k))
            
            if k == k_list[0]:
                all_recommended_items.update(rec_items)
                evaluated += 1
        
        if recalls:
            results[f'Recall@{k}'] = np.mean(recalls)
            results[f'NDCG@{k}'] = np.mean(ndcgs)
        else:
            results[f'Recall@{k}'] = 0.0
            results[f'NDCG@{k}'] = 0.0
    
    # Coverage
    results['Coverage@5'] = len(all_recommended_items) / model.n_items
    results['n_users_evaluated'] = evaluated
    
    return results


if __name__ == "__main__":
    print("=" * 70)
    print("Phase 3 - Task 3.2: ItemKNN 모델 구현 및 테스트")
    print("=" * 70)
    
    # 데이터 로드
    print("\n[Step 1] 데이터 로드")
    print("-" * 50)
    
    train_sparse = load_npz("data_split/loo_train_sparse.npz")
    
    with open("data_split/loo_mappings.pkl", 'rb') as f:
        mappings = pickle.load(f)
    
    loo_test = pd.read_csv("data_split/loo_test.csv", usecols=['user_id', 'app_id'])
    
    print(f"  Train Sparse: {train_sparse.shape}")
    print(f"  LOO Test: {len(loo_test):,} rows")
    
    # 모델 학습
    print("\n[Step 2] ItemKNN 모델 학습")
    print("-" * 50)
    
    model = ItemKNNModel(k_neighbors=50)
    model.fit(train_sparse, mappings)
    
    # 샘플 추천 확인
    print("\n[Step 3] 샘플 추천 확인")
    print("-" * 50)
    
    sample_user = loo_test['user_id'].iloc[0]
    sample_rec = model.recommend(sample_user, k=10)
    print(f"  사용자 {sample_user}에 대한 Top-10 추천:")
    for i, item in enumerate(sample_rec[:10]):
        print(f"    {i+1}. app_id={item}")
    
    # 모델 저장
    print("\n[Step 4] 모델 저장")
    print("-" * 50)
    
    model.save("models/itemknn_model.pkl")
    
    # 평가
    print("\n[Step 5] 모델 평가 (샘플 10,000명)")
    print("-" * 50)
    
    results = evaluate_itemknn_model(
        model, 
        loo_test, 
        train_sparse,
        k_list=[5, 10, 20],
        sample_size=10000
    )
    
    print("\n  평가 결과:")
    for metric, value in results.items():
        if isinstance(value, float):
            print(f"    {metric}: {value:.4f}")
        else:
            print(f"    {metric}: {value:,}")
    
    print("\n" + "=" * 70)
    print("[결과 요약]")
    print("=" * 70)
    print(f"""
ItemKNN 모델 구현 완료!

모델 특성:
  - Item-based Collaborative Filtering
  - k_neighbors: {model.k_neighbors}
  - 아이템 수: {model.n_items:,}개
  
샘플 평가 결과:
  - Recall@5: {results.get('Recall@5', 0):.4f}
  - Recall@10: {results.get('Recall@10', 0):.4f}
  - Recall@20: {results.get('Recall@20', 0):.4f}
  - NDCG@5: {results.get('NDCG@5', 0):.4f}
  - NDCG@10: {results.get('NDCG@10', 0):.4f}
  - NDCG@20: {results.get('NDCG@20', 0):.4f}
  - Coverage@5: {results.get('Coverage@5', 0):.4f}
  - 평가된 사용자: {results.get('n_users_evaluated', 0):,}명

저장 파일:
  - models/itemknn_model.pkl
""")
    print("=" * 70)

