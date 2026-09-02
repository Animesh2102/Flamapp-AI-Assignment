# B3 — Correction of REPORT_v0.md

## 1. Misleading Claim 1: "Longer prompts clearly give better GPU utilization."
**What REPORT_v0.md says:**
"at batch 16, long prompts hit **1311 tok/s** vs only **883 tok/s** for short prompts. Longer prompts clearly give better GPU utilization."

**Why the interpretation is wrong:**
The benchmark's `reported_tok_s` is a total-token throughput metric that credits both prompt/prefill tokens and generated/decode tokens. The error in `REPORT_v0.md` is interpreting this quantity as generation throughput/goodput. By mathematically reverse-engineering the harness (EXP-B3-001), we verified that it empirically matches:
$$ \text{reported\_tok\_s} = \frac{\text{batch\_size} \times (\text{prompt\_tokens} + \text{generated\_tokens})}{\text{wall\_clock\_seconds}} $$
This metric conflates fast prefill with slow decode. Long prompts artificially inflate this value because it instantly credits thousands of prefill tokens (3584 per request) over the same wall-clock period.

**What the data actually supports (REPORT VALUE ≠ GENERATION GOODPUT):**
If we calculate the *generation goodput* (generated tokens / wall-clock time):
- **Batch 16 Short Prompt (512 prompt + 256 gen):** $16 \times 256 / 13.91\text{s} \approx \mathbf{294.5 \text{ generated tok/s}}$.
- **Batch 16 Long Prompt (3584 prompt + 512 gen):** $16 \times 512 / 49.97\text{s} \approx \mathbf{163.9 \text{ generated tok/s}}$.

The true generation goodput is vastly *worse* for long prompts. The original conclusion is therefore unsupported and reversed when evaluated using the appropriate generation-throughput measure.

---

## 2. Misleading Claim 2: "scale linearly with batch size, so batch 48 should give us ~3200 tok/s"
**What REPORT_v0.md says:**
"For capacity planning, assume ~1600 tok/s per L4 (best observed) and scale linearly with batch size, so batch 48 should give us ~3200 tok/s."

**Why the interpretation is wrong:**
Linear extrapolation from the batch-24 peak is invalid for this long-context workload because the system encounters a memory/scheduler regime change. 
1. The observed metric does not represent generation goodput.
2. Long-context throughput does not scale linearly after the KV-cache boundary.
3. The actual batch-48 row (recorded at 1298.5 `reported_tok_s`) is already worse than batch 24.
4. Preemptions increase sharply at batch 32 and 48, completely destroying performance scaling.

---

## 3. Honest Goodput Derivation (Batch 24, Long Prompt)
For the peak long-prompt row (batch 24, prompt_len 3584, gen_len 512, wall_clock 61.16s, reported 1607.4 tok/s):

**Method 1: Direct from raw counts**
$$ \text{Generation Goodput} = \frac{\text{batch\_size} \times \text{gen\_len}}{\text{wall\_clock\_s}} $$
$$ \text{Generation Goodput} = \frac{24 \times 512}{61.16} \approx \mathbf{200.92 \text{ tok/s}} $$

**Method 2: Reconstructed from the reported metric definition**
Since `reported_tok_s` = $\text{batch} \times (\text{prompt} + \text{gen}) / \text{wall}$, we can isolate generation tokens by scaling the reported metric by the fraction of tokens that were actually generated:
$$ \text{Generation Goodput} = \text{reported\_tok\_s} \times \left( \frac{\text{gen\_len}}{\text{prompt\_len} + \text{gen\_len}} \right) $$
$$ \text{Generation Goodput} = 1607.4 \times \left( \frac{512}{3584 + 512} \right) $$
$$ \text{Generation Goodput} = 1607.4 \times \frac{512}{4096} = 1607.4 \times \frac{1}{8} \approx \mathbf{200.93 \text{ tok/s}} $$

Both independent methods reconcile to ~200.9 tok/s (they agree within rounding due to the decimal precision of `reported_tok_s`). The claimed "1600 tok/s" conflates input processing with generation output.
