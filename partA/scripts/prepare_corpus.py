#!/usr/bin/env python3
"""
prepare_corpus.py -- A1: Download and prepare FLORES-200 devtest corpus
for multilingual fertility evaluation.

Languages: English (eng_Latn), Hindi (hin_Deva), Kannada (kan_Knda), Tamil (tam_Taml)

Downloads from a public HuggingFace mirror of FLORES-200 to avoid gating issues.
"""

import sys
import io
import os
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    try:
        from datasets import load_dataset
    except ImportError:
        print("ERROR: 'datasets' library is required. Please install it.")
        sys.exit(1)

    print("Loading FLORES-200 devtest from HuggingFace mirror 'yash9439/flores200'...")
    try:
        ds = load_dataset("yash9439/flores200", split="devtest")
    except Exception as e:
        print(f"FAILED to load dataset: {e}")
        sys.exit(1)

    print(f"Dataset loaded: {len(ds)} rows.")
    
    # Target languages in the FLORES-200 dataset format
    targets = {
        "eng": "eng_Latn",
        "hin": "hin_Deva",
        "kan": "kan_Knda",
        "tam": "tam_Taml",
    }

    # Verify all target columns exist
    for lang, col in targets.items():
        if col not in ds.column_names:
            print(f"ERROR: Column '{col}' not found for {lang}!")
            sys.exit(1)

    # Output directory
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus")
    os.makedirs(out_dir, exist_ok=True)

    print("\nExtracting and normalizing sentences...")
    for lang, col in targets.items():
        out_path = os.path.join(out_dir, f"{lang}.txt")
        n_written = 0
        n_skipped = 0
        with open(out_path, "w", encoding="utf-8") as f:
            for row in ds:
                text = str(row[col]).strip()
                if not text:
                    n_skipped += 1
                    continue
                # Normalize text
                text = unicodedata.normalize("NFC", text)
                f.write(text + "\n")
                n_written += 1
        print(f"  {lang}: wrote {n_written} sentences to {out_path} (skipped {n_skipped})")

    # Validate parallelism
    print("\nValidating parallelism...")
    counts = {}
    for lang in targets:
        out_path = os.path.join(out_dir, f"{lang}.txt")
        with open(out_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        counts[lang] = len(lines)
        print(f"  {lang}: {len(lines)} non-empty lines")

    if len(set(counts.values())) == 1:
        print(f"\n  PASS: All languages have {list(counts.values())[0]} parallel sentences.")
    else:
        print(f"\n  WARNING: Line counts differ: {counts}")

    print("\nCorpus statistics:")
    for lang in targets:
        out_path = os.path.join(out_dir, f"{lang}.txt")
        with open(out_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        total_chars = sum(len(l) for l in lines)
        total_bytes = sum(len(l.encode('utf-8')) for l in lines)
        total_words = sum(len(l.split()) for l in lines)
        print(f"  {lang}: {len(lines)} sentences, {total_words} words, {total_chars} codepoints, {total_bytes} bytes")

if __name__ == "__main__":
    main()
