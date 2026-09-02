#!/usr/bin/env python3
"""
test_split.py -- EXP-002: Diagnose line.split(" ") vs line.split() behavior
on the supplied corpora.

Measures:
1. Per-line word counts using split(" ") vs split()
2. Per-line fertility using each method
3. Overall fertility using each method
4. Delta between the two approaches
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
        print(f"\n{'='*70}")
        print(f"Language: {lang} ({path})")
        print(f"{'='*70}")
        print(f"{'Line':>4}  {'split(\" \") words':>16}  {'split() words':>14}  {'Δ words':>8}  {'tokens':>7}  {'fert(\" \")':>10}  {'fert()':>8}  {'Δ fert':>8}")
        print("-" * 100)

        fert_space_list = []
        fert_default_list = []

        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            tokens = encode(line_lower)
            n_tokens = len(tokens)

            words_space = line_lower.split(" ")
            words_default = line_lower.split()

            n_words_space = len(words_space)
            n_words_default = len(words_default)
            delta_words = n_words_space - n_words_default

            fert_space = n_tokens / n_words_space
            fert_default = n_tokens / n_words_default
            delta_fert = fert_space - fert_default

            fert_space_list.append(fert_space)
            fert_default_list.append(fert_default)

            # Flag lines with differences
            flag = " <<<" if delta_words != 0 else ""
            print(f"{i:4d}  {n_words_space:16d}  {n_words_default:14d}  {delta_words:8d}  {n_tokens:7d}  {fert_space:10.4f}  {fert_default:8.4f}  {delta_fert:8.4f}{flag}")

            # If there's a difference, show the actual word lists
            if delta_words != 0:
                print(f"      split(' '): {words_space}")
                print(f"      split():    {words_default}")

        avg_fert_space = sum(fert_space_list) / len(fert_space_list)
        avg_fert_default = sum(fert_default_list) / len(fert_default_list)

        print("-" * 100)
        print(f"{'AVG':>4}  {'':>16}  {'':>14}  {'':>8}  {'':>7}  {avg_fert_space:10.4f}  {avg_fert_default:8.4f}  {avg_fert_space - avg_fert_default:8.4f}")
        print(f"\n  Average fertility with split(' '): {avg_fert_space:.4f}")
        print(f"  Average fertility with split():    {avg_fert_default:.4f}")
        print(f"  Delta:                             {avg_fert_space - avg_fert_default:.4f}")
        print(f"  Relative change:                   {(avg_fert_space - avg_fert_default) / avg_fert_default * 100:.2f}%")


if __name__ == "__main__":
    main()
