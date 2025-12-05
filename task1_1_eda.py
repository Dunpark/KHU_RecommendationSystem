# -*- coding: utf-8 -*-
"""
Phase 1 - Task 1.1: recommendations.csv 기본 검증
"""
import pandas as pd
import os

print("=" * 70)
print("Phase 1 - Task 1.1: recommendations.csv 기본 검증")
print("=" * 70)

rec_file = "Game Recommendations on Steam/recommendations.csv"

# Step 1: 파일 크기
file_size_gb = os.path.getsize(rec_file) / (1024**3)
print(f"\n[Step 1] 파일 정보")
print(f"  파일 크기: {file_size_gb:.2f} GB")

# Step 2: 컬럼 구조
print(f"\n[Step 2] 컬럼 구조")
sample = pd.read_csv(rec_file, nrows=5)
print(f"  컬럼 ({len(sample.columns)}개): {list(sample.columns)}")
print(f"\n  데이터 타입:")
for col in sample.columns:
    print(f"    - {col}: {sample[col].dtype}")

# Step 3: 샘플 100만 행 검증
print(f"\n[Step 3] 샘플 100만 행 검증")
sample_1m = pd.read_csv(rec_file, nrows=1_000_000)

print(f"\n  유니크 ID 수 (샘플 내):")
print(f"    - user_id: {sample_1m['user_id'].nunique():,}")
print(f"    - app_id: {sample_1m['app_id'].nunique():,}")

print(f"\n  Null 비율:")
for col in sample_1m.columns:
    null_pct = sample_1m[col].isnull().mean() * 100
    status = "WARNING" if null_pct > 0 else "OK"
    print(f"    [{status}] {col}: {null_pct:.4f}%")

print(f"\n  is_recommended 분포:")
rec_dist = sample_1m["is_recommended"].value_counts(normalize=True) * 100
print(f"    - True (추천): {rec_dist.get(True, 0):.1f}%")
print(f"    - False (비추천): {rec_dist.get(False, 0):.1f}%")

print(f"\n  hours 통계:")
print(f"    - 평균: {sample_1m['hours'].mean():.2f} 시간")
print(f"    - 중앙값: {sample_1m['hours'].median():.2f} 시간")
print(f"    - 최대: {sample_1m['hours'].max():.2f} 시간")
print(f"    - 0시간 비율: {(sample_1m['hours'] == 0).mean() * 100:.2f}%")

# Step 4: 전체 행 수 (line count)
print(f"\n[Step 4] 전체 데이터 규모")
print("  행 수 카운트 중... (약 1-2분 소요)")
line_count = 0
with open(rec_file, "r", encoding="utf-8") as f:
    for _ in f:
        line_count += 1
total_rows = line_count - 1  # 헤더 제외
print(f"  총 행 수: {total_rows:,}")

# Step 5: 요약
print("\n" + "=" * 70)
print("[결과 요약]")
print("=" * 70)
print(f"  - 파일 크기: {file_size_gb:.2f} GB")
print(f"  - 총 행 수: {total_rows:,}")
print(f"  - 컬럼 수: {len(sample.columns)}")
print(f"  - 추천 비율: {rec_dist.get(True, 0):.1f}%")
print(f"  - 평균 플레이시간: {sample_1m['hours'].mean():.2f} 시간")
print("=" * 70)

