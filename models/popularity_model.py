# -*- coding: utf-8 -*-
"""
Phase 3 - Task 3.1: Popularity 모델
모든 사용자에게 가장 인기있는 아이템을 추천하는 Non-personalized Baseline
"""
import pandas as pd
import numpy as np
from collections import defaultdict
import pickle
import os
import sys

# 상위 디렉토리 모듈 임포트
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PopularityModel:
    """
    인기도 기반 추천 모델
    
    특징:
    - Non-personalized: 모든 사용자에게 동일한 추천
    - Cold User에게 효과적인 fallback
    - Baseline 성능 측정용
    """
    
    def __init__(self):
        self.item_popularity = None  # {app_id: interaction_count}
        self.popular_items = None    # 인기도 순 정렬된 아이템 리스트
        self.n_items = 0
        
    def fit(self, train_df, item_col='app_id'):
        """
        학습: 아이템별 상호작용 수 집계
        
        Args:
            train_df: 학습 데이터 (user_id, app_id, ...)
            item_col: 아이템 컬럼명
        """
        print("[Popularity] 모델 학습 시작...")
        
        # 아이템별 상호작용 수 집계
        self.item_popularity = train_df[item_col].value_counts().to_dict()
        
        # 인기도 순 정렬
        self.popular_items = sorted(
            self.item_popularity.keys(),
            key=lambda x: self.item_popularity[x],
            reverse=True
        )
        
        self.n_items = len(self.popular_items)
        
        print(f"  학습 완료: {self.n_items:,}개 아이템")
        print(f"  Top 5 인기 아이템: {self.popular_items[:5]}")
        print(f"  Top 5 상호작용 수: {[self.item_popularity[i] for i in self.popular_items[:5]]}")
        
        return self
    
    def recommend(self, user_id, k=10, exclude_items=None):
        """
        추천 생성: 상위 K개 인기 아이템 반환
        
        Args:
            user_id: 사용자 ID (실제로 사용되지 않음 - Non-personalized)
            k: 추천 개수
            exclude_items: 제외할 아이템 리스트 (이미 상호작용한 아이템)
            
        Returns:
            추천 아이템 리스트 (인기도 순)
        """
        if exclude_items is None:
            exclude_items = set()
        else:
            exclude_items = set(exclude_items)
        
        recommendations = []
        for item in self.popular_items:
            if item not in exclude_items:
                recommendations.append(item)
            if len(recommendations) >= k:
                break
        
        return recommendations
    
    def recommend_batch(self, user_ids, k=10, user_items_dict=None):
        """
        배치 추천: 여러 사용자에게 한 번에 추천
        
        Args:
            user_ids: 사용자 ID 리스트
            k: 추천 개수
            user_items_dict: {user_id: [상호작용한 아이템들]} - 제외용
            
        Returns:
            {user_id: [추천 아이템 리스트]}
        """
        if user_items_dict is None:
            user_items_dict = {}
        
        recommendations = {}
        for user_id in user_ids:
            exclude_items = user_items_dict.get(user_id, [])
            recommendations[user_id] = self.recommend(user_id, k, exclude_items)
        
        return recommendations
    
    def get_item_score(self, item_id):
        """아이템의 인기도 점수 반환"""
        return self.item_popularity.get(item_id, 0)
    
    def save(self, filepath):
        """모델 저장"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'item_popularity': self.item_popularity,
                'popular_items': self.popular_items,
                'n_items': self.n_items
            }, f)
        print(f"  모델 저장: {filepath}")
    
    def load(self, filepath):
        """모델 로드"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.item_popularity = data['item_popularity']
        self.popular_items = data['popular_items']
        self.n_items = data['n_items']
        print(f"  모델 로드: {filepath}")
        return self


def evaluate_popularity_model(model, test_df, k_list=[5, 10, 20], user_items_train=None):
    """
    Popularity 모델 평가
    
    Args:
        model: PopularityModel 인스턴스
        test_df: 테스트 데이터
        k_list: 평가할 K 값들
        user_items_train: {user_id: [train에서 상호작용한 아이템들]}
    """
    from evaluation import recall_at_k, ndcg_at_k, coverage_at_k, novelty_at_k
    
    print("\n[Popularity] 모델 평가 시작...")
    
    # 테스트 데이터에서 사용자별 정답 아이템 추출
    test_user_items = defaultdict(list)
    for _, row in test_df.iterrows():
        test_user_items[row['user_id']].append(row['app_id'])
    
    if user_items_train is None:
        user_items_train = {}
    
    results = {}
    all_recs = []
    
    for k in k_list:
        recalls = []
        ndcgs = []
        
        for user_id, actual_items in test_user_items.items():
            # 추천 생성 (train에서 상호작용한 아이템 제외)
            exclude_items = user_items_train.get(user_id, [])
            rec_items = model.recommend(user_id, k, exclude_items)
            
            # 평가
            recalls.append(recall_at_k(rec_items, actual_items, k))
            ndcgs.append(ndcg_at_k(rec_items, actual_items, k))
            
            if k == k_list[0]:  # 첫 번째 K에서만 수집
                all_recs.append(rec_items)
        
        results[f'Recall@{k}'] = np.mean(recalls)
        results[f'NDCG@{k}'] = np.mean(ndcgs)
    
    # Coverage & Novelty (첫 번째 K 기준)
    k = k_list[0]
    all_items = set(model.popular_items)
    results[f'Coverage@{k}'] = coverage_at_k(all_recs, all_items, k)
    results[f'Novelty@{k}'] = novelty_at_k(all_recs, model.item_popularity, k)
    
    results['n_users'] = len(test_user_items)
    
    return results


