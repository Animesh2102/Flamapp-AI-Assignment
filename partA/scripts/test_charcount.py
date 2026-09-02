#!/usr/bin/env python3
"""
test_charcount.py -- EXP-004: Compare len(line) (codepoints) vs grapheme
cluster count for Hindi, and measure effect on tok/char metric.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import unicodedata
import tiktoken

# Use the regex module for grapheme cluster counting (\X)
try:
    import regex
    HAS_REGEX = True
except ImportError:
    HAS_REGEX = False
    print("WARNING: 'regex' module not available. Using manual Unicode segmentation.")


def count_grapheme_clusters(text):
    """Count grapheme clusters using regex \\X pattern."""
    if HAS_REGEX:
        return len(regex.findall(r'\X', text))
    else:
        # Fallback: approximate by counting non-combining characters
        count = 0
        for ch in text:
            cat = unicodedata.category(ch)
            # Skip combining marks (Mn, Mc, Me)
            if not cat.startswith('M'):
                count += 1
        return count


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
        print(f"\n{'='*90}")
        print(f"Language: {lang} ({path})")
        print(f"{'='*90}")
        print(f"{'Line':>4}  {'text (first 30)':30s}  {'codepoints':>10}  {'graphemes':>10}  {'diff':>6}  {'utf8_bytes':>10}  {'tokens':>7}  {'tok/cp':>8}  {'tok/gr':>8}  {'tok/byte':>9}")
        print("-" * 140)

        total_codepoints = 0
        total_graphemes = 0
        total_utf8 = 0
        total_tokens = 0

        tpc_cp_list = []
        tpc_gr_list = []
        tpc_byte_list = []

        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            tokens = encode(line_lower)
            n_tokens = len(tokens)

            n_codepoints = len(line_lower)
            n_graphemes = count_grapheme_clusters(line_lower)
            n_utf8 = len(line_lower.encode('utf-8'))

            total_codepoints += n_codepoints
            total_graphemes += n_graphemes
            total_utf8 += n_utf8
            total_tokens += n_tokens

            tpc_cp = n_tokens / n_codepoints
            tpc_gr = n_tokens / n_graphemes
            tpc_byte = n_tokens / n_utf8

            tpc_cp_list.append(tpc_cp)
            tpc_gr_list.append(tpc_gr)
            tpc_byte_list.append(tpc_byte)

            diff = n_codepoints - n_graphemes
            flag = " <<<" if diff != 0 else ""

            display = line[:30]
            print(f"{i:4d}  {display:30s}  {n_codepoints:10d}  {n_graphemes:10d}  {diff:6d}  {n_utf8:10d}  {n_tokens:7d}  {tpc_cp:8.4f}  {tpc_gr:8.4f}  {tpc_byte:9.4f}{flag}")

        print("-" * 140)
        print(f"TOTAL: codepoints={total_codepoints}, graphemes={total_graphemes}, diff={total_codepoints - total_graphemes}, utf8_bytes={total_utf8}, tokens={total_tokens}")
        print(f"  Codepoints vs graphemes difference: {total_codepoints - total_graphemes} ({(total_codepoints - total_graphemes)/total_graphemes * 100:.2f}%)")
        print(f"\n  Average tok/codepoint:  {sum(tpc_cp_list)/len(tpc_cp_list):.4f}")
        print(f"  Average tok/grapheme:   {sum(tpc_gr_list)/len(tpc_gr_list):.4f}")
        print(f"  Average tok/utf8_byte:  {sum(tpc_byte_list)/len(tpc_byte_list):.4f}")
        print(f"  Delta tok/cp vs tok/gr: {sum(tpc_cp_list)/len(tpc_cp_list) - sum(tpc_gr_list)/len(tpc_gr_list):.4f}")


if __name__ == "__main__":
    main()
