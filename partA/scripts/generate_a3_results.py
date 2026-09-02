#!/usr/bin/env python3
import os
import io
import sys
import statistics
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import tiktoken
    from transformers import AutoTokenizer
    from uniseg.graphemecluster import grapheme_clusters
except ImportError:
    print("ERROR: Missing dependencies.")
    sys.exit(1)

def count_graphemes(text):
    return sum(1 for _ in grapheme_clusters(text))

def main():
    corpus_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus")
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(out_dir, exist_ok=True)
    
    langs = ['eng', 'hin', 'kan', 'tam']
    tokenizers = {
        'gpt2': lambda: tiktoken.get_encoding('gpt2'),
        'xlm-roberta-base': lambda: AutoTokenizer.from_pretrained('xlm-roberta-base')
    }
    
    # Store results: results[tok_name][lang] = stats_dict
    all_results = {}
    
    # First, load the data to avoid redundant IO
    corpus_data = {}
    for lang in langs:
        filepath = os.path.join(corpus_dir, f"{lang}.txt")
        with open(filepath, 'r', encoding='utf-8') as f:
            corpus_data[lang] = [l.strip() for l in f if l.strip()]
            
    # Process
    for tok_name, get_tok in tokenizers.items():
        print(f"Processing tokenizer: {tok_name}...")
        enc = get_tok()
        is_hf = hasattr(enc, 'add_special_tokens')
        
        all_results[tok_name] = {}
        for lang in langs:
            lines = corpus_data[lang]
            total_toks = 0
            total_words = 0
            total_cps = 0
            total_graphemes = 0
            total_bytes = 0
            
            sent_toks = []
            
            for line in lines:
                if is_hf:
                    toks = len(enc.encode(line, add_special_tokens=False))
                else:
                    toks = len(enc.encode(line))
                    
                sent_toks.append(toks)
                total_toks += toks
                total_words += len(line.split())
                total_cps += len(line)
                total_graphemes += count_graphemes(line)
                total_bytes += len(line.encode('utf-8'))
                
            all_results[tok_name][lang] = {
                'sentences': len(lines),
                'total_tokens': total_toks,
                'mean_toks_per_sent': statistics.mean(sent_toks),
                'median_toks_per_sent': statistics.median(sent_toks),
                'stdev_toks_per_sent': statistics.stdev(sent_toks) if len(sent_toks) > 1 else 0,
                'total_words': total_words,
                'tokens_per_word': total_toks / total_words,
                'total_codepoints': total_cps,
                'tokens_per_codepoint': total_toks / total_cps,
                'total_graphemes': total_graphemes,
                'tokens_per_grapheme': total_toks / total_graphemes,
                'total_bytes': total_bytes,
                'tokens_per_byte': total_toks / total_bytes,
                'sentence_tokens_list': sent_toks  # For paired ratio calculation
            }

    # Generate CSV
    csv_path = os.path.join(out_dir, "a3_comparison.csv")
    md_path = os.path.join(out_dir, "a3_comparison.md")
    
    headers = [
        "Tokenizer", "Language", "Sentences", "Total_Tokens", "Mean_Toks_Sent", 
        "Median_Toks_Sent", "StDev_Toks_Sent", "Total_Words", "Toks_Per_Word", 
        "Total_Codepoints", "Toks_Per_Codepoint", "Total_Graphemes", "Toks_Per_Grapheme", 
        "Total_Bytes", "Toks_Per_Byte", "Ratio_Total_Tokens_vs_Eng", 
        "Ratio_Toks_Per_Word_vs_Eng", "Mean_Sentence_Ratio_vs_Eng", "StDev_Sentence_Ratio_vs_Eng"
    ]
    
    md_lines = ["# A3 Consolidated Tokenization Results\n"]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.writer(csvf)
        writer.writerow(headers)
        
        for tok_name in tokenizers.keys():
            md_lines.append(f"## Tokenizer: {tok_name}\n")
            
            eng_stats = all_results[tok_name]['eng']
            
            for lang in langs:
                stats = all_results[tok_name][lang]
                
                # Ratios
                ratio_tot = stats['total_tokens'] / eng_stats['total_tokens']
                ratio_tpw = stats['tokens_per_word'] / eng_stats['tokens_per_word']
                
                if lang == 'eng':
                    mean_sent_ratio = 1.0
                    stdev_sent_ratio = 0.0
                else:
                    ratios = [t / max(1, e) for t, e in zip(stats['sentence_tokens_list'], eng_stats['sentence_tokens_list'])]
                    mean_sent_ratio = statistics.mean(ratios)
                    stdev_sent_ratio = statistics.stdev(ratios)
                    
                row = [
                    tok_name, lang, stats['sentences'], stats['total_tokens'], 
                    round(stats['mean_toks_per_sent'], 2), round(stats['median_toks_per_sent'], 2), 
                    round(stats['stdev_toks_per_sent'], 2), stats['total_words'], 
                    round(stats['tokens_per_word'], 2), stats['total_codepoints'], 
                    round(stats['tokens_per_codepoint'], 3), stats['total_graphemes'], 
                    round(stats['tokens_per_grapheme'], 3), stats['total_bytes'], 
                    round(stats['tokens_per_byte'], 3), round(ratio_tot, 2), 
                    round(ratio_tpw, 2), round(mean_sent_ratio, 2), round(stdev_sent_ratio, 2)
                ]
                writer.writerow(row)
                
                md_lines.append(f"### {lang.upper()}")
                md_lines.append(f"- **Total Tokens**: {stats['total_tokens']} (Aggregate Ratio vs Eng: {ratio_tot:.2f}x)")
                md_lines.append(f"- **Tokens / Sentence**: {stats['mean_toks_per_sent']:.2f}")
                md_lines.append(f"  - *Sentence-Level Ratios vs Eng*: Mean = {mean_sent_ratio:.2f}x, StDev = {stdev_sent_ratio:.2f}x")
                md_lines.append(f"- **Tokens / Word**: {stats['tokens_per_word']:.2f} (Ratio vs Eng: {ratio_tpw:.2f}x)")
                md_lines.append(f"- **Tokens / Codepoint**: {stats['tokens_per_codepoint']:.3f}")
                md_lines.append(f"- **Tokens / Grapheme**: {stats['tokens_per_grapheme']:.3f}")
                md_lines.append(f"- **Tokens / Byte**: {stats['tokens_per_byte']:.3f}")
                md_lines.append("")
                
    with open(md_path, 'w', encoding='utf-8') as mdf:
        mdf.write("\n".join(md_lines))
        
    print(f"Results written to {csv_path} and {md_path}")

if __name__ == "__main__":
    main()
