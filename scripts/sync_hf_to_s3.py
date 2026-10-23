"""
Synchronize Full HuggingFace Dataset (data/hf_git_clone) to Amazon S3
Zero downsampling, all 3,445 files across all 735 failure cases.
"""

import os
import sys
import time
from pathlib import Path
import concurrent.futures as cf
import boto3

def sync_local_to_s3(
    local_dir: str = "data/hf_git_clone",
    bucket_name: str = "telecom-rca-benchmark-dev-397669520479",
    s3_prefix: str = "rcaeval",
    aws_region: str = "us-east-1",
    max_workers: int = 32
):
    s3 = boto3.client("s3", region_name=aws_region)
    s3.head_bucket(Bucket=bucket_name)
    print(f"[OK] Connected to s3://{bucket_name}/", flush=True)

    local_path = Path(local_dir).resolve()
    all_files = [
        f for f in local_path.rglob("*")
        if f.is_file() and ".git" not in f.parts and not f.name.startswith(".")
    ]
    print(f"[SCAN] Found {len(all_files)} total files in {local_path}.", flush=True)

    # Fetch existing keys to avoid re-uploading identical objects
    print("[SCAN] Fetching existing S3 inventory...", flush=True)
    existing_keys = {}
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix):
        for obj in page.get("Contents", []):
            existing_keys[obj["Key"]] = obj["Size"]

    print(f"[INVENTORY] Found {len(existing_keys)} existing objects in S3.", flush=True)

    files_to_upload = []
    for f in all_files:
        rel_posix = f.relative_to(local_path).as_posix()
        s3_key = f"{s3_prefix}/{rel_posix}".replace("//", "/")
        f_size = f.stat().st_size
        if s3_key not in existing_keys or existing_keys[s3_key] != f_size:
            files_to_upload.append((f, s3_key))

    print(f"[DELTA] {len(files_to_upload)} new or modified files to synchronize.", flush=True)
    if not files_to_upload:
        print("[COMPLETE] All files already synchronized with S3!", flush=True)
        return True

    start_time = time.time()
    uploaded = 0
    failed = 0

    def upload_one(item):
        f_path, k = item
        try:
            s3.upload_file(str(f_path), bucket_name, k)
            return True, k
        except Exception as e:
            return False, f"{k} ({e})"

    with cf.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(upload_one, item): item for item in files_to_upload}
        for i, future in enumerate(cf.as_completed(futures), 1):
            ok, msg = future.result()
            if ok:
                uploaded += 1
            else:
                failed += 1
            if i % 100 == 0 or i == len(files_to_upload):
                pct = (i / len(files_to_upload)) * 100.0
                elapsed = time.time() - start_time
                print(f"  Progress: {i}/{len(files_to_upload)} files ({pct:.1f}%) in {elapsed:.1f}s", flush=True)

    print(f"\n[DONE] Successfully uploaded {uploaded} files in {time.time() - start_time:.2f}s (Failed: {failed})", flush=True)
    return failed == 0

if __name__ == "__main__":
    b = sys.argv[1] if len(sys.argv) > 1 else "telecom-rca-benchmark-dev-397669520479"
    sync_local_to_s3(bucket_name=b)
