# Part C — Decision Memo: Casual Output Formatting

## RECOMMENDATION
**Option C: Prompt Engineering Only**

## WHY
Option C is preferred under the stated constraints because it:
- requires no weight updates/training data,
- avoids adding a second inference stage,
- uses the limited reviewer budget for direct evaluation,
- is immediately reversible,
- provides the fastest empirical test of whether the base 4B model can achieve the desired style shift.

## ASSUMPTIONS
- **PLANNING ASSUMPTION**: A native speaker can evaluate a bilingual response pair (baseline vs. casual) in exactly 1 minute.
- **PLANNING ASSUMPTION**: Generating synthetic data via the 4B model yields noisy outputs that require human review before serving as a safe training signal.

## BACK-OF-THE-ENVELOPE
- **Reviewer Bandwidth**: 10 hours/week × 2 weeks = 20 total reviewer hours.
- **Capacity**: 20 hours = 1,200 minutes. At 1 minute per pair, maximum capacity is **1,200 reviewed pairs** total before launch review.

## SUCCESS METRIC & DEFINITIONS
**Primary Metric**: A/B Casualness Preference Win-Rate (guarded by Semantic Error Rate).

**Operational Definitions**:
- **Casualness Preference Win-Rate**: *(number of evaluation pairs where the casual-prompt response is preferred for casualness) / (number of non-tied evaluation pairs)*. Ties are excluded from the denominator.
- **Semantic Error Rate**: *(number of evaluated responses containing a reviewer-identified semantic/factual error) / (total evaluated responses)*.

**DECISION THRESHOLD — MANAGEMENT ASSUMPTION**: On a held-out final evaluation set of 100 prompts for Hindi and 100 prompts for Kannada (200 prompts total, generating 200 response pairs), the casual-prompted responses must achieve a **>= 20 percentage points** improvement in casualness preference over the baseline, while the semantic error rate must remain **<= 5%**. (These values are management decision thresholds designed to ensure the shift is large enough to matter while keeping regression bounded; they are not scientifically established safety boundaries).

## KILL CRITERION
**Week-1 Decision Gate**: Kill the prompt engineering approach if, by the end of Week 1, the Day-1 Experiment yields a casualness win-rate of **< 10%**, or produces a semantic error rate of **> 5%**. Explicitly, this is an early management gate, not a statistical significance threshold. This gate leaves sufficient time in Week 2 to pivot, distinguishing a model that fundamentally lacks zero-shot stylistic steerability from one showing promise.

## DAY-1 EXPERIMENT
**Prompt A/B Zero-Shot Pilot**: Generate 50 baseline responses and 50 casual-prompt responses per language for Hindi and Kannada (100 prompts/pairs total). Send these 100 pairs to the native reviewer immediately. At the assumed 1 minute/pair, this requires exactly **1.67 hours** of review time, efficiently utilizing the Week 1 budget to answer the highest-value unknown: can the base 4B model adopt a casual style via prompting alone?

## RISKS
**Multilingual Uncertainty**: Native-speaker validation is available only for Hindi and Kannada. For the remaining four languages (Tamil, Telugu, Bengali, Marathi), prompt adherence is uncertain and must be treated as a launch risk; automated checks and rollback are required because native-speaker validation is unavailable. Prompt-only deployment is reversible and does not modify model weights, reducing the blast radius of style failures compared to deploying an unvalidated SFT model.
