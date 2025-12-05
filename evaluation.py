# -*- coding: utf-8 -*-
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
