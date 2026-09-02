# AI Usage

## Tools
The following AI tools and models were used during the completion of this assignment:
- Primary AI Assistant (Agentic Coding Framework) utilizing large language models.
- Python ecosystem standard tooling, integrated with AI execution.

## How AI Was Used
- **Planning and Decomposition:** Structured the multi-part investigation into discrete, hypothesis-driven steps (Parts A, B, and C).
- **Code/Script Assistance:** Drafted and refined Python scripts for data processing, tokenization (`evaluate_a3.py`, `generate_a3_results.py`), and mathematical derivations for memory and throughput (`capacity_math.py`, `parse_bench.py`, `infer_throughput_definition.py`).
- **Experiment Design:** Designed A/B controlled experiments to isolate metric flaws (e.g. tokenizer ratios vs word count denominators) and debug capacity anomalies (identifying KV-cache saturation).
- **Analysis/Documentation:** Assisted in writing memos (`A4_memo.md`, `memo.md`) and generating markdown artifacts summarizing findings (`B1_capacity.md`, `B2_anomaly.md`, `decision_analysis.md`).
- **Adversarial Review:** Conducted hostile auditing passes to strictly separate empirical measurements from inference, aggressively removing unverified absolute claims.

## Human Verification
Repository execution, numerical checks, experiment outputs, and final decisions were reviewed by the author. No independent external verification process (beyond the stated constraints and local reproducibility checks) is claimed. 

## Evidence Integrity
Measured claims in this submission are tied directly to executable experiments or explicit mathematical derivations. Unsupported claims, estimates, and hypotheses are explicitly labeled as ASSUMPTION, INFERENCE, or PREDICTION across the repository. No experimental data or metrics were fabricated.
