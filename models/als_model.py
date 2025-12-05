# -*- coding: utf-8 -*-
"""
Phase 3 - Task 3.3: ALS 모델
Alternating Least Squares for Implicit Feedback
순수 NumPy/SciPy 구현 (Hu et al., 2008)
"""
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, load_npz, eye, diags
from scipy.sparse.linalg import spsolve
from collections import defaultdict
import pickle
import os
import sys
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ALSModel:
    """
    ALS (Alternating Least Squares) for Implicit Feedback
    
    구현 기반: Hu, Koren, and Volinsky (2008)
    "Collaborative Filtering for Implicit Feedback Datasets"
    
    특징:
    - Implicit Feedback 전용
    - Matrix Factorization 기반
    - 순수 NumPy/SciPy 구현
    """
    
    def __init__(self, factors=32, regularization=0.1, iterations=10, alpha=40):
        """
        Args:
            factors: Latent factor 차원
            regularization: L2 정규화 계수
            iterations: 학습 반복 횟수
            alpha: Confidence 스케일링 (C = 1 + alpha * R)
        """
        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        self.alpha = alpha
        
        self.user_factors = None  # (n_users, factors)
        self.item_factors = None  # (n_items, factors)
        self.user_item_matrix = None
        self.user_to_idx = None
        self.idx_to_user = None
        self.item_to_idx = None
        self.idx_to_item = None
        self.n_users = 0
        self.n_items = 0
        
    def fit(self, train_sparse, mappings):
        """
        학습: User/Item Factor 행렬 학습
        
        Args:
            train_sparse: CSR sparse matrix (users × items)
            mappings: ID 매핑 딕셔너리
        """
        print(f"[ALS] 모델 학습 시작 (factors={self.factors}, iter={self.iterations})...")
        
        self.user_item_matrix = train_sparse
        self.user_to_idx = mappings['user_to_idx']
        self.idx_to_user = mappings['idx_to_user']
        self.item_to_idx = mappings['item_to_idx']
        self.idx_to_item = mappings['idx_to_item']
        self.n_users, self.n_items = train_sparse.shape
        
        print(f"  행렬 크기: {self.n_users:,} users × {self.n_items:,} items")
        print(f"  Non-zero: {train_sparse.nnz:,}")
        
        # 데이터가 너무 크면 샘플링
        if self.n_users > 100000:
            print(f"  [Notice] 사용자 수가 많아 샘플링 학습...")
            sample_size = 100000
            sample_idx = np.random.choice(self.n_users, sample_size, replace=False)
            train_sample = train_sparse[sample_idx]
            n_users_train = sample_size
        else:
            train_sample = train_sparse
            n_users_train = self.n_users
        
        # Confidence 행렬: C = 1 + alpha * R
        confidence = train_sample.copy()
        confidence.data = 1 + self.alpha * confidence.data
        
        # Preference 행렬: P = (R > 0)
        preference = train_sample.copy()
        preference.data = np.ones_like(preference.data)
        
        # Factor 초기화 (Xavier 초기화)
        np.random.seed(42)
        self.user_factors = np.random.normal(0, 0.01, (n_users_train, self.factors))
        self.item_factors = np.random.normal(0, 0.01, (self.n_items, self.factors))
        
        # 정규화 행렬
        reg_matrix = self.regularization * eye(self.factors)
        
        # ALS 반복 학습
        for iteration in range(self.iterations):
            print(f"  Iteration {iteration + 1}/{self.iterations}...")
            
            # 1. User factors 업데이트 (Item factors 고정)
            YtY = self.item_factors.T @ self.item_factors
            
            for u in range(min(n_users_train, 10000)):  # 메모리 제한
                # 사용자 u가 상호작용한 아이템들
                Cu = confidence[u].toarray().flatten()
                Pu = preference[u].toarray().flatten()
                
                # (Y^T C^u Y + λI)^{-1} Y^T C^u p^u
                Cu_diag = diags(Cu - 1)  # C^u - I
                A = YtY + self.item_factors.T @ Cu_diag @ self.item_factors + reg_matrix
                b = self.item_factors.T @ (Cu * Pu)
                
                self.user_factors[u] = np.linalg.solve(A.toarray() if hasattr(A, 'toarray') else A, b)
            
            # 2. Item factors 업데이트 (User factors 고정)
            XtX = self.user_factors.T @ self.user_factors
            
            for i in range(self.n_items):
                # 아이템 i와 상호작용한 사용자들
                Ci = confidence[:, i].toarray().flatten()
                Pi = preference[:, i].toarray().flatten()
                
                Ci_diag = diags(Ci - 1)
                A = XtX + self.user_factors.T @ Ci_diag @ self.user_factors + reg_matrix
                b = self.user_factors.T @ (Ci * Pi)
                
                self.item_factors[i] = np.linalg.solve(A.toarray() if hasattr(A, 'toarray') else A, b)
            
            # Loss 계산 (선택적)
            if (iteration + 1) % 5 == 0:
                pred = self.user_factors @ self.item_factors.T
                loss = np.sum(confidence.multiply(preference - csr_matrix(pred)).power(2))
                print(f"    Loss: {loss:.4f}")
        
        print(f"  학습 완료!")
        print(f"  User factors: {self.user_factors.shape}")
        print(f"  Item factors: {self.item_factors.shape}")
        
        return self
    
    def recommend(self, user_id, k=10, exclude_items=None):
        """
        추천 생성
        """
        if user_id not in self.user_to_idx:
            return []
        
        user_idx = self.user_to_idx[user_id]
        
        # 학습된 사용자 범위 확인
        if user_idx >= len(self.user_factors):
            return []
        
        # 점수 계산
        scores = self.user_factors[user_idx] @ self.item_factors.T
        
        # 이미 상호작용한 아이템 제외
        user_items = self.user_item_matrix[user_idx].indices
        scores[user_items] = -np.inf
        
        # 추가 제외
        if exclude_items:
            for item in exclude_items:
                if item in self.item_to_idx:
                    scores[self.item_to_idx[item]] = -np.inf
        
        # Top-K
        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx = top_k_idx[np.argsort(scores[top_k_idx])[::-1]]
        
        return [self.idx_to_item[idx] for idx in top_k_idx if scores[idx] > -np.inf][:k]
    
    def save(self, filepath):
        """모델 저장"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'user_factors': self.user_factors,
                'item_factors': self.item_factors,
                'user_to_idx': self.user_to_idx,
                'idx_to_user': self.idx_to_user,
                'item_to_idx': self.item_to_idx,
                'idx_to_item': self.idx_to_item,
                'factors': self.factors,
                'n_users': self.n_users,
                'n_items': self.n_items
            }, f)
        print(f"  모델 저장: {filepath}")
    
    def load(self, filepath):
        """모델 로드"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.user_factors = data['user_factors']
        self.item_factors = data['item_factors']
        self.user_to_idx = data['user_to_idx']
        self.idx_to_user = data['idx_to_user']
        self.item_to_idx = data['item_to_idx']
        self.idx_to_item = data['idx_to_item']
        self.factors = data['factors']
        self.n_users = data['n_users']
        self.n_items = data['n_items']
        return self


