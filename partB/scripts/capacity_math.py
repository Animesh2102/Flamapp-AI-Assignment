#!/usr/bin/env python3

def main():
    # 1. Model specs from bench/model_spec.md
    layers = 28
    kv_heads = 8
    head_dim = 128
    bytes_per_param = 2  # fp16
    kv_factor = 2        # Key and Value
    
    # 2. Compute KV cache bytes per token
    # Formula: 2 (K,V) * bytes_per_param * layers * kv_heads * head_dim
    bytes_per_token = kv_factor * bytes_per_param * layers * kv_heads * head_dim
    print(f"--- B1 KV Cache Arithmetic ---")
    print(f"Bytes per token: {bytes_per_token} bytes")
    
    # 3. Compute KV cache MiB per sequence (4096 tokens)
    seq_len = 4096
    bytes_per_seq = bytes_per_token * seq_len
    mib_per_seq = bytes_per_seq / (1024 ** 2)
    print(f"Bytes per max sequence (4096 tokens): {bytes_per_seq} bytes")
    print(f"MiB per max sequence (4096 tokens): {mib_per_seq:.2f} MiB")
    
    # 4. A100-80GB Memory Budget Estimation
    # Assume A100-80GB = 80 GiB of VRAM
    total_gpu_memory_bytes = 80 * (1024 ** 3)
    gpu_memory_utilization = 0.92
    
    # Usable memory by vLLM (before overhead/weights)
    usable_memory_bytes = total_gpu_memory_bytes * gpu_memory_utilization
    
    # Model Weights (4.2 B params in fp16)
    # Typically 1B params = 10^9 parameters.
    params = 4.2 * (10**9)
    weights_bytes = params * bytes_per_param
    
    # Non-KV Overhead (given as ~1.6 GB)
    # We will assume GB = 10^9 bytes for weights and overhead, or GiB.
    # Let's use 1.6 * 1024**3 for safety, or 1.6 * 10**9. 
    # Usually "1.6 GB" means 1.6 * 1024**3 in CUDA contexts (GiB).
    overhead_bytes = 1.6 * (1024 ** 3)
    
    # Available for KV cache
    available_kv_bytes = usable_memory_bytes - weights_bytes - overhead_bytes
    
    # Max sequences
    max_seqs_theoretical = int(available_kv_bytes // bytes_per_seq)
    
    print(f"\n--- Concurrency on A100-80GB ---")
    print(f"Total GPU Memory: 80 GiB = {total_gpu_memory_bytes / 1024**3:.2f} GiB")
    print(f"Usable Memory (0.92 util): {usable_memory_bytes / 1024**3:.2f} GiB")
    print(f"Weights Memory (4.2B fp16): {weights_bytes / 1024**3:.2f} GiB")
    print(f"Overhead Memory (1.6 GB): {overhead_bytes / 1024**3:.2f} GiB")
    print(f"Available for KV Cache: {available_kv_bytes / 1024**3:.2f} GiB")
    print(f"Theoretical Max 4096-token Sequences: {max_seqs_theoretical}")

if __name__ == "__main__":
    main()
