# -*- coding: utf-8 -*-
"""
Phase 2 - Task 2.1: 파티션 교차 분석
Popular/Long-tail × Heavy/Light 4개 그룹 분석
"""
import pandas as pd
import numpy as np
from collections import defaultdict

print("=" * 70)
print("Phase 2 - Task 2.1: 파티션 교차 분석")
print("=" * 70)

# ============================================================
# Step 1: 파티션 정보 로드
# ============================================================
print("\n[Step 1] 파티션 정보 로드")
print("-" * 50)

items = pd.read_csv("merged_items.csv", usecols=['app_id', 'item_partition', 'interaction_count'])
users = pd.read_csv("merged_users.csv", usecols=['user_id', 'user_partition', 'review_count'])

print(f"  아이템: {len(items):,} (Popular: {(items['item_partition']=='Popular').sum():,}, Long-tail: {(items['item_partition']=='Long-tail').sum():,})")
print(f"  사용자: {len(users):,} (Heavy: {(users['user_partition']=='Heavy').sum():,}, Light: {(users['user_partition']=='Light').sum():,})")

# 파티션 딕셔너리 생성
item_partition_dict = dict(zip(items['app_id'], items['item_partition']))
user_partition_dict = dict(zip(users['user_id'], users['user_partition']))

# ============================================================
# Step 2: 상호작용 청크 처리 - 그룹별 집계
# ============================================================
print("\n[Step 2] 상호작용 청크 처리 - 그룹별 집계")
print("-" * 50)

rec_file = "Game Recommendations on Steam/recommendations.csv"

# 그룹별 카운터
group_counts = defaultdict(int)
group_hours = defaultdict(list)
group_recommended = defaultdict(list)

total_rows = 0
chunk_size = 2_000_000

print("  청크 처리 중...")
for chunk in pd.read_csv(rec_file, chunksize=chunk_size, 
                          usecols=['app_id', 'user_id', 'hours', 'is_recommended']):
    
    # 파티션 매핑
    chunk['item_part'] = chunk['app_id'].map(item_partition_dict).fillna('Long-tail')
    chunk['user_part'] = chunk['user_id'].map(user_partition_dict).fillna('Light')
    
    # 4개 그룹 생성
    chunk['group'] = chunk['item_part'] + '_' + chunk['user_part']
    
    # 그룹별 집계
    for group, g_df in chunk.groupby('group'):
        group_counts[group] += len(g_df)
        # 샘플링하여 hours, is_recommended 저장 (메모리 효율)
        if len(group_hours[group]) < 100000:
            group_hours[group].extend(g_df['hours'].sample(min(1000, len(g_df))).tolist())
            group_recommended[group].extend(g_df['is_recommended'].sample(min(1000, len(g_df))).tolist())
    
    total_rows += len(chunk)
    if total_rows % 10_000_000 == 0:
        print(f"    {total_rows:,} rows 처리...")

print(f"\n  총 처리: {total_rows:,} rows")

# ============================================================
# Step 3: 그룹별 상호작용 분포
# ============================================================
print("\n[Step 3] 그룹별 상호작용 분포")
print("-" * 50)

groups = ['Popular_Heavy', 'Popular_Light', 'Long-tail_Heavy', 'Long-tail_Light']
total_interactions = sum(group_counts.values())

print("\n  [상호작용 분포표]")
print(f"  {'그룹':<20} {'상호작용 수':>15} {'비율':>10}")
print("  " + "-" * 47)

for group in groups:
    count = group_counts[group]
    pct = count / total_interactions * 100
    print(f"  {group:<20} {count:>15,} {pct:>9.2f}%")

print("  " + "-" * 47)
print(f"  {'합계':<20} {total_interactions:>15,} {100.0:>9.2f}%")

# ============================================================
# Step 4: 아이템/사용자 파티션별 합계
# ============================================================
print("\n[Step 4] 파티션별 합계")
print("-" * 50)

# 아이템 파티션
popular_total = group_counts['Popular_Heavy'] + group_counts['Popular_Light']
longtail_total = group_counts['Long-tail_Heavy'] + group_counts['Long-tail_Light']

print("\n  [아이템 파티션]")
print(f"    Popular: {popular_total:,} ({popular_total/total_interactions*100:.2f}%)")
print(f"    Long-tail: {longtail_total:,} ({longtail_total/total_interactions*100:.2f}%)")

# 사용자 파티션
heavy_total = group_counts['Popular_Heavy'] + group_counts['Long-tail_Heavy']
light_total = group_counts['Popular_Light'] + group_counts['Long-tail_Light']

print("\n  [사용자 파티션]")
print(f"    Heavy: {heavy_total:,} ({heavy_total/total_interactions*100:.2f}%)")
print(f"    Light: {light_total:,} ({light_total/total_interactions*100:.2f}%)")