def evaluate_als_model(model, test_df, train_sparse, k_list=[5, 10, 20], sample_size=5000):
    """ALS 모델 평가"""
    print("\n[ALS] 모델 평가 시작...")
    
    if len(test_df) > sample_size:
        test_df = test_df.sample(n=sample_size, random_state=42)
    
    test_user_items = defaultdict(list)
    for _, row in test_df.iterrows():
        test_user_items[row['user_id']].append(row['app_id'])
    
    model.user_item_matrix = train_sparse
    
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
    
    results = {}
    all_recommended_items = set()
    evaluated = 0
    
    print(f"  평가 대상: {len(test_user_items):,}명")
    
    for k in k_list:
        recalls = []
        ndcgs = []
        
        for user_id, actual_items in test_user_items.items():
            rec_items = model.recommend(user_id, k)
            
            if len(rec_items) == 0:
                continue
            
            recalls.append(recall_at_k(rec_items, actual_items, k))
            ndcgs.append(ndcg_at_k(rec_items, actual_items, k))
            
            if k == k_list[0]:
                all_recommended_items.update(rec_items)
                evaluated += 1
        
        results[f'Recall@{k}'] = np.mean(recalls) if recalls else 0.0
        results[f'NDCG@{k}'] = np.mean(ndcgs) if ndcgs else 0.0
    
    results['Coverage@5'] = len(all_recommended_items) / model.n_items
    results['n_users_evaluated'] = evaluated
    
    return results


if __name__ == "__main__":
    print("=" * 70)
    print("Phase 3 - Task 3.3: ALS 모델 구현 및 테스트")
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
    
    # 모델 학습 (작은 설정으로)
    print("\n[Step 2] ALS 모델 학습")
    print("-" * 50)
    
    model = ALSModel(factors=32, regularization=0.1, iterations=5, alpha=40)
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
    
    model.save("models/als_model.pkl")
    
    # 평가
    print("\n[Step 5] 모델 평가 (샘플 5,000명)")
    print("-" * 50)
    
    results = evaluate_als_model(
        model, 
        loo_test, 
        train_sparse,
        k_list=[5, 10, 20],
        sample_size=5000
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
ALS 모델 구현 완료!

모델 특성:
  - Matrix Factorization (ALS, 순수 NumPy)
  - factors: {model.factors}
  - iterations: 5
  
샘플 평가 결과:
  - Recall@5: {results.get('Recall@5', 0):.4f}
  - Recall@10: {results.get('Recall@10', 0):.4f}
  - Recall@20: {results.get('Recall@20', 0):.4f}
  - NDCG@5: {results.get('NDCG@5', 0):.4f}
  - NDCG@10: {results.get('NDCG@10', 0):.4f}
  - NDCG@20: {results.get('NDCG@20', 0):.4f}
  - Coverage@5: {results.get('Coverage@5', 0):.4f}

저장 파일:
  - models/als_model.pkl
""")
    print("=" * 70)
