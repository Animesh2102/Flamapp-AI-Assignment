#!/usr/bin/env python3
"""
test_lower.py -- EXP-003: Measure effect of .lower() on GPT-2 token counts
for both English and Hindi corpora.

Compares token counts with and without lowercasing, per line.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import unicodedata
import tiktoken


def read_lines(path: str):
    """Exact copy of fertility.py's read_lines."""
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            line = unicodedata.normalize("NFC", line)
            lines.append(line)
    return lines


def main():
    enc = tiktoken.get_encoding("gpt2")
    encode = enc.encode

    corpora = {
        "eng": "corpus_sample/eng_sample.txt",
        "hin": "corpus_sample/hin_sample.txt",
    }

    for lang, path in corpora.items():
        lines = read_lines(path)
        print(f"\n{'='*80}")
        print(f"Language: {lang} ({path})")
        print(f"{'='*80}")
        print(f"{'Line':>4}  {'text (first 40 chars)':40s}  {'tok(lower)':>10}  {'tok(orig)':>10}  {'delta':>6}  {'%change':>8}")
        print("-" * 90)

        total_lower = 0
        total_orig = 0

        for i, line in enumerate(lines, 1):
            tokens_lower = encode(line.lower())
            tokens_orig = encode(line)

            n_lower = len(tokens_lower)
            n_orig = len(tokens_orig)
            delta = n_lower - n_orig

            total_lower += n_lower
            total_orig += n_orig

            pct = (delta / n_orig * 100) if n_orig > 0 else 0
            flag = " <<<" if delta != 0 else ""

            # Show first 40 chars of original line
            display = line[:40]
            print(f"{i:4d}  {display:40s}  {n_lower:10d}  {n_orig:10d}  {delta:6d}  {pct:7.2f}%{flag}")

            # If there's a difference, show the actual tokens
            if delta != 0:
                print(f"      Tokens (lowered):  {tokens_lower}")
                print(f"      Tokens (original): {tokens_orig}")

        print("-" * 90)
        total_delta = total_lower - total_orig
        total_pct = (total_delta / total_orig * 100) if total_orig > 0 else 0
        print(f"TOTAL: tok(lower)={total_lower}, tok(orig)={total_orig}, delta={total_delta}, change={total_pct:.2f}%")

        # Also compute fertility both ways using split() (corrected split)
        print(f"\nFertility comparison (using corrected split()):")
        fert_lower_list = []
        fert_orig_list = []
        for line in lines:
            words = line.lower().split()  # Using corrected split
            n_words = len(words)
            fert_lower = len(encode(line.lower())) / n_words
            # For original case, we still need words -- use original split
            words_orig = line.split()
            n_words_orig = len(words_orig)
            fert_orig = len(encode(line)) / n_words_orig
            fert_lower_list.append(fert_lower)
            fert_orig_list.append(fert_orig)

        avg_fert_lower = sum(fert_lower_list) / len(fert_lower_list)
        avg_fert_orig = sum(fert_orig_list) / len(fert_orig_list)
        print(f"  Avg fertility (lowered):  {avg_fert_lower:.4f}")
        print(f"  Avg fertility (original): {avg_fert_orig:.4f}")
        print(f"  Delta:                    {avg_fert_lower - avg_fert_orig:.4f}")
        print(f"  Relative change:          {(avg_fert_lower - avg_fert_orig) / avg_fert_orig * 100:.2f}%")


if __name__ == "__main__":
    main()
