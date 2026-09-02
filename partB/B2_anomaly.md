## 1. The Anomaly in the Benchmark Data

**MEASURED OBSERVATIONS:**
- **Batch 24**: `kv_cache_util` = 0.93, `preempted_seqs` = 0, `reported_tok_s` = 1607.4
- **Batch 32**: `kv_cache_util` = 0.97, `preempted_seqs` = 7, `reported_tok_s` = 1384.0
- **Batch 48**: `kv_cache_util` = 0.97, `preempted_seqs` = 23, `reported_tok_s` = 1298.5

**INFERENCE:**
Increasing batch size beyond the memory boundary is associated with increased preemption and declining throughput.

### Candidate A: Compute Bound / Batch Size Overhead
- **Hypothesis**: The GPU compute is simply saturated, and larger batches introduce scheduling or matrix-multiplication overhead that reduces efficiency.
- **Evidence / Short-Prompt Control**: The short-prompt sweep (`prompt_len = 512`) explicitly serves as a control experiment. In that sweep, batch size was scaled up to 64, throughput successfully reached 2267.3 tok/s, `preempted_seqs` remained at 0, and `kv_cache_util` stayed substantially below the long-context boundary (peaking at 0.47). 
- **Counter-evidence Conclusion**: This is evidence that batch-size increase alone does not explain the long-context collapse. The compute/scheduler can handle large batches natively.

### Candidate B: KV Cache Saturation & Scheduler Preemption (Strongest Supported Explanation)
- **Mechanism Hypothesis**: KV-cache pressure forces scheduler preemption, which is the most plausible explanation for the observed throughput degradation.
- **Evidence**: 
  1. **Mathematical Boundary**: 
     - L4 Usable Memory: $24 \text{ GB} \times 0.92 = 22.08 \text{ GB}$.
     - Weights & Overhead: $8.4 \text{ GB} + 1.6 \text{ GB} = 10.0 \text{ GB}$.
     - Available KV Cache = **$12.08 \text{ GB}$**.
     - Max sequence memory (`prompt + gen = 4096`): $4096 \times 114,688 = 469,762,048 \text{ bytes} \approx 0.47 \text{ GB}$.
     - Max concurrent sequences fitting in KV cache: $12.08 / 0.47 \approx \mathbf{25.7 \text{ sequences}}$.
  2. **Corroborating Metrics**: At batch 24, `kv_cache_util` is safely at 0.93. At batch 32 and 48, it hits a hard ceiling at 0.97. The `preempted_seqs` counter spikes exactly when throughput drops.
- **Conclusion**: At the estimated KV-cache budget, 32 or 48 simultaneous 4096-token sequences cannot all remain resident at once; the scheduler therefore has to manage memory pressure through preemption/queueing. This strongly supports KV saturation as the mechanism for the collapse. 

## 3. Recommended Configuration Change

**Proposed Prediction / Configuration**: Cap the maximum concurrent sequences by setting `--max-num-seqs 24` (or 25) in the vLLM serving configuration.

**Why it should help**: It should eliminate or reduce preemption caused by exceeding the KV-cache resident-sequence boundary. The scheduler will refuse to admit more than 24-25 requests simultaneously, leaving excess requests in the pending queue.

**Expected Effect**: 
- `preempted_seqs` will drop strictly to 0.
- `kv_cache_util` will plateau at safe levels (~0.93).
- (Prediction): Because preemption is eliminated, generation goodput will stabilize, preventing the performance collapse seen at batch 32 and 48. Exact production goodput must be benchmarked after the configuration change.

**Trade-off**: 
This trades throughput opportunity for queueing/latency behavior. Time-To-First-Token (TTFT) for the 26th request in a burst will increase, as it must wait in the queue for a previous request to complete.