# ============================================================
# Step 5: 그룹별 상세 통계
# ============================================================
print("\n[Step 5] 그룹별 상세 통계")
print("-" * 50)

print("\n  [플레이 시간 (hours)]")
print(f"  {'그룹':<20} {'평균':>10} {'중앙값':>10}")
print("  " + "-" * 42)
for group in groups:
    hours = group_hours[group]
    if hours:
        avg = np.mean(hours)
        med = np.median(hours)
        print(f"  {group:<20} {avg:>10.1f} {med:>10.1f}")

print("\n  [추천 비율 (is_recommended=True)]")
print(f"  {'그룹':<20} {'추천 비율':>10}")
print("  " + "-" * 32)
for group in groups:
    recs = group_recommended[group]
    if recs:
        rec_rate = np.mean(recs) * 100
        print(f"  {group:<20} {rec_rate:>9.1f}%")

# ============================================================
# Step 6: 교차 분석 매트릭스
# ============================================================
print("\n[Step 6] 교차 분석 매트릭스")
print("-" * 50)

print("\n  [상호작용 수]")
print(f"  {'':>15} {'Heavy':>15} {'Light':>15} {'합계':>15}")
print("  " + "-" * 62)
print(f"  {'Popular':>15} {group_counts['Popular_Heavy']:>15,} {group_counts['Popular_Light']:>15,} {popular_total:>15,}")
print(f"  {'Long-tail':>15} {group_counts['Long-tail_Heavy']:>15,} {group_counts['Long-tail_Light']:>15,} {longtail_total:>15,}")
print("  " + "-" * 62)
print(f"  {'합계':>15} {heavy_total:>15,} {light_total:>15,} {total_interactions:>15,}")

print("\n  [상호작용 비율 (%)]")
print(f"  {'':>15} {'Heavy':>15} {'Light':>15} {'합계':>15}")
print("  " + "-" * 62)
ph = group_counts['Popular_Heavy']/total_interactions*100
pl = group_counts['Popular_Light']/total_interactions*100
lh = group_counts['Long-tail_Heavy']/total_interactions*100
ll = group_counts['Long-tail_Light']/total_interactions*100
print(f"  {'Popular':>15} {ph:>14.2f}% {pl:>14.2f}% {popular_total/total_interactions*100:>14.2f}%")
print(f"  {'Long-tail':>15} {lh:>14.2f}% {ll:>14.2f}% {longtail_total/total_interactions*100:>14.2f}%")
print("  " + "-" * 62)
print(f"  {'합계':>15} {heavy_total/total_interactions*100:>14.2f}% {light_total/total_interactions*100:>14.2f}% {100.0:>14.2f}%")

# ============================================================
# Step 7: 핵심 인사이트
# ============================================================
print("\n[Step 7] 핵심 인사이트")
print("-" * 50)

# Popular_Heavy vs Long-tail_Light 비교
ph_count = group_counts['Popular_Heavy']
ll_count = group_counts['Long-tail_Light']

print(f"""
  ⭐ 핵심 발견:
  
  1. Popular × Heavy (협업 신호 풍부)
     - 상호작용: {ph_count:,} ({ph_count/total_interactions*100:.2f}%)
     - CF 모델의 핵심 학습 데이터
     
  2. Long-tail × Light (Cold-start 심각)
     - 상호작용: {ll_count:,} ({ll_count/total_interactions*100:.2f}%)
     - CF만으로는 추천 불가능
     - Content 피처 의존 필수
     
  3. 불균형 비율
     - Popular_Heavy / Long-tail_Light = {ph_count/ll_count:.2f}x
     - Heavy 사용자가 Popular 아이템에 집중
""")

# ============================================================
# 결과 요약
# ============================================================
print("\n" + "=" * 70)
print("[결과 요약]")
print("=" * 70)
print(f"""
교차 분석 결과:
  - Popular × Heavy: {group_counts['Popular_Heavy']:,} ({group_counts['Popular_Heavy']/total_interactions*100:.2f}%)
  - Popular × Light: {group_counts['Popular_Light']:,} ({group_counts['Popular_Light']/total_interactions*100:.2f}%)
  - Long-tail × Heavy: {group_counts['Long-tail_Heavy']:,} ({group_counts['Long-tail_Heavy']/total_interactions*100:.2f}%)
  - Long-tail × Light: {group_counts['Long-tail_Light']:,} ({group_counts['Long-tail_Light']/total_interactions*100:.2f}%)

모델링 시사점:
  - CF 모델: Popular × Heavy에서 높은 성능 예상
  - Content 모델: Long-tail × Light에서 CF 보완 필요
  - Hybrid 전략: 그룹별 가중치 차등 적용 권장
""")
print("=" * 70)

