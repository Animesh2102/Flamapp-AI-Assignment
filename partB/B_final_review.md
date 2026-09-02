# Part B Final Review: Capacity Reconciliation

## B1: KV Cache Arithmetic
- **KV bytes/token**: 114,688 bytes
- **4096-token sequence memory**: ~448.00 MiB (469,762,048 bytes)
- **A100-80GB theoretical concurrency**: 146 sequences
- **Evidence file/script**: `partB/scripts/capacity_math.py`, `partB/B1_capacity.md` (derived exactly from `model_spec.md`).
- **Confidence level**: High (Exact Arithmetic)
- **Important caveat**: This represents a strict theoretical upper bound assuming 100% packing efficiency of the KV cache allocator without fragmentation.

## B2: Long-Context Throughput Anomaly
- **Long-context anomaly**: At `prompt_len = 3584`, throughput collapses from a peak of 1607.4 tok/s at batch 24, down to 1298.5 tok/s at batch 48.
- **Strongest supported mechanism**: KV-cache pressure forces scheduler preemption. The 24GB L4 GPU mathematically cannot fit 32 concurrent max-length sequences. When the boundary is breached, vLLM hits its 0.97 KV cache utilization ceiling and triggers preemptions/thrashing, tanking performance.
- **Selected configuration change (Prediction)**: Cap `--max-num-seqs` to 24 (or 25) to enforce the memory boundary at the scheduler level.
- **Evidence file/script**: `partB/scripts/parse_bench.py`, `partB/B2_anomaly.md`.
- **Confidence level**: High (Exact Arithmetic / Corroborating Metrics)
- **Important caveat**: This configuration change forces queueing; time-to-first-token (TTFT) will increase for requests forced to wait in the queue, trading latency for sustained generation goodput.

## B3: Benchmark Audit & Report Correction
- **Meaning of `reported_tok_s`**: It is a total-token throughput metric corresponding to `batch_size × (prompt_tokens + generated_tokens) / wall_clock_seconds`.
- **Generation goodput (Batch 24, long prompt)**: ~200.9 tok/s of actual generated tokens (NOT 1607 tok/s).
- **Corrected interpretation of `REPORT_v0.md`**: `REPORT_v0.md` fundamentally misinterpreted the metric as generation goodput. Because the metric instantly credits massive prefill inputs, it falsely made long prompts appear faster. In reality, evaluated on true generation goodput, short prompts (294.5 tok/s) vastly outperform long prompts (163.9 tok/s). Linear extrapolation to batch 48 is also invalid due to the KV-cache regime change.
- **Evidence file/script**: `partB/scripts/infer_throughput_definition.py`, `partB/report_correction.md`.
- **Confidence level**: High (0.00% residual error in metric reverse-engineering)
- **Important caveat**: Goodput and TTFT must be evaluated together in production; while goodput is low for long contexts, batching still offers some systemic scaling up to the memory boundary.

## B4: Serving-Stack Validation Metric
- **Selected diagnostic serving metric**: `preempted_seqs` (vLLM scheduler preemptions, or `vllm_scheduler_preempted_requests_total`).
- **Evidence file/script**: `partB/B4_validation_metric.md`.
- **Confidence level**: High
- **Important caveat**: The CSV log measures the count of preemptions but does not directly measure the resulting recompute cycles (compute overhead) invoked by those preemptions.
