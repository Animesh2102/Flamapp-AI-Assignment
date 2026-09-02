#!/usr/bin/env python3
import csv
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Parse benchmark logs")
    default_bench = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "starter kit", "starter_kit", "bench", "bench_log.csv")
    parser.add_argument("--bench-file", type=str, default=default_bench, help="Path to bench_log.csv")
    args = parser.parse_args()
    bench_file = args.bench_file
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "bench_summary.csv")
    
    # We want to identify the long-context sweep where prompt_len = 3584
    # and short-context sweep where prompt_len = 512
    with open(bench_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"Loaded {len(rows)} rows from bench_log.csv")
    print(f"Columns: {reader.fieldnames}")
    
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            
    # Quick analysis
    print("\n--- Long Context Sweep (prompt_len=3584) ---")
    for row in rows:
        if row['prompt_len'] == '3584':
            print(f"Batch: {row['batch_size']}, Requests: {row['num_requests']}, WallTime: {row['wall_clock_s']}s, "
                  f"ReportedTok/s: {row['reported_tok_s']}, Preempts: {row['preempted_seqs']}, "
                  f"KVCache: {row['kv_cache_util']}, E2E p95: {row['e2e_ms_p95']}ms")

if __name__ == "__main__":
    main()
