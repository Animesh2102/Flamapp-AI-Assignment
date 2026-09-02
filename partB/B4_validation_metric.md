# B4 — Serving-Stack Validation Metric

## Selected Metric
**Exact metric name**: `preempted_seqs` 
*(Production telemetry equivalent: `vllm:num_preemptions` or `vllm_scheduler_preempted_requests_total`)*

## What It Measures
It measures the cumulative number of times the serving scheduler (e.g., vLLM) forcibly pauses an active sequence and evicts its KV cache to make room for other requests due to memory exhaustion. These sequences must be queued and their prompts potentially recomputed later.

## Why It Validates B2
The B2 mechanism proposed that throughput collapses strictly because the KV-cache budget is exceeded, forcing the scheduler to thrash, rather than due to compute-bound batch overhead. `preempted_seqs` is highly diagnostic because it strictly isolates scheduler memory intervention. Unlike generic symptoms like GPU utilization or latency (which can degrade under normal compute saturation), for this workload and serving configuration, preemption appears when KV-cache pressure reaches the scheduler's memory boundary. If memory pressure is the true cause of the performance collapse, preemption is the necessary mechanical bridge.

## Evidence from Benchmark
The provided `bench_log.csv` establishes a strict numerical association between memory boundaries, preemption, and performance degradation during the long-context sweep (prompt 3584, gen 512):

- **Batch 24:** `kv_cache_util` = 0.93 | `preempted_seqs` = **0** | `reported_tok_s` = 1607.4
- **Batch 32:** `kv_cache_util` = 0.97 | `preempted_seqs` = **7** | `reported_tok_s` = 1384.0
- **Batch 48:** `kv_cache_util` = 0.97 | `preempted_seqs` = **23** | `reported_tok_s` = 1298.5

The benchmark demonstrates that throughput scales positively up to batch 24 while preemptions are 0. Throughput only degrades exactly when `preempted_seqs` > 0 (which occurs precisely when `kv_cache_util` pegs at its 0.97 hard limit).

## Expected Production Signature
If the B2 mechanism is correct, we expect the following chronological sequence in live production:
1. As concurrent long-context requests increase, KV-cache utilization will rise until it hits its configured upper bound (e.g., ~0.95–0.97).
2. Immediately following this saturation, the `preempted_seqs` counter will begin incrementing.
3. If KV-cache pressure is the dominant mechanism, we expect increasing preemptions to coincide with degradation in generation goodput and/or tail latency (e.g., e2e_ms_p95) severely spiking, confirming the recomputation/thrashing penalty.

## Falsification Condition
If production traffic exhibits severely degraded generation goodput and massive latency spikes, but the `preempted_seqs` counter remains at exactly zero (and `kv_cache_util` remains below the relevant ceiling), the KV-preemption hypothesis becomes less plausible and another bottleneck should be investigated. Such an observation would suggest that the bottleneck is ordinary compute saturation, network I/O, or a different architectural limit, rather than KV-cache scheduler thrashing.

## Operational Recommendation
Configure production alerting on `preempted_seqs > 0` rather than relying solely on latency SLIs. If preemptions are occurring continuously, the live system is actively thrashing its memory. To mitigate this, operators should decrease `max_num_seqs` (as predicted in B2) or scale out replicas to bring the system back into the stable, zero-preemption regime.
