# Recommendation Memo: Cross-Language Capacity Planning Audit

**To:** Leadership, Capacity & Routing Team  
**From:** Auditing Team  
**Date:** 2026-09-01  

---

## 1. CORRECTED HEADLINE NUMBERS

The original capacity report falsely claimed that routing Indic language traffic (particularly Kannada and Tamil) would consume up to ~20x the token capacity of English traffic. Our audit reveals this was driven by an inappropriate denominator (`tokens/word`) applied to morphologically rich languages, exacerbated by an English-centric legacy tokenizer (`gpt2`). 

By holding semantic meaning constant (using a parallel sentence corpus) and measuring with a multilingual tokenizer used in this evaluation (`xlm-roberta-base`), the measured denominator/tokenizer change reduces the observed token-workload disparity by roughly an order of magnitude.

**Observed Token-Workload Multipliers (Relative to English)**
*Measured on a 1,012-sentence parallel evaluation corpus:*

| Language | Original Report<br>(GPT-2, tok/word) | Corrected Denominator<br>(GPT-2, tok/sentence) | **Corrected Tokenizer**<br>**(XLM-R, tok/sentence)** |
|:---|:---|:---|:---|
| **Hindi** | 6.34x | 7.42x | **1.25x** |
| **Kannada** | 18.48x | 13.58x | **1.35x** |
| **Tamil** | 20.28x | 15.54x | **1.35x** |

*Evidence Traceability: Numbers directly extracted from A3 tokenization experiments (`partA/results/a3_comparison.md`), using `gpt2` and `xlm-roberta-base` tokenizers. The A2 tokenization and word-count issues were corrected before computing these ratios (`split(" ")` affected the word denominator; `.lower()` affected GPT-2 token counts).*

---

## 2. ROUTING RECOMMENDATION

**Do not penalize or throttle Indic languages based on the original 20x cost estimate.** 

To accurately model cross-language serving capacity, we recommend two immediate operational changes:
1. **Change the Planning Metric**: Immediately abandon `tokens/word` for cross-language cost modeling. Agglutinative languages like Tamil pack vast amounts of meaning into single, long words; dividing massive token counts by artificially small word counts distorts reality. Capacity models must shift to meaning-equivalent proxies (e.g., average tokens per request/prompt).
2. **Update Tokenizer Capacity Assumptions**: Ensure that routing cost models are strictly calibrated against the actual tokenizers used in production. On this evaluation corpus, GPT-2 shows an observed ~15.5x Tamil-to-English token-workload multiplier. On this evaluation corpus, XLM-R reduces the observed Tamil-to-English token-workload multiplier to ~1.35x. 

---

## 3. BIGGEST CAVEAT

**These multipliers do not constitute a universal production-capacity law.** 

The ~1.35x token workload multiplier for Kannada and Tamil was observed on a static, formal, strictly parallel Wikipedia corpus holding semantic meaning perfectly constant. Real production traffic is highly dynamic. Actual deployment traffic will feature drastically different request lengths, casual registers, domain shifts, and system prompt distributions across different markets. While 1.35x is the most defensible baseline for *equivalent content*, live user behavior in different locales may naturally result in longer or shorter average queries.

---

## 4. PRODUCTION MONITORING METRIC

**Metric to Monitor:** `Average Input Tokens per Request (Segmented by Language)`

**Why:** Because we cannot compute "parallel sentences" on live, organic user traffic, we must measure the actual token payload users are sending. 
**Actionable Signal:** By monitoring `Total Prompt Tokens / Total Requests` for each language tag in the serving logs, leadership can observe the true operational token workload. If Tamil requests average 35% more tokens than English requests, this is consistent with our baseline audit model. If the gap diverges significantly from ~1.35x, it indicates that user behavior (query length/complexity) differs across locales, triggering an automated update to the capacity provisioning assumptions.
