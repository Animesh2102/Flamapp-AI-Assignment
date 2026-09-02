#!/usr/bin/env python3
import tiktoken
from transformers import AutoTokenizer
from uniseg.graphemecluster import grapheme_clusters
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    text = "नमस्ते दुनिया"  # Namaste duniya
    print(f"Text: '{text}'")
    
    # 1. Denominators
    words = len(text.split())
    codepoints = len(text)
    graphemes = sum(1 for _ in grapheme_clusters(text))
    bytes_count = len(text.encode('utf-8'))
    
    print(f"Words (split): {words}")
    print(f"Codepoints (len): {codepoints}")
    print(f"Graphemes: {graphemes}")
    print(f"Bytes (utf-8): {bytes_count}")
    
    # 2. Tokenizers
    enc_gpt2 = tiktoken.get_encoding("gpt2")
    tokens_gpt2 = enc_gpt2.encode(text)
    print(f"GPT-2 tokens: {len(tokens_gpt2)} -> {tokens_gpt2}")
    
    enc_xlmr = AutoTokenizer.from_pretrained("xlm-roberta-base")
    tokens_xlmr = enc_xlmr.encode(text, add_special_tokens=False)
    print(f"XLM-R tokens: {len(tokens_xlmr)} -> {tokens_xlmr}")

if __name__ == "__main__":
    main()
