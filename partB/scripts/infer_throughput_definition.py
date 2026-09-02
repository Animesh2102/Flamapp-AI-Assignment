#!/usr/bin/env python3
import csv
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Infer throughput definition")
    default_bench = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "starter kit", "starter_kit", "bench", "bench_log.csv")
    parser.add_argument("--bench-file", type=str, default=default_bench, help="Path to bench_log.csv")
    args = parser.parse_args()
    bench_file = args.bench_file
    
    with open(bench_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print("--- B3 Throughput Definition Inference ---\n")
    
    best_candidate = None
    min_avg_error = float('inf')
    
    candidates = {
        "A: (gen) / wall": lambda r: float(r['gen_len']) / float(r['wall_clock_s']),
        "B: (prompt + gen) / wall": lambda r: (float(r['prompt_len']) + float(r['gen_len'])) / float(r['wall_clock_s']),
        "C: batch * (gen) / wall": lambda r: float(r['batch_size']) * float(r['gen_len']) / float(r['wall_clock_s']),
        "D: batch * (prompt + gen) / wall": lambda r: float(r['batch_size']) * (float(r['prompt_len']) + float(r['gen_len'])) / float(r['wall_clock_s'])
    }
    
    results = {k: [] for k in candidates}
    
    for row in rows:
        if not row['batch_size']: continue
        
        reported = float(row['reported_tok_s'])
        
        for name, func in candidates.items():
            calculated = func(row)
            error = abs(calculated - reported) / reported
            results[name].append(error)
            
    print("Average Error across all rows:")
    for name, errors in results.items():
        avg_err = sum(errors) / len(errors)
        print(f"{name:35} : {avg_err:.4%}")
        
        if avg_err < min_avg_error:
            min_avg_error = avg_err
            best_candidate = name
            
    print(f"\nBest matching definition: {best_candidate}")
    
    # Detailed output for the best candidate
    print("\nRow-by-row for the best candidate:")
    for row in rows:
        if not row['batch_size']: continue
        reported = float(row['reported_tok_s'])
        calculated = candidates[best_candidate](row)
        print(f"Batch {row['batch_size']}, Prompt {row['prompt_len']}: Reported {reported:.1f} vs Calculated {calculated:.1f} (Diff: {abs(reported - calculated):.1f})")

if __name__ == "__main__":
    main()