if __name__ == "__main__":
    print("=" * 70)
    print("Phase 3 - Task 3.1: Popularity 모델 구현 및 테스트")
    print("=" * 70)
    
    # 데이터 로드
    print("\n[Step 1] 데이터 로드")
    print("-" * 50)
    
    # 필요한 컬럼만 로드 (메모리 최적화)
    loo_train = pd.read_csv("data_split/loo_train.csv", usecols=['user_id', 'app_id'])
    loo_test = pd.read_csv("data_split/loo_test.csv", usecols=['user_id', 'app_id'])
    
    print(f"  LOO Train: {len(loo_train):,} rows")
    print(f"  LOO Test: {len(loo_test):,} rows")
    
    # 모델 학습
    print("\n[Step 2] Popularity 모델 학습")
    print("-" * 50)
    
    model = PopularityModel()
    model.fit(loo_train)
    
    # 샘플 추천 확인
    print("\n[Step 3] 샘플 추천 확인")
    print("-" * 50)
    
    sample_user = loo_test['user_id'].iloc[0]
    sample_rec = model.recommend(sample_user, k=10)
    print(f"  사용자 {sample_user}에 대한 Top-10 추천:")
    for i, item in enumerate(sample_rec[:10]):
        print(f"    {i+1}. app_id={item}, 인기도={model.item_popularity[item]:,}")
    
    # 모델 저장
    print("\n[Step 4] 모델 저장")
    print("-" * 50)
    
    os.makedirs("models", exist_ok=True)
    model.save("models/popularity_model.pkl")
    
    # 평가 (샘플)
    print("\n[Step 5] 모델 평가 (샘플 10,000명)")
    print("-" * 50)
    
    # 샘플링하여 빠른 평가
    sample_test = loo_test.sample(n=min(10000, len(loo_test)), random_state=42)
    sample_test_users = set(sample_test['user_id'].unique())
    
    # 해당 사용자들의 train 상호작용만 추출 (메모리 최적화)
    print("  Train 상호작용 추출 중...")
    train_filtered = loo_train[loo_train['user_id'].isin(sample_test_users)]
    
    # 딕셔너리 구축 (최적화된 방식)
    user_items_train = {}
    for user_id, group in train_filtered.groupby('user_id'):
        user_items_train[user_id] = group['app_id'].tolist()
    
    print(f"  추출 완료: {len(user_items_train):,}명")
    
    # 평가 함수 직접 구현 (evaluation.py 의존성 제거)
    from collections import defaultdict
    import math
    
    def recall_at_k_simple(recommended, actual, k):
        if len(actual) == 0:
            return 0.0
        recommended_k = set(recommended[:k])
        actual_set = set(actual)
        hits = len(recommended_k & actual_set)
        return hits / len(actual_set)
    
    def ndcg_at_k_simple(recommended, actual, k):
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
    
    print("  평가 진행 중...")
    
    # 테스트 데이터에서 사용자별 정답
    test_user_items = defaultdict(list)
    for _, row in sample_test.iterrows():
        test_user_items[row['user_id']].append(row['app_id'])
    
    results = {}
    all_recommended_items = set()
    
    for k in [5, 10, 20]:
        recalls = []
        ndcgs = []
        
        for user_id, actual_items in test_user_items.items():
            exclude_items = user_items_train.get(user_id, [])
            rec_items = model.recommend(user_id, k, exclude_items)
            
            recalls.append(recall_at_k_simple(rec_items, actual_items, k))
            ndcgs.append(ndcg_at_k_simple(rec_items, actual_items, k))
            
            if k == 5:
                all_recommended_items.update(rec_items)
        
        results[f'Recall@{k}'] = np.mean(recalls)
        results[f'NDCG@{k}'] = np.mean(ndcgs)
    
    # Coverage
    results['Coverage@5'] = len(all_recommended_items) / model.n_items
    results['n_users'] = len(test_user_items)
    
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
Popularity 모델 구현 완료!

모델 특성:
  - Non-personalized: 모든 사용자에게 동일 추천
  - 학습된 아이템: {model.n_items:,}개
  - Top 1 인기 아이템: app_id={model.popular_items[0]}
  
샘플 평가 결과 ({results['n_users']:,}명):
  - Recall@5: {results.get('Recall@5', 0):.4f}
  - Recall@10: {results.get('Recall@10', 0):.4f}
  - Recall@20: {results.get('Recall@20', 0):.4f}
  - NDCG@5: {results.get('NDCG@5', 0):.4f}
  - NDCG@10: {results.get('NDCG@10', 0):.4f}
  - NDCG@20: {results.get('NDCG@20', 0):.4f}
  - Coverage@5: {results.get('Coverage@5', 0):.4f}

저장 파일:
  - models/popularity_model.pkl
""")
    print("=" * 70)

