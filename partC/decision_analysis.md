# Part C — Decision Analysis: Casual Output Formatting

## 1. Constraints & Labeled Claims

**FACTS FROM ASSIGNMENT:**
- **Compute**: One A100-80GB GPU.
- **Time**: 2 weeks engineering/training window. Launch review in 3 weeks.
- **Reviewer Capacity**: Native speaker covering ONLY Hindi and Kannada. 10 hours/week.
- **External Budget**: $0 (No external APIs for synthetic data or evaluation).
- **Target Languages**: Hindi, Kannada, Tamil, Telugu, Bengali, Marathi.

**ASSUMPTIONS:**
- **Reviewer Speed**: The primary planning assumption is that a native speaker can read and evaluate a bilingual response pair in exactly 1 minute.
- **Base Model Capability**: Generating synthetic data zero-shot across 6 languages via the 4B model yields noisy outputs that require human review before serving as a safe training signal.

## 2. Back-of-the-Envelope Arithmetic (Reviewer Capacity)

The native reviewer is available for 10 hours/week. Over the 2-week engineering window, this totals 20 hours (1,200 minutes).

### Sensitivity Analysis (Reviewer Load)
Because reviewer speed is an assumption, we perform sensitivity analysis to determine maximum validated dataset sizes:
- **At 0.5 min/pair (Fast)**: 2,400 reviewed pairs total (1,200 Hindi / 1,200 Kannada).
- **At 1.0 min/pair (Baseline)**: 1,200 reviewed pairs total (600 Hindi / 600 Kannada).
- **At 2.0 min/pair (Thorough)**: 600 reviewed pairs total (300 Hindi / 300 Kannada).

**INFERENCE**: Even under the most optimistic assumption (2,400 pairs), the human bandwidth is exhausted exclusively on Hindi and Kannada. No human-validated data can be created for Tamil, Telugu, Bengali, or Marathi within the 2-week window.

## 3. Option Comparison & Evaluation

### Option A: SFT on synthetic casualized response pairs
- **FACT**: Reviewer capacity permits at most ~1,200 reviewed pairs under the stated 1 min/pair planning assumption.
- **FACT**: Only Hindi and Kannada have native-speaker review coverage.
- **INFERENCE**: Option A therefore cannot obtain equivalent human validation across all six target languages within the two-week window.
- **PREDICTION/RISK**: Training an intervention using unvalidated synthetic data for the other four languages introduces materially higher validation and regression risk.
- **Can we evaluate six languages with only Hindi/Kannada native review?** No.
- **What is the launch-review risk?** High, due to unvalidated synthetic data.

### Option B: Small <=1B inference-time rewriter
- **FACT & INFERENCE**: Faces the identical data-starvation constraints as Option A.
- **What new serving complexity does it introduce?** A sequential rewriter introduces additional inference latency and requires managing a secondary serving pipeline.
- **What is the latency risk?** (PREDICTION) Because generation must wait for the main model to finish before the rewriter begins, sequential latency increases. The exact latency penalty must be benchmarked before launch.

### Option C: Prompt Engineering Only
- **Can prompting create a measurable style shift quickly?** (PREDICTION) It relies entirely on the base 4B model's zero-shot adherence, which must be tested immediately via a Day-1 experiment.
- **How reversible is it?** Highly reversible. Prompt engineering does not modify model weights, so failures can be rolled back immediately without managing separate deployment artifacts.
- **How do we validate semantic preservation?** We dedicate the entire 20-hour human review budget to A/B testing outputs rather than cleaning training data.
- **What happens for the 4 unreviewed languages?** Prompt adherence in the four unreviewed languages is uncertain and must be treated as a launch risk; automated checks and rollback are required because native-speaker validation is unavailable.

**DECISION**: Option C has the strongest expected launch confidence. Options A and B are not preferred under the stated constraints because they demand human-validated data that mathematically exceeds the 20-hour capacity constraint, and they carry much higher operational risk for the four unreviewed languages.

## 4. Success Threshold & Kill Criterion Rationale

**Success Threshold (DECISION THRESHOLD — MANAGEMENT ASSUMPTION):**
*>= 20 percentage points absolute casualness win-rate, with <= 5% semantic error rate.*
- **Casualness Preference Win-Rate**: *(number of evaluation pairs where the casual-prompt response is preferred for casualness) / (number of non-tied evaluation pairs)*. Ties are excluded from the denominator.
- **Semantic Error Rate**: *(number of evaluated responses containing a reviewer-identified semantic/factual error) / (total evaluated responses)*.
We select 20% and 5% as management planning assumptions; they represent operational GO/NO-GO planning gates rather than scientifically established safety boundaries.

**Kill Criterion:**
*Kill if Week-1 Day-1 experiment yields < 10% casualness win-rate or > 5% semantic regression.*
This is an early management gate, not a statistical significance threshold. If the 4B model shows weak (<10%) steering in Week 1, killing it leaves time to pivot or delay the launch, distinguishing a dead-end approach from one showing promise.

## 5. Multilingual Risk Strategy

Native-speaker validation is available only for Hindi and Kannada. For the remaining four languages (Tamil, Telugu, Bengali, Marathi), the launch decision must rely on automated/weak evaluation and rollback safeguards. Prompt-only deployment is reversible and does not modify model weights, reducing the blast radius of style failures compared to serving an SFT model whose weights have been explicitly shifted by unreviewed data.
