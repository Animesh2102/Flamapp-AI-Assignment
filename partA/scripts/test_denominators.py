#!/usr/bin/env python3
"""
test_denominators.py -- EXP-005: Compare cross-language ratios using
multiple denominators on the supplied parallel corpora.

For each denominator, computes:
- per-language total tokens
- per-language total denominator units
- tokens/unit for each language
- Hindi/English ratio
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import unicodedata
import tiktoken

try:
    import regex
    def count_grapheme_clusters(text):
        return len(regex.findall(r'\X', text))
except ImportError:
    def count_grapheme_clusters(text):
        count = 0
        for ch in text:
            if not unicodedata.category(ch).startswith('M'):
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

    # Collect per-language totals
    lang_data = {}
    for lang, path in corpora.items():
        lines = read_lines(path)
        total_tokens = 0
        total_words_space = 0  # split(" ") -- original buggy
        total_words_default = 0  # split() -- corrected
        total_codepoints = 0
        total_graphemes = 0
        total_utf8_bytes = 0
        n_sentences = len(lines)

        for line in lines:
            line_lower = line.lower()
            tokens = encode(line_lower)
            total_tokens += len(tokens)
            total_words_space += len(line_lower.split(" "))
            total_words_default += len(line_lower.split())
            total_codepoints += len(line_lower)
            total_graphemes += count_grapheme_clusters(line_lower)
            total_utf8_bytes += len(line_lower.encode('utf-8'))

        lang_data[lang] = {
            "tokens": total_tokens,
            "words_space": total_words_space,
            "words_default": total_words_default,
            "codepoints": total_codepoints,
            "graphemes": total_graphemes,
            "utf8_bytes": total_utf8_bytes,
            "sentences": n_sentences,
        }

    # Print raw totals
    print("="*80)
    print("RAW TOTALS")
    print("="*80)
    print(f"{'Metric':<20} {'eng':>10} {'hin':>10} {'hin/eng ratio':>15}")
    print("-"*60)
    for key in ["tokens", "words_space", "words_default", "codepoints", "graphemes", "utf8_bytes", "sentences"]:
        e = lang_data["eng"][key]
        h = lang_data["hin"][key]
        ratio = h / e if e > 0 else float('inf')
        print(f"{key:<20} {e:>10} {h:>10} {ratio:>15.4f}")

    # Compute and compare metrics
    denominators = {
        "tok/word (split ' ', buggy)": ("tokens", "words_space"),
        "tok/word (split(), corrected)": ("tokens", "words_default"),
        "tok/codepoint": ("tokens", "codepoints"),
        "tok/grapheme": ("tokens", "graphemes"),
        "tok/utf8_byte": ("tokens", "utf8_bytes"),
        "tok/sentence (parallel)": ("tokens", "sentences"),
    }

    print("\n" + "="*80)
    print("CROSS-LANGUAGE COMPARISON: METRIC VALUES AND RATIOS")
    print("="*80)
    print(f"{'Denominator':<35} {'eng value':>12} {'hin value':>12} {'hin/eng':>10} {'interpretation':>30}")
    print("-"*110)

    for name, (num_key, den_key) in denominators.items():
        eng_val = lang_data["eng"][num_key] / lang_data["eng"][den_key]
        hin_val = lang_data["hin"][num_key] / lang_data["hin"][den_key]
        ratio = hin_val / eng_val

        if "sentence" in name:
            interp = f"hin needs {ratio:.2f}x tokens for same content"
        else:
            interp = f"hin/eng = {ratio:.2f}x"

        print(f"{name:<35} {eng_val:>12.4f} {hin_val:>12.4f} {ratio:>10.4f} {interp:>30}")

    # Key comparison: tok/sentence is the only metric that holds CONTENT constant
    # because the corpora are parallel
    print("\n" + "="*80)
    print("KEY ANALYSIS: What does each ratio tell us about COST?")
    print("="*80)

    eng_tps = lang_data["eng"]["tokens"] / lang_data["eng"]["sentences"]
    hin_tps = lang_data["hin"]["tokens"] / lang_data["hin"]["sentences"]

    print(f"\nTokens per parallel sentence:")
    print(f"  English: {eng_tps:.2f} tokens/sentence")
    print(f"  Hindi:   {hin_tps:.2f} tokens/sentence")
    print(f"  Ratio:   {hin_tps/eng_tps:.2f}x")
    print(f"\nThis ratio answers: 'For the SAME user message, how many more tokens")
    print(f"  does Hindi require than English?'")

    eng_tpw = lang_data["eng"]["tokens"] / lang_data["eng"]["words_default"]
    hin_tpw = lang_data["hin"]["tokens"] / lang_data["hin"]["words_default"]
    print(f"\nTokens per word (corrected split):")
    print(f"  English: {eng_tpw:.2f} tokens/word")
    print(f"  Hindi:   {hin_tpw:.2f} tokens/word")
    print(f"  Ratio:   {hin_tpw/eng_tpw:.2f}x")
    print(f"\nThis ratio answers: 'For each whitespace-delimited word, how many more")
    print(f"  tokens does Hindi need?' (But a Hindi word != an English word in content)")

    print(f"\n  COMPARE: tok/sentence ratio = {hin_tps/eng_tps:.2f}x vs tok/word ratio = {hin_tpw/eng_tpw:.2f}x")
    print(f"  These differ because Hindi uses fewer words to express the same content.")
    print(f"  Eng words = {lang_data['eng']['words_default']}, Hin words = {lang_data['hin']['words_default']} for same sentences.")


if __name__ == "__main__":
    main()
