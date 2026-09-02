# B1 — KV Cache Arithmetic & Capacity Estimation

## 1. Exact KV-Cache Bytes / Token

According to `model_spec.md` for FLM-4B-Instruct (dense):
- **Layers ($L$)**: 28
- **KV heads ($H_{kv}$)**: 8
- **Head dimension ($D_{head}$)**: 128
- **Precision**: fp16 (2 bytes per parameter)
- **K/V Factor**: 2 (since we store both Key and Value tensors)

The exact formula for the KV cache size of a single token is:
$$ \text{Bytes/Token} = (\text{K/V factor}) \times (\text{Bytes/Param}) \times L \times H_{kv} \times D_{head} $$

**Substitution:**
$$ \text{Bytes/Token} = 2 \times 2 \times 28 \times 8 \times 128 $$
$$ \text{Bytes/Token} = 114,688 \text{ bytes} $$

---

## 2. Maximum Concurrent Sequences Estimation (A100-80GB)

We want to estimate the theoretical maximum number of concurrent 4096-token sequences that can fit on one NVIDIA A100-80GB GPU. 

**Memory per max sequence:**
- 4,096 tokens × 114,688 bytes/token = **469,762,048 bytes** per sequence (Exactly **448.00 MiB**).

**Memory Budget Assumptions:**
- **GPU Capacity**: We assume the A100-80GB provides exactly 80 GiB ($80 \times 1024^3 = 85,899,345,920$ bytes) of VRAM.
- **Reserved/Runtime Memory**: Based on `model_spec.md`, `gpu_memory_utilization` is 0.92. This limits the usable memory for weights + KV cache + overhead to **73.6 GiB** ($79,026,012,160$ bytes). 
- **Model Weights**: `model_spec.md` specifies 4.2 B parameters in fp16. Assuming 1 billion = $10^9$, the serialized weight memory is exactly $4.2 \times 10^9 \times 2 \text{ bytes} = 8,400,000,000 \text{ bytes}$ (approx. **7.82 GiB**).
- **Non-KV Overhead**: `model_spec.md` states to assume ~1.6 GB overhead. Because CUDA runtime allocations are typically evaluated in powers of two, we explicitly assume this means **1.6 GiB** ($1.6 \times 1024^3 = 1,717,986,918$ bytes).

**Available KV Cache Memory:**
$$ \text{Available} = \text{Total Usable} - \text{Weights} - \text{Overhead} $$
$$ \text{Available} = 79,026,012,160 - 8,400,000,000 - 1,717,986,918 = \mathbf{68,908,025,242 \text{ bytes}} $$

**Theoretical Max Sequences:**
$$ \text{Max Sequences} = \lfloor \text{Available Bytes} / \text{Bytes per Max Sequence} \rfloor $$
$$ \text{Max Sequences} = \lfloor 68,908,025,242 / 469,762,048 \rfloor = \mathbf{146 \text{ sequences}} $$

**Practical Caveat:**
This is a strict theoretical upper bound assuming 100% packing efficiency of the KV cache allocator (like PagedAttention). In practice, memory fragmentation, varying prompt lengths, context switching, and slightly conservative memory reservation thresholds might limit concurrency below this exact theoretical ceiling.
