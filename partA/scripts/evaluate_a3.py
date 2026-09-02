#!/usr/bin/env python3
"""
evaluate_a3.py -- A3 tokenization evaluation script

Computes tokens and various denominators (words, sentences, codepoints, graphemes, bytes)
for the A1 parallel corpus using specified tokenizers.
"""

import os
import sys
import argparse
import statistics
import unicodedata
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import tiktoken
except ImportError:
    pass

try:
    from transformers import AutoTokenizer
except ImportError:
    pass

try:
    from uniseg.graphemecluster import grapheme_clusters
except ImportError:
    print("ERROR: uniseg is required. Please install it (pip install uniseg).")
    sys.exit(1)

LANGS = ['eng', 'hin', 'kan', 'tam']

def count_graphemes(text):
    return sum(1 for _ in grapheme_clusters(text))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokenizer", type=str, required=True, help="Tokenizer name (e.g., gpt2, o200k_base)")
    args = parser.parse_args()

    is_tiktoken = False
    is_transformers = False
    
    try:
        enc = tiktoken.get_encoding(args.tokenizer)
        is_tiktoken = True
    except Exception:
        try:
            enc = AutoTokenizer.from_pretrained(args.tokenizer)
            is_transformers = True
        except Exception as e:
            print(f"ERROR: Could not load tokenizer {args.tokenizer} via tiktoken or transformers. ({e})")
            sys.exit(1)
    corpus_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus")

    print(f"==================================================")
    print(f"A3 Evaluation: Tokenizer = {args.tokenizer}")
    print(f"==================================================\n")

    results = {}
    
    for lang in LANGS:
        filepath = os.path.join(corpus_dir, f"{lang}.txt")
        if not os.path.exists(filepath):
            print(f"ERROR: {filepath} not found.")
            sys.exit(1)
            
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]

        total_tokens = 0
        total_words = 0
        total_codepoints = 0
        total_bytes = 0
        total_graphemes = 0
        
        sentence_tokens = []
        
        for line in lines:
            if is_tiktoken:
                tokens = enc.encode(line)
            else:
                tokens = enc.encode(line, add_special_tokens=False)
                
            n_toks = len(tokens)
            
            total_tokens += n_toks
            sentence_tokens.append(n_toks)
            
            # Words using .split() correctly
            total_words += len(line.split())
            
            # Codepoints
            total_codepoints += len(line)
            
            # Bytes
            total_bytes += len(line.encode("utf-8"))
            
            # Graphemes
            total_graphemes += count_graphemes(line)
            
        results[lang] = {
            "sentences": len(lines),
            "tokens": total_tokens,
            "words": total_words,
            "codepoints": total_codepoints,
            "bytes": total_bytes,
            "graphemes": total_graphemes,
            "mean_toks_per_sent": statistics.mean(sentence_tokens),
            "median_toks_per_sent": statistics.median(sentence_tokens),
            "stdev_toks_per_sent": statistics.stdev(sentence_tokens) if len(sentence_tokens) > 1 else 0
        }

    eng_res = results['eng']

    for lang in LANGS:
        res = results[lang]
        
        tok_ratio = res["tokens"] / eng_res["tokens"]
        
        print(f"--- Language: {lang.upper()} ---")
        print(f"Totals:")
        print(f"  Sentences:  {res['sentences']}")
        print(f"  Tokens:     {res['tokens']} (Ratio to Eng: {tok_ratio:.2f}x)")
        print(f"  Words:      {res['words']}")
        print(f"  Codepoints: {res['codepoints']}")
        print(f"  Graphemes:  {res['graphemes']}")
        print(f"  Bytes:      {res['bytes']}")
        
        print(f"\nDenominators (Metrics):")
        print(f"  Tok / Sentence:  {res['tokens'] / res['sentences']:.2f}")
        print(f"  Tok / Word:      {res['tokens'] / res['words']:.2f}")
        print(f"  Tok / Codepoint: {res['tokens'] / res['codepoints']:.3f}")
        print(f"  Tok / Grapheme:  {res['tokens'] / res['graphemes']:.3f}")
        print(f"  Tok / Byte:      {res['tokens'] / res['bytes']:.3f}")
        
        print(f"\nSentence Token Distribution:")
        print(f"  Mean:   {res['mean_toks_per_sent']:.2f} tokens")
        print(f"  Median: {res['median_toks_per_sent']:.1f} tokens")
        print(f"  StDev:  {res['stdev_toks_per_sent']:.2f} tokens\n")
        
        if lang != 'eng':
            print(f"Cost Multiplier (vs English):")
            print(f"  Based on tok/sentence: { (res['tokens'] / res['sentences']) / (eng_res['tokens'] / eng_res['sentences']) :.2f}x")
            print(f"  Based on tok/word:     { (res['tokens'] / res['words']) / (eng_res['tokens'] / eng_res['words']) :.2f}x")
            print(f"")

if __name__ == "__main__":
    main()
