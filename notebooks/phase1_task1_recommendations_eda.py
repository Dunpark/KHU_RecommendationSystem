"""
Phase 1 – Task 1.1: recommendations.csv 로드 전략 수립 및 기본 검증
Steam 게임 추천 시스템 프로젝트
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os

# 프로젝트 루트 설정
PROJECT_ROOT = Path(r"D:\지원-curusr제발\추천시스템_팀플")
DATA_PATH = PROJECT_ROOT / "Game Recommendations on Steam"

print("=" * 70)
print("Phase 1 – Task 1.1: recommendations.csv 로드 전략 수립 및 기본 검증")
print("=" * 70)

# ============================================================
# Step 1: 파일 존재 확인 및 기본 정보
# ============================================================
print("\n[Step 1] 파일 기본 정보 확인")
print("-" * 50)

rec_file = DATA_PATH / "recommendations.csv"
file_size_gb = os.path.getsize(rec_file) / (1024**3)
print(f"파일 경로: {rec_file}")
print(f"파일 크기: {file_size_gb:.2f} GB")

# ============================================================
# Step 2: 컬럼 구조 확인 (첫 5행만)
# ============================================================
print("\n[Step 2] 컬럼 구조 확인")
print("-" * 50)

sample_df = pd.read_csv(rec_file, nrows=5)
print(f"컬럼 목록 ({len(sample_df.columns)}개):")
for col in sample_df.columns:
    print(f"  - {col}: {sample_df[col].dtype}")

print("\n첫 5행 샘플:")
print(sample_df.to_string())

# ============================================================
# Step 3: Chunked Reading으로 전체 통계 집계
# ============================================================
print("\n[Step 3] Chunked Reading으로 전체 통계 집계")
print("-" * 50)

CHUNK_SIZE = 1_000_000  # 100만 행씩

# 집계 변수 초기화
total_rows = 0
null_counts = None
user_ids = set()
app_ids = set()
is_recommended_counts = {True: 0, False: 0}
hours_sum = 0
hours_count = 0
hours_max = 0

print(f"청크 크기: {CHUNK_SIZE:,} rows")
print("처리 중...")

chunk_num = 0
for chunk in pd.read_csv(rec_file, chunksize=CHUNK_SIZE):
    chunk_num += 1
    total_rows += len(chunk)
    
    # Null 집계
    if null_counts is None:
        null_counts = chunk.isnull().sum()
    else:
        null_counts += chunk.isnull().sum()
    
    # 유니크 ID 수집
    user_ids.update(chunk['user_id'].unique())
    app_ids.update(chunk['app_id'].unique())
    
    # is_recommended 분포
    rec_counts = chunk['is_recommended'].value_counts()
    for val, cnt in rec_counts.items():
        is_recommended_counts[val] += cnt
    
    # hours 통계 (NaN 제외)
    valid_hours = chunk['hours'].dropna()
    hours_sum += valid_hours.sum()
    hours_count += len(valid_hours)
    hours_max = max(hours_max, valid_hours.max())
    
    if chunk_num % 5 == 0:
        print(f"  청크 {chunk_num} 완료 - 누적 {total_rows:,} rows")

print(f"\n총 {chunk_num}개 청크 처리 완료!")

# ============================================================
# Step 4: 결과 요약
# ============================================================
print("\n" + "=" * 70)
print("[결과 요약] recommendations.csv 기본 검증")
print("=" * 70)

print(f"\n📊 기본 통계:")
print(f"  - 총 행 수: {total_rows:,}")
print(f"  - 유니크 user_id 수: {len(user_ids):,}")
print(f"  - 유니크 app_id 수: {len(app_ids):,}")
print(f"  - 평균 interactions/user: {total_rows/len(user_ids):.2f}")
print(f"  - 평균 interactions/item: {total_rows/len(app_ids):.2f}")

print(f"\n🔍 Null 값 현황:")
for col, cnt in null_counts.items():
    pct = cnt / total_rows * 100
    status = "⚠️" if pct > 0 else "✅"
    print(f"  {status} {col}: {cnt:,} ({pct:.4f}%)")

print(f"\n👍 is_recommended 분포:")
total_rec = sum(is_recommended_counts.values())
for val, cnt in is_recommended_counts.items():
    pct = cnt / total_rec * 100
    label = "추천" if val else "비추천"
    print(f"  - {label}: {cnt:,} ({pct:.1f}%)")

print(f"\n⏱️ hours (플레이타임) 통계:")
hours_mean = hours_sum / hours_count if hours_count > 0 else 0
print(f"  - 유효 데이터 수: {hours_count:,}")
print(f"  - 평균: {hours_mean:.2f} 시간")
print(f"  - 최대: {hours_max:.2f} 시간")

print(f"\n📐 데이터 밀도 (Density):")
density = total_rows / (len(user_ids) * len(app_ids)) * 100
print(f"  - User-Item Matrix Density: {density:.6f}%")
print(f"  - (매우 희소한 데이터 - 전형적인 추천시스템 특성)")

# ============================================================
# Step 5: 로드 전략 권고
# ============================================================
print("\n" + "=" * 70)
print("[권고] 효율적인 데이터 처리 전략")
print("=" * 70)

print("""
1. 전체 데이터 활용 시:
   - Sparse Matrix (scipy.sparse.csr_matrix) 사용 권장
   - user_id, app_id를 0부터 시작하는 인덱스로 매핑 필요
   
2. 개발/테스트 단계:
   - Heavy users 또는 Popular items 서브셋으로 축소 가능
   - 예: 상위 10만 유저 + 상위 1만 아이템으로 프로토타이핑
   
3. 메모리 효율:
   - user_id, app_id: int32로 다운캐스팅 가능
   - is_recommended: bool (1 byte)
   - hours: float32로 충분
""")

print("\n" + "=" * 70)
print("Phase 1 – Task 1.1 완료")
print("=" * 70)

