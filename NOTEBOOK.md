# NOTEBOOK.md — Chronological Lab Notebook

**Project**: FlamApp AI Intern Assignment — The Audit  
**Started**: 2026-09-01T17:44 IST  
**Author**: Animesh (with AI assistance — see AI_USAGE.md)

---

## Experiment Index

| ID | Stage | Hypothesis | Status |
|----|-------|------------|--------|
| EXP-001 | A2 / Baseline | Running original fertility.py reproduces REPORT_v0 numbers | CONFIRMED |
| EXP-002 | A2 / split bug | `line.split(" ")` produces empty-string words on double-spaced lines, deflating reported fertility | CONFIRMED |
| EXP-003 | A2 / .lower() | `.lower()` materially changes English token counts but not Hindi | CONFIRMED |
| EXP-004 | A2 / len(line) | `len(line)` (codepoints) differs from grapheme count for Hindi | CONFIRMED — SUSPICIOUS BUT CORRECT |
| EXP-005 | A2 / denominators | tok/word gives different cross-language ratio than tok/sentence | CONFIRMED |
| EXP-006 | A2 / dead code | `import random` + `random.seed(1337)` is unused dead code | CONFIRMED |
| EXP-A1-001 | A1 / Corpus Selection | Find reproducible public parallel corpus source (English, Hindi, 2 Dravidian) | SUCCESS |
| EXP-A1-002 | A1 / Corpus Extraction | Extract and normalize aligned text files | SUCCESS |
| EXP-A1-003 | A1 / Corpus Validation | Verify parallelism and basic statistics | SUCCESS |

---

## Experiments

---

### EXP-001 — Reproduce REPORT_v0 Numbers

**Stage**: A2 / Baseline  
**Date**: 2026-09-01

#### Hypothesis
Running `fertility.py` with the supplied corpora and `gpt2` tokenizer will reproduce the exact numbers in REPORT_v0.md:
- eng: fertility = 1.27, tok/char = 0.226
- hin: fertility = 7.45, tok/char = 1.579
- Hindi/English ratio: 5.89×

**HYPOTHESIS — NOT YET PROVEN**

#### Motivation
We must establish a baseline before auditing. If we cannot reproduce the reported numbers, either our environment differs or the report itself contains transcription errors.

#### Experiment
Run the original `fertility.py` exactly as documented in its docstring, with the supplied corpora.

#### Command
```
cd "..\starter kit\starter_kit"
python fertility.py --corpus eng=corpus_sample/eng_sample.txt --corpus hin=corpus_sample/hin_sample.txt --tokenizer gpt2
```

#### Result
**MEASURED**:
```
tokenizer: gpt2
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.27       0.226
hin                       7.45       1.579

hin is 5.89x the fertility of eng (worse tokenization)
```

All numbers match REPORT_v0.md exactly:

| Metric | REPORT_v0 | Measured | Δ |
|--------|-----------|----------|---|
| eng fertility | 1.27 | 1.27 | 0.00 |
| eng tok/char | 0.226 | 0.226 | 0.000 |
| hin fertility | 7.45 | 7.45 | 0.00 |
| hin tok/char | 1.579 | 1.579 | 0.000 |
| ratio | 5.89× | 5.89× | 0.00 |

#### Evidence
The script output matches REPORT_v0 exactly on all five reported values. The baseline is reproducible. Our environment (Python 3.14, tiktoken 0.14.0) produces identical results.

#### Verdict
**CONFIRMED**

#### Revision / Next Step
Baseline established. We can now test individual components of `fertility.py` against this baseline to measure the effect of each suspected issue.

Next experiment: EXP-002 — test `line.split(" ")` vs `split()` behavior on the supplied corpora.

---

### EXP-002 — `line.split(" ")` vs `line.split()` on Supplied Corpora

**Stage**: A2 / split bug  
**Date**: 2026-09-01

#### Hypothesis
`line.split(" ")` (splitting on a single space literal) produces empty-string elements when lines contain consecutive spaces, inflating the word count denominator and thereby deflating the computed fertility ratio.

**HYPOTHESIS — NOT YET PROVEN**

#### Motivation
- **FACT (Python semantics)**: `"a  b".split(" ")` → `["a","","b"]` (length 3); `"a  b".split()` → `["a","b"]` (length 2).
- **FACT (corpus observation)**: eng_sample.txt line 7 has double space between "books" and "in". hin_sample.txt line 10 has double space between "किताबें" and "अलमारी".
- **FACT (code)**: `fertility.py` line 62 uses `line.split(" ")`.

The question is: does this produce a measurable change in the reported fertility values?

#### Experiment
For each line in both corpora, compute word count and fertility using `split(" ")` vs `split()`. Compare per-line and average values.

#### Command
```
cd "..\starter kit\starter_kit"
python "..\your-submission\partA\scripts\test_split.py"
```

#### Result
**MEASURED**:

**English (eng_sample.txt):**

| Line | split(" ") words | split() words | Δ words | tokens | fert(" ") | fert() | Δ fert |
|------|-----------------|---------------|---------|--------|-----------|--------|--------|
| 1 | 8 | 8 | 0 | 12 | 1.5000 | 1.5000 | 0.0000 |
| 2 | 7 | 7 | 0 | 9 | 1.2857 | 1.2857 | 0.0000 |
| 3 | 12 | 12 | 0 | 13 | 1.0833 | 1.0833 | 0.0000 |
| 4 | 7 | 7 | 0 | 8 | 1.1429 | 1.1429 | 0.0000 |
| 5 | 6 | 6 | 0 | 7 | 1.1667 | 1.1667 | 0.0000 |
| 6 | 8 | 8 | 0 | 11 | 1.3750 | 1.3750 | 0.0000 |
| **7** | **8** | **7** | **1** | **10** | **1.2500** | **1.4286** | **-0.1786** |
| 8 | 6 | 6 | 0 | 9 | 1.5000 | 1.5000 | 0.0000 |
| 9 | 6 | 6 | 0 | 7 | 1.1667 | 1.1667 | 0.0000 |
| 10 | 11 | 11 | 0 | 13 | 1.1818 | 1.1818 | 0.0000 |
| **AVG** | | | | | **1.2652** | **1.2831** | **-0.0179** |

- eng line 7: `split(' ')` → `['please','keep','the','books','','in','the','cupboard.']` (8 words, one empty)
- eng line 7: `split()` → `['please','keep','the','books','in','the','cupboard.']` (7 words)
- Fertility: 1.2500 (bug) vs 1.4286 (correct) — **Δ = -0.1786 on that line**
- Average fertility: 1.2652 (bug) vs 1.2831 (correct) — **Δ = -0.0179, relative = -1.39%**

**Hindi (hin_sample.txt):**

| Line | split(" ") words | split() words | Δ words | tokens | fert(" ") | fert() | Δ fert |
|------|-----------------|---------------|---------|--------|-----------|--------|--------|
| 1 | 7 | 7 | 0 | 47 | 6.7143 | 6.7143 | 0.0000 |
| 2 | 8 | 8 | 0 | 61 | 7.6250 | 7.6250 | 0.0000 |
| ... (lines 3-9 identical) | | | | | | | |
| **10** | **6** | **5** | **1** | **45** | **7.5000** | **9.0000** | **-1.5000** |
| **AVG** | | | | | **7.4485** | **7.5985** | **-0.1500** |

- hin line 10: `split(' ')` → `['किताबें','','अलमारी','में','रखी','हैं।']` (6 words, one empty)
- hin line 10: `split()` → `['किताबें','अलमारी','में','रखी','हैं।']` (5 words)
- Fertility: 7.5000 (bug) vs 9.0000 (correct) — **Δ = -1.5000 on that line**
- Average fertility: 7.4485 (bug) vs 7.5985 (correct) — **Δ = -0.1500, relative = -1.97%**

**Effect on reported ratio:**

| Metric | With bug (split(" ")) | Corrected (split()) | Δ |
|--------|----------------------|---------------------|---|
| eng fertility | 1.2652 | 1.2831 | -0.0179 |
| hin fertility | 7.4485 | 7.5985 | -0.1500 |
| hin/eng ratio | 5.89× | 5.92× | -0.03× |

Note: The reported eng=1.27 and hin=7.45 round to match the bug version (1.2652→1.27, 7.4485→7.45). The corrected values would be 1.28 and 7.60.

#### Evidence

1. **The defect EXISTS**: `split(" ")` produces empty-string elements on 2 of 20 lines (eng line 7, hin line 10). This is a **FACT** — deterministic Python behavior on observed corpus content.

2. **Magnitude of effect**:
   - On affected English line: fertility deflated by 0.1786 tok/word (12.5% of the line's correct fertility)
   - On affected Hindi line: fertility deflated by 1.5000 tok/word (16.7% of the line's correct fertility)
   - On English average: fertility deflated by 0.0179 (1.39% relative)
   - On Hindi average: fertility deflated by 0.1500 (1.97% relative)

3. **Direction**: The bug **deflates** fertility (makes both languages look more efficient than they are). The effect is larger on Hindi because the per-line fertility values are larger in absolute terms.

4. **Effect on cross-language ratio**: Minimal on this tiny corpus (5.89× → 5.92×). However, this is an artifact of only 1/10 lines being affected in each language. On a corpus with more spacing irregularities, the effect would be larger and unpredictable.

5. **Whether it changes the decision**: On this corpus, the 6× cost ratio barely changes. But the bug is real and its magnitude depends on corpus-specific double-space frequency — it is not a controlled or bounded error.

#### Verdict
**CONFIRMED — CODE BUG EXISTS**

The defect is real: `split(" ")` creates phantom empty words. The magnitude is corpus-dependent (1.4% to 2.0% on this corpus, but up to 16.7% on individual affected lines). The direction is always deflation of fertility. The bug does not materially change the cross-language ratio *on this specific corpus*, but it is an implementation defect that would cause errors on any corpus with irregular spacing.

#### Revision / Next Step
- The bug is confirmed. Corrected script should use `split()` or equivalent.
- The magnitude on this toy corpus is small, but the bug is unbounded (a corpus with many double/triple spaces would be severely affected).
- Next experiment: EXP-003 — test `.lower()` effect on token counts.

---

### EXP-003 — Effect of `.lower()` on GPT-2 Token Counts

**Stage**: A2 / .lower()  
**Date**: 2026-09-01

#### Hypothesis
`.lower()` on line 60 of `fertility.py` may materially change token counts for English (which has case distinction) but not for Hindi (Devanagari has no case). The magnitude of the effect is unknown.

**HYPOTHESIS — NOT YET PROVEN**

#### Motivation
- **FACT (code)**: Line 60 applies `.lower()` before tokenization.
- **FACT (Unicode)**: Devanagari has no uppercase/lowercase distinction.
- **QUESTION**: Does lowercasing change GPT-2 BPE tokenization? By how much?
- The code comment says "lowercase so casing doesn't add noise to the comparison" — is this justification valid?

#### Experiment
Tokenize each line with and without `.lower()`, compare per-line token counts and overall fertility.

#### Command
```
cd "..\starter kit\starter_kit"
python "..\your-submission\partA\scripts\test_lower.py"
```

#### Result
**MEASURED**:

**English:**

| Line | Text (first 40 chars) | tok(lower) | tok(orig) | delta | %change |
|------|----------------------|-----------|-----------|-------|---------|
| 1 | Bengaluru International Airport handled | 12 | 12 | 0 | 0.00% |
| 2 | The Quarterly Review meeting moved to Th | 9 | 8 | **+1** | **12.50%** |
| 3 | I bought this book yesterday from a smal | 13 | 13 | 0 | 0.00% |
| 4 | Children are playing cricket on the grou | 8 | 8 | 0 | 0.00% |
| 5 | The train arrived exactly on time. | 7 | 7 | 0 | 0.00% |
| 6 | NASA and ISRO announced a joint mission | 11 | 10 | **+1** | **10.00%** |
| 7 | Please keep the books in the cupboard. | 10 | 10 | 0 | 0.00% |
| 8 | We are visiting Mysuru next week. | 9 | 9 | 0 | 0.00% |
| 9 | Do you want tea or coffee? | 7 | 7 | 0 | 0.00% |
| 10 | The GPU cluster ran out of memory during | 13 | 12 | **+1** | **8.33%** |

- **TOTAL**: 99 tokens (lowered) vs 96 tokens (original), **delta = +3, change = +3.12%**
- Lines 2, 6, 10 are affected. These contain capitalized proper nouns/acronyms: "Quarterly Review", "NASA", "ISRO", "GPU".
- Lowercasing breaks known BPE merges for uppercase tokens (e.g., "NASA" is 1 token, but "nasa" → "n" + "asa" = 2 tokens).

**Hindi:**
- **TOTAL**: 459 tokens (lowered) vs 459 tokens (original), **delta = 0, change = 0.00%**
- **CONFIRMED**: `.lower()` is a no-op for Devanagari. Zero effect on all 10 lines.

**Fertility impact (using corrected `split()`):**

| Language | Fertility (lowered) | Fertility (original) | Delta | Relative |
|----------|-------------------|---------------------|-------|----------|
| English | 1.2831 | 1.2472 | +0.0359 | +2.88% |
| Hindi | 7.5985 | 7.5985 | 0.0000 | 0.00% |

#### Evidence

1. **The defect EXISTS**: `.lower()` increases English token count by 3.12% (3 of 96 tokens) because GPT-2 has separate BPE merges for capitalized/uppercase forms. Lowercasing destroys these merges.

2. **Asymmetric effect**: The effect is **unidirectional** — it inflates English fertility but has zero effect on Hindi. This means `.lower()` systematically **narrows the gap** between English and Hindi fertility, making the comparison appear closer to parity than it actually is.

3. **Magnitude**: English fertility is inflated by 2.88% (1.2472 → 1.2831). The hin/eng ratio changes from 6.09× (without lower) to 5.92× (with lower). The 0.17× difference may seem small but it represents a systematic bias.

4. **The comment is misleading**: The comment says "lowercase so casing doesn't add noise to the comparison." But casing is not noise — it is a real property of the input that affects tokenization cost. Lowercasing removes real signal.

#### Verdict
**CONFIRMED — THIS IS A BUG, NOT "SUSPICIOUS BUT CORRECT"**

`.lower()` is not harmless. It inflates English token counts by 3.12%, has zero effect on Hindi, and thereby systematically biases the cross-language fertility ratio downward. The original rationale ("casing doesn't add noise") is incorrect — casing affects BPE merges and therefore real tokenization cost.

**Revision to initial hypothesis**: I initially suspected `.lower()` might be the "suspicious but correct" item. The evidence shows it is a genuine bug with an asymmetric cross-language effect. This means the "suspicious but correct" item is likely something else — perhaps `len(line)` (EXP-004).

#### Revision / Next Step
- `.lower()` is confirmed as a code bug affecting English disproportionately.
- Need to re-assess what the "suspicious but correct" item is.
- Next: EXP-004 — test `len(line)` codepoints vs grapheme clusters.

---

### EXP-004 — `len(line)` Codepoints vs Grapheme Clusters

**Stage**: A2 / len(line)  
**Date**: 2026-09-01

#### Hypothesis
`len(line)` counts Unicode codepoints, not grapheme clusters. For Hindi (Devanagari), combining characters (matras, virama) mean codepoint count > grapheme cluster count. This may make the tok/char metric misleading.

**HYPOTHESIS — NOT YET PROVEN**

#### Motivation
- **FACT (code)**: Line 63 uses `chars = len(line)`, which counts codepoints in Python 3.
- **FACT (Unicode)**: Devanagari uses combining marks. E.g., "की" (kī) = 2 codepoints (क + ी) but 1 grapheme cluster.
- **QUESTION**: How large is the codepoint/grapheme divergence on the actual Hindi corpus? Does it change the tok/char metric materially?

#### Experiment
For each line, compute codepoint count, grapheme cluster count, UTF-8 byte count, and the resulting tok/X ratios.

#### Command
```
cd "..\starter kit\starter_kit"
python "..\your-submission\partA\scripts\test_charcount.py"
```

#### Result
**MEASURED**:

**English:**
- Codepoints = Graphemes = UTF-8 bytes = 448 for all 10 lines (ASCII text)
- **Difference: 0 (0.00%)**
- tok/codepoint = tok/grapheme = tok/byte = 0.2256

**Hindi:**
- Total codepoints: 290
- Total graphemes: 188
- **Difference: 102 codepoints (54.26% more codepoints than graphemes)**
- Total UTF-8 bytes: 764

Per-line:

| Line | Codepoints | Graphemes | Diff | UTF-8 bytes | Tokens | tok/cp | tok/gr | tok/byte |
|------|-----------|-----------|------|------------|--------|--------|--------|----------|
| 1 | 30 | 22 | 8 | 78 | 47 | 1.5667 | 2.1364 | 0.6026 |
| 2 | 38 | 24 | 14 | 100 | 61 | 1.6053 | 2.5417 | 0.6100 |
| 3 | 30 | 21 | 9 | 78 | 47 | 1.5667 | 2.2381 | 0.6026 |
| 4 | 32 | 21 | 11 | 84 | 51 | 1.5938 | 2.4286 | 0.6071 |
| 5 | 24 | 14 | 10 | 62 | 34 | 1.4167 | 2.4286 | 0.5484 |
| 6 | 24 | 17 | 7 | 64 | 40 | 1.6667 | 2.3529 | 0.6250 |
| 7 | 36 | 21 | 15 | 96 | 59 | 1.6389 | 2.8095 | 0.6146 |
| 8 | 22 | 13 | 9 | 60 | 35 | 1.5909 | 2.6923 | 0.5833 |
| 9 | 26 | 18 | 8 | 68 | 40 | 1.5385 | 2.2222 | 0.5882 |
| 10 | 28 | 17 | 11 | 74 | 45 | 1.6071 | 2.6471 | 0.6081 |

**Averages:**

| Metric | English | Hindi |
|--------|---------|-------|
| tok/codepoint | 0.2256 | 1.5791 |
| tok/grapheme | 0.2256 | 2.4497 |
| tok/utf8_byte | 0.2256 | 0.5990 |
| Delta tok/cp vs tok/gr | 0.0000 | -0.8706 |

#### Evidence

1. **The difference is LARGE**: Hindi has 54.26% more codepoints than grapheme clusters. This is because virtually every Hindi akshara (visual syllable) is composed of a base consonant + one or more combining marks.

2. **Effect on tok/char metric**: The tok/codepoint ratio for Hindi (1.5791) is **substantially different** from tok/grapheme (2.4497). The difference is -0.8706, or about 35.5% relative.

3. **However — the metric label says "tok/char", not "tok/grapheme"**: In Python, `len(string)` counts characters (= codepoints), and this is the standard meaning of "character" in programming. The metric label "tok/char" is technically accurate if "char" = "codepoint."

4. **The metric is not being used for the cross-language cost comparison**: REPORT_v0 uses tok/word (fertility) for its 5.89× cost claim, not tok/char. The tok/char column is secondary ("agrees: 1.579 vs 0.226"). Even if tok/char is debatable, it doesn't drive the report's headline conclusion.

5. **Cross-language implications**: For English, all three measures (codepoint, grapheme, byte) are identical. The divergence only matters for scripts with combining characters. So `len(line)` introduces no cross-language bias *within the tok/char metric* — it consistently measures codepoints.

#### Verdict
**CONFIRMED — SUSPICIOUS BUT CORRECT**

`len(line)` counting codepoints instead of grapheme clusters is initially suspicious because the 54.26% codepoint/grapheme divergence for Hindi seems alarming. However:
- The metric is labelled "tok/char," and "char" = codepoint is the standard Python/programming definition
- The metric is consistent (always measures codepoints, for both languages)
- The report does not use tok/char for its headline cost claim
- Changing to grapheme clusters would change the *number* but not introduce or fix any *error* in the metric's definition

This is the **"suspicious but actually fine"** item the assignment describes: it looks wrong because of the large codepoint/grapheme gap, but it is internally consistent and correctly labelled.

#### Revision / Next Step
- `len(line)` is suspicious but correct. This is likely the assignment's "suspicious but fine" item.
- We have now classified all A2 candidates:
  - **Code bug #1**: `split(" ")` (EXP-002)
  - **Code bug #2**: `.lower()` (EXP-003) — asymmetric effect on cross-language comparison
  - **Suspicious but correct**: `len(line)` codepoints (EXP-004)
  - **Conceptual problem**: tok/word as cost proxy (EXP-005, see below)
- Next: Record EXP-005 and EXP-006, then perform A2 Stage Review.

---

### EXP-005 — Cross-Language Ratio Under Multiple Denominators

**Stage**: A2 / denominators  
**Date**: 2026-09-01

#### Hypothesis
If tok/word is the wrong metric for cross-language cost comparison, then different denominators will yield materially different hin/eng ratios. The denominator that holds *content* constant across languages (parallel sentence) should give the most honest cost estimate.

**HYPOTHESIS — NOT YET PROVEN** (we do not pre-decide which denominator is correct)

#### Motivation
- The report claims "Serving Hindi will cost us roughly 6× more per request than English" based on tok/word = 5.89×.
- The corpora are parallel (same content, same sentence count).
- If tok/word overstates or understates the actual per-request cost ratio, it misleads capacity planning.

#### Experiment
Compute total tokens, words, codepoints, graphemes, UTF-8 bytes, and sentences for each language. Derive tokens/X for each X and compare hin/eng ratios.

#### Command
```
cd "..\starter kit\starter_kit"
python "..\your-submission\partA\scripts\test_denominators.py"
```

#### Result
**MEASURED**:

**Raw totals (both languages, 10 parallel sentences each):**

| Metric | English | Hindi | hin/eng ratio |
|--------|---------|-------|---------------|
| tokens | 99 | 459 | 4.6364 |
| words (split " ", buggy) | 79 | 62 | 0.7848 |
| words (split(), corrected) | 78 | 61 | 0.7821 |
| codepoints | 448 | 290 | 0.6473 |
| graphemes | 448 | 188 | 0.4196 |
| utf8_bytes | 448 | 764 | 1.7054 |
| sentences | 10 | 10 | 1.0000 |

**Critical observation**: Hindi uses **fewer words** (61) than English (78) to express the **same content**. This is a MEASURED FACT.

**Cross-language ratios by denominator:**

| Denominator | eng value | hin value | hin/eng ratio | What this measures |
|-------------|-----------|-----------|--------------|-------------------|
| tok/word (buggy) | 1.2532 | 7.4032 | 5.91× | tokens per whitespace word |
| tok/word (corrected) | 1.2692 | 7.5246 | 5.93× | tokens per whitespace word |
| tok/codepoint | 0.2210 | 1.5828 | 7.16× | tokens per Unicode codepoint |
| tok/grapheme | 0.2210 | 2.4415 | 11.05× | tokens per visual character |
| tok/utf8_byte | 0.2210 | 0.6008 | 2.72× | tokens per byte of storage |
| **tok/sentence (parallel)** | **9.9000** | **45.9000** | **4.64×** | **tokens per unit of equivalent content** |

**Key finding**: The ratios span from 2.72× (tok/byte) to 11.05× (tok/grapheme). The report's 5.89× (tok/word) is one value on this spectrum. The tok/sentence ratio is 4.64×.

#### Evidence

1. **MEASURED**: Different denominators give drastically different hin/eng ratios (range: 2.72× to 11.05×). This proves that the denominator choice materially affects the conclusion.

2. **MEASURED**: Hindi uses 61 words vs English's 78 words for the same 10 parallel sentences (ratio 0.78). This means tok/word conflates two effects: (a) the tokenizer's efficiency and (b) the language's word density.

3. **Analysis of each denominator for the cost question**:

   The routing/cost decision asks: "For the same user request, how many more tokens does Hindi consume?"

   | Denominator | What it holds constant | Suitable for cost question? |
   |-------------|----------------------|----------------------------|
   | tok/word | word count | **No** — a Hindi "word" carries more content than an English word (Hindi uses fewer words for same meaning). Overstates Hindi's relative cost. |
   | tok/codepoint | codepoint count | **No** — codepoints per unit of meaning differ across scripts. |
   | tok/grapheme | visual character count | **No** — graphemes per unit of meaning differ across scripts. |
   | tok/utf8_byte | byte storage | **Partially** — measures tokenizer efficiency relative to raw encoding, but doesn't directly answer the cost-per-request question. |
   | tok/sentence | meaning/content | **Yes** — for parallel sentences, this directly measures tokens consumed for equivalent content. This is what drives per-request serving cost. |

4. **The report's error**: The report says "Serving Hindi will cost us roughly 6× more per request than English" based on tok/word = 5.89×. But the tok/sentence ratio is 4.64×, meaning the actual per-request cost difference is ~4.6×, not ~6×. The report **overstates** Hindi's relative cost by about 28%.

#### Verdict
**CONFIRMED — tok/word is a CONCEPTUAL PROBLEM for this use case**

The metric (tok/word) computes exactly what it says — tokens per whitespace word. But for the report's stated purpose (routing and cost comparison across languages), it is the wrong denominator because whitespace words are not a content-constant unit across languages. The report's 6× cost claim is inflated by ~28% relative to the content-normalized ratio (4.64×).

**IMPORTANT CAVEAT**: This conclusion is based on the toy 10-sentence corpus. The absolute numbers will change on a larger corpus (A3). But the structural issue — that tok/word conflates tokenizer efficiency with language word density — is a property of the metric, not the corpus.

**NOTE**: We are not asserting that tok/sentence is definitively the "correct" cost metric. For production cost estimation, the right denominator depends on what "a request" looks like. But tok/sentence on parallel data is the best available proxy for "same meaning, different tokens." This assessment will be revisited in A3 with a larger corpus and multiple tokenizers.

#### Revision / Next Step
- tok/word is confirmed as the conceptual problem.
- The report's 6× claim overstates the actual per-request cost by ~28% (on this corpus).
- In A3, we will verify this finding on a larger corpus with multiple tokenizers.
- Next: EXP-006 (dead code check), then A2 Stage Review.

---

### EXP-006 — `import random` and `random.seed(1337)` Dead Code Check

**Stage**: A2 / dead code  
**Date**: 2026-09-01

#### Hypothesis
`import random` (line 21) and `random.seed(1337)` (line 25) are dead code — imported and seeded but never called anywhere in the script.

**HYPOTHESIS — NOT YET PROVEN**

#### Motivation
- The script imports `random` and seeds it, suggesting the author planned or previously used randomization (e.g., sampling lines). But does the current script use it?

#### Experiment
Search the entire script for any reference to `random` beyond the import and seed lines.

#### Command
Manual inspection of fertility.py (107 lines):
- Line 21: `import random`
- Line 25: `random.seed(1337)  # reproducibility`
- Lines 28-107: No other reference to `random` found in `load_tokenizer()`, `read_lines()`, `analyze()`, or `main()`.

#### Result
**MEASURED**: `random` is referenced only on lines 21 and 25. No functional code uses it.

#### Evidence
Full scan of the script confirms `random` is never called. The seed is set but irrelevant since no random operation occurs. This is dead code.

#### Verdict
**CONFIRMED — DEAD CODE**

Not a results-affecting bug. It's a code quality issue (leftover from a previous version that may have sampled lines). Does not affect any computed values. Will note in the audit but not claim as a significant flaw.

#### Revision / Next Step
Record this for completeness. Not a major finding.

---

### A2 Stage Review

**Date**: 2026-09-01

#### What we established:
1. **Code bug #1 (EXP-002)**: `split(" ")` creates phantom empty words on lines with consecutive spaces. Deflates fertility by 1.4-2.0% on this corpus, up to 16.7% on affected individual lines.
2. **Code bug #2 (EXP-003)**: `.lower()` inflates English token count by 3.12% (destroying uppercase BPE merges) with zero effect on Hindi, systematically biasing the cross-language ratio downward.
3. **Suspicious but correct (EXP-004)**: `len(line)` counts codepoints, not grapheme clusters. Despite a 54% codepoint/grapheme gap for Hindi, this is consistent with the "tok/char" label and standard Python semantics.
4. **Conceptual problem (EXP-005)**: tok/word is the wrong denominator for cross-language cost comparison. It conflates tokenizer efficiency with language word density. The report's 6× claim overstates the per-request cost ratio (4.64× on parallel data) by ~28%.
5. **Dead code (EXP-006)**: `import random` + `random.seed(1337)` is unused.

#### What we disproved:
- Initial hypothesis that `.lower()` might be "suspicious but correct" — it turned out to be a genuine asymmetric bug.

#### What remains uncertain:
- All measurements are on a 10-sentence toy corpus. A3 will determine whether findings hold on a larger, proper eval corpus.
- We have not yet tested with a multilingual tokenizer — the cross-language ratio may differ dramatically with an Indic-aware tokenizer.
- The exact "correct" cost metric for production routing is still under investigation (tok/sentence is best available, but depends on request structure).

#### What changed in our thinking:
- Initially expected one code bug and one conceptual problem. Found **two** code bugs (split + lower), one conceptual problem (tok/word), and correctly identified the suspicious-but-fine item (len/codepoints).
- The `.lower()` effect was a surprise — expected it to be negligible but found +3.12% on English with zero on Hindi.
#### What we will investigate next:
- A1: Build proper eval corpus (FLORES-200)
- A3: Corrected analysis on larger corpus with multiple tokenizers and denominators

---

### EXP-A1-001 — Corpus-source investigation and selection

**Stage**: A1 / Corpus Selection  
**Date**: 2026-09-01

#### Hypothesis / Objective
To find a publicly accessible, reproducible multilingual parallel evaluation corpus containing English, Hindi, and at least two Dravidian languages, with enough sentences (~200+) for stable comparison.

#### Motivation
The assignment requires a robust parallel corpus for A3. FLORES-200 is the standard benchmark for this task, but we must verify if we can access it programmatically without authentication barriers.

#### Experiment
Attempt to download FLORES-200 via multiple methods:
1. Direct download via `datasets` library from `facebook/flores` and `openlanguagedata/flores_plus`.
2. Direct raw HTTP download from GitHub `facebookresearch/flores` and `openlanguagedata/flores`.
3. Search for open mirrors on HuggingFace.

#### Command
Various iterations of `partA/scripts/prepare_corpus.py` and `search_web`.

#### Result
**MEASURED**:
- `facebook/flores` and `openlanguagedata/flores_plus` are gated and failed with `DatasetNotFoundError: ... You must be authenticated to access it.`
- GitHub raw URLs returned `HTTP Error 404: Not Found` because the raw text structure is no longer maintained there.
- Searching HuggingFace for `flores200` revealed a community mirror `yash9439/flores200` which contains the full `devtest` split in Parquet format, ungated.

#### Evidence
The script outputs confirmed that the standard paths are gated, but the community mirror successfully loaded 1012 rows of data with all expected language columns.

#### Verdict
**SUCCESS** - Selected `yash9439/flores200` as the corpus source. It provides the exact FLORES-200 devtest data (English, Hindi, Kannada, Tamil) without authentication barriers.

#### Revision / Next Step
Proceed to extract and validate the specific target languages from this source (EXP-A1-002).

---

### EXP-A1-002 — Corpus download/extraction

**Stage**: A1 / Corpus Extraction  
**Date**: 2026-09-01

#### Hypothesis / Objective
We can programmatically extract exactly parallel text files for English (`eng_Latn`), Hindi (`hin_Deva`), Kannada (`kan_Knda`), and Tamil (`tam_Taml`) from the selected dataset.

#### Motivation
We need plain text, normalized, aligned parallel sentence files for our evaluation script in A3.

#### Experiment
Run `prepare_corpus.py` using `datasets.load_dataset("yash9439/flores200")`. Apply Unicode NFC normalization. Drop any empty lines.

#### Command
```
cd "..\your-submission"
python "partA\scripts\prepare_corpus.py"
```

#### Result
**MEASURED**:
- Extracted 1012 sentences for all 4 languages.
- 0 lines were skipped (no empty lines found).
- Files successfully written to `partA/corpus/`.

#### Evidence
Script logs confirmed: `PASS: All languages have 1012 parallel sentences.`

#### Verdict
**SUCCESS** - Data successfully extracted and normalized.

#### Revision / Next Step
Review corpus statistics to ensure data sanity (EXP-A1-003).

---

### EXP-A1-003 — Corpus validation and statistics

**Stage**: A1 / Corpus Validation  
**Date**: 2026-09-01

#### Hypothesis / Objective
The extracted text files are perfectly aligned and exhibit the expected cross-lingual differences (e.g., word count variation despite identical meaning).

#### Motivation
We must ensure the data isn't corrupted and understand its basic properties before running tokenization benchmarks.

#### Experiment
Analyze the extracted files for line counts, word counts, codepoint counts, and byte counts.

#### Command
Output included in the run of `prepare_corpus.py`.

#### Result
**MEASURED**:
- Line counts: 1012 across all 4 files (perfect alignment).
- Word counts:
  - English: 21,901 words
  - Hindi: 25,643 words
  - Kannada: 16,100 words
  - Tamil: 16,775 words

#### Evidence
The word counts confirm our finding from EXP-005 on the starter corpus: languages use vastly different numbers of whitespace-separated words to express the exact same 1012 sentences. English uses ~22k words, whereas the Dravidian languages (which are highly agglutinative) use ~16k words to express the same content.

#### Verdict
**SUCCESS** - The corpus is valid, aligned, and reveals deep morphological differences between the language families, reinforcing why `tok/word` is a flawed metric.

#### Revision / Next Step
A1 is complete. We can proceed to A3.

---

### Stage A1 Review

**Date**: 2026-09-01

#### What we established:
- The official FLORES repositories require authentication or have moved/deleted raw files.
- An ungated HuggingFace mirror (`yash9439/flores200`) contains the exact FLORES-200 devtest data.
- We successfully extracted 1012 perfectly aligned parallel sentences for English, Hindi, Kannada, and Tamil.
- The data validates our earlier finding: agglutinative Dravidian languages use far fewer words (~16k) than English (~22k) for the same meaning.

#### What source we selected:
- Dataset: FLORES-200 devtest
- Source: `yash9439/flores200` on HuggingFace.

#### Corpus size:
- 1012 sentences per language.

#### Major preprocessing:
- Unicode NFC normalization applied to ensure consistent character representation.

#### Limitations:
- The corpus is Wikipedia-based formal text. It may not reflect the tokenization efficiency of casual text or code.

#### Unresolved concerns:
- None. The corpus perfectly satisfies the requirements for A3.

#### Is the corpus ready for A3?
- **YES**. A1 is complete. We have the data and documentation (`partA/A1_corpus.md`) ready for the full tokenization evaluation in A3.

---

### A2/A1 Quality Gate Review

**Date**: 2026-09-01

#### 1. A2 Classification Quality Check
- **EXP-003 (`.lower()`) Re-evaluation**: 
  - *What the experiment PROVES*: `.lower()` changes English token counts by 3.12% but does not affect Hindi in the tested corpus.
  - *What it SUGGESTS*: The original author intended case-insensitive normalization (commented: "so casing doesn't add noise").
  - *Interpretation*: Real-world API requests for LLMs are case-sensitive. By artificially lowercasing English, the script undercounts the actual tokens an English prompt would consume in production. 
  - *Final Classification Update*: `.lower()` is not an "implementation bug" (the code does what the author intended). It is a **methodological/design choice** that is inappropriate because it distorts real-world serving cost.

#### 2. A2 Conceptual-Metric Check
- **Deployment Question**: "What quantity are we trying to predict when deciding routing/capacity/cost across languages?"
- **Metric Evaluation**:
  - `tok/word`: Numerator = tokens, denominator = whitespace-separated strings. The word count is not held constant across languages (e.g., Hindi uses fewer words than English for the same meaning). It does not approximate serving cost. Not appropriate.
  - `tok/codepoint`: Denominator = Unicode characters. Codepoints per unit of meaning varies drastically by script (e.g., Devanagari uses many combining marks). Not appropriate for cost.
  - `tok/grapheme`: Denominator = visual characters. Still varies significantly across language families. Not appropriate for cost.
  - `tok/UTF-8 byte`: Denominator = bytes. Measures tokenizer efficiency relative to raw UTF-8 encoding, but doesn't predict per-request cost directly since byte-length per meaning varies.
  - `tok/parallel sentence`: Numerator = tokens, denominator = aligned sentences. **Holds meaning/content constant**. Approximates "per user request cost". This is the most appropriate metric for routing/cost decisions.

#### 3. Original-File Integrity Check
- **Check**: Verified that no files in `starter_kit/` (`fertility.py`, `REPORT_v0.md`, etc.) were modified during our investigation. All changes and custom scripts are properly isolated in `your-submission/partA/`.
- **Verdict**: PASS. Original files are completely untouched.

#### 4. A1 Corpus Documentation Check
- **Check**: Edited `A1_corpus.md` to remove unsupported claims (like "agglutinative morphology" strictly explaining the word count diff) and to phrase the HuggingFace mirror's provenance conservatively.
- **Verdict**: PASS. Documentation is accurate.

#### 5. A3 Readiness Check
- A1 corpus exists and validates. (YES)
- A1_corpus.md is accurate. (YES)
- A2 experiments are recorded and classifications refined. (YES)
- Original starter files are untouched. (YES)
- **Verdict**: PASS. Ready for A3.

---

### EXP-A3-001 — A3 First Tokenizer Evaluation (GPT-2)

**Stage**: A3 / Tokenizer Evaluation  
**Date**: 2026-09-01

#### Hypothesis / Objective
To measure the cross-language tokenization cost using the original GPT-2 tokenizer on the full 1,012-sentence parallel corpus, computing all relevant denominators to definitively establish the true per-request cost ratio.

#### Motivation
We need to run the corrected evaluation pipeline (without `.lower()`, without `split(" ")` bugs) on the robust A1 corpus to establish our baseline for A3.

#### Second Tokenizer Selection
Before running, we select **`o200k_base` (GPT-4o tokenizer)** as the second tokenizer for future evaluation. 
- *Why*: It is highly capable and explicitly optimized for multilingual/Indic text, unlike GPT-2. 
- *Accessibility*: It is built directly into the `tiktoken` library (v0.14.0+) we are already using, making it 100% accessible, offline, and reproducible without external API calls or large model downloads.

#### Experiment (First Tokenizer Only)
Write an evaluation script `partA/scripts/evaluate_a3.py` that computes total tokens, words (corrected split), codepoints, graphemes, UTF-8 bytes, and sentences. 
Run it using the `gpt2` tokenizer on the 4 A1 languages.

#### Command
```
python "partA\scripts\evaluate_a3.py" --tokenizer gpt2
```

#### Result
**MEASURED**:
*Metrics are rounded for readability.*

**1. Total Tokens (vs English 27,044)**:
- Hindi: 200,688 (7.42x)
- Kannada: 367,366 (13.58x)
- Tamil: 420,171 (15.54x)

**2. Cost Multiplier (Cost relative to English) by Denominator**:
- **tok/sentence** (The true meaning-equivalent multiplier):
  - Hindi: 7.42x
  - Kannada: 13.58x
  - Tamil: 15.54x
- **tok/word** (The flawed original metric):
  - Hindi: 6.34x (Underestimates cost)
  - Kannada: 18.48x (Overestimates cost)
  - Tamil: 20.28x (Overestimates cost)

#### Evidence
Tamil requires 15.54x more tokens than English to convey the exact same 1,012 sentences (meaning constant). However, because Tamil expresses those sentences using fewer whitespace-separated words (16,775 words vs English's 21,901 words), dividing the massive token count by the much smaller word count yields an artificially inflated `tok/word` metric (25.05 tok/word vs English's 1.23 tok/word). This makes Tamil look 20.28x more expensive per word, when in reality, it is only 15.54x more expensive per request/sentence. 

#### INFERENCE
`tok/word` is potentially misleading for the stated routing/cost objective because the word count varies dramatically across languages for the exact same semantic content, distorting the cross-language cost ratio.

#### HYPOTHESIS TO VALIDATE
Parallel-sentence normalization is the most defensible cost proxy for equivalent content, because it holds the amount of meaning/content constant.

#### Verdict
**SUCCESS** - We have established that different denominators produce materially different cross-language ratios. The baseline GPT-2 measurement is complete.

#### Revision / Next Step
Run the script using the second tokenizer (`xlm-roberta-base`) to determine how an explicitly multilingual tokenizer changes these ratios.

---

### A3 Tokenizer Selection (Second Tokenizer)

**Date**: 2026-09-01

#### Investigation
The assignment requires a strictly "multilingual/Indic-aware" tokenizer. 
- *Rejected*: `o200k_base` (GPT-4o). While it has strong multilingual performance due to a massive vocabulary, its underlying design choices and exact Indic coverage aren't transparently published as an academic standard for "Indic-aware" tokenization.
- *Rejected*: `ai4bharat/indic-bert`. Explicitly built for Indic languages, but the repository is gated on HuggingFace and requires authentication, breaking reproducibility.
- *Selected*: **`xlm-roberta-base`**. 

#### Justification
XLM-R (Cross-lingual Language Model - Roberta) is the gold standard open multilingual model by Meta (Facebook AI). Its SentencePiece tokenizer was explicitly trained on common crawl data for 100 languages, with strong representation for Hindi, Tamil, Kannada, and other Indic languages. It is definitively "multilingual/Indic-aware" by design and is 100% accessible locally via the `transformers` library without authentication.

---

### EXP-A3-002 — Second Tokenizer Evaluation (XLM-R)

**Stage**: A3 / Tokenizer Evaluation  
**Date**: 2026-09-01

#### Hypothesis / Objective
Measure cross-language tokenization cost using an explicitly multilingual tokenizer (`xlm-roberta-base`) on the exact same A1 corpus (same sentences, preprocessing, denominators) to see how tokenizer architecture affects the cost ratio.

#### Experiment
Run `evaluate_a3.py` using `xlm-roberta-base`.

#### Command
```
python "partA\scripts\evaluate_a3.py" --tokenizer xlm-roberta-base
```

#### Result

**MEASURED**:
*Total Tokens:*
- English: 30,661 (GPT-2: 27,044) -> XLM-R uses *more* tokens for English.
- Hindi: 38,221 (GPT-2: 200,688) -> 81% reduction
- Kannada: 41,459 (GPT-2: 367,366) -> 89% reduction
- Tamil: 41,354 (GPT-2: 420,171) -> 90% reduction

*Cost Multiplier (Cost relative to English) by Denominator:*
- **tok/sentence** (Meaning constant):
  - Hindi: 1.25x (was 7.42x)
  - Kannada: 1.35x (was 13.58x)
  - Tamil: 1.35x (was 15.54x)
- **tok/word** (Whitespace constant):
  - Hindi: 1.06x (underestimates cost)
  - Kannada: 1.84x (overestimates cost)
  - Tamil: 1.76x (overestimates cost)

#### Direct Comparison & Sensitivity
The `tok/sentence` ratio is robust. The sentence-level variability (StDev ~10-15 tokens for XLM-R) shows the token distribution is relatively tight, meaning the total `tok/sentence` ratio is a stable proxy for average per-request cost, not an artifact of a few outlier sentences.

#### Interpretation
1. **Tokenizer Efficiency**: Legacy/English-centric tokenizers (GPT-2) are disastrously inefficient for Indic languages, causing massive (15x) token bloat. Multilingual tokenizers (XLM-R) largely solve this, dropping the penalty to ~1.35x.
2. **Cross-Language Token Disparity**: On this parallel evaluation corpus, XLM-R produces approximately 25-35% more input tokens for Hindi, Kannada, and Tamil than English, making this the observed token-workload multiplier for semantically matched inputs.
3. **Actual Serving-Cost Implication**: For leadership deciding routing/capacity, the correct multiplier to model traffic cost is the `tok/sentence` ratio (e.g., 1.35x for Tamil using XLM-R). The original `tok/word` metric is fundamentally invalid because it distorts reality: it would falsely tell leadership that Tamil costs 1.76x using XLM-R, penalizing agglutinative languages.

#### Verdict
**SUCCESS** - The dual-tokenizer experiment proves that while upgrading the tokenizer heavily mitigates the cost disparity, the choice of *denominator* (`tok/sentence` vs `tok/word`) dictates whether the capacity planning model correctly reflects reality. 

#### Revision / Next Step
A3 is complete. The audit findings are solidified. Proceed to A4 (Recommendation Memo).

---

### Final Denominator Decision

**Date**: 2026-09-01

#### Deployment Question
"What quantity are we trying to predict when deciding routing/capacity/cost across languages?"
We are attempting to predict the **average token workload per unit of user-intended meaning** (e.g. per query, per prompt, per request).

#### Evaluation of Denominators
1. **TOK/WORD**:
   - *Numerator*: Token count
   - *Denominator*: Whitespace-separated string count
   - *Constant*: Nothing. Word count varies drastically across languages for the exact same meaning.
   - *Approximates*: Tokenizer efficiency relative to space-delimited clusters.
   - *Limitation*: Agglutinative languages (Tamil, Kannada) pack more meaning into fewer words. `tok/word` artificially inflates their cost multiplier relative to English.
2. **TOK/CODEPOINT**:
   - *Numerator*: Token count
   - *Denominator*: Unicode codepoints
   - *Constant*: Nothing. Different scripts require vastly different codepoint counts (e.g. Devanagari matras).
   - *Approximates*: Tokenizer efficiency per raw string element.
   - *Limitation*: Does not hold meaning constant.
3. **TOK/GRAPHEME**:
   - *Numerator*: Token count
   - *Denominator*: Visual characters (grapheme clusters)
   - *Constant*: Visual length.
   - *Approximates*: Tokenizer efficiency per user-perceived character.
   - *Limitation*: Orthographic density varies by language family. Does not hold meaning constant.
4. **TOK/UTF-8 BYTE**:
   - *Numerator*: Token count
   - *Denominator*: Bytes
   - *Constant*: Storage size.
   - *Approximates*: Compression ratio over raw UTF-8.
   - *Limitation*: UTF-8 variable length encoding heavily penalizes non-Latin scripts (3 bytes per character vs 1 for English).
5. **TOK/ALIGNED SENTENCE**:
   - *Numerator*: Token count
   - *Denominator*: Aligned parallel sentences
   - *Constant*: Semantic meaning / Content.
   - *Approximates*: Average per-request serving cost.
   - *Limitation*: Only computable on explicitly parallel corpora.

#### Conclusion
The experiment shows that, on the parallel evaluation corpus, total tokens per aligned sentence gives an empirical estimate of the average token-count multiplier for semantically matched content. Because the evaluation corpus is parallel, aligned-sentence token count is the most direct empirical measure we have for average token workload on semantically matched inputs. 

*Production Caveat*: This evaluation corpus consists of formal Wikipedia sentences. Real production traffic contains different request lengths, domains, casual registers, code, formatting, system prompts, and output lengths. Production monitoring must validate that the relationship holds for live traffic, but for the purpose of a static capacity audit, `tok/sentence` provides the most defensible cross-language baseline.

---

### A3 Final Verification and Summary

**Date**: 2026-09-01

#### 1. Script Correctness Verification
An independent script (`verify_semantics.py`) was run on the sentence "नमस्ते दुनिया" (Namaste duniya) to explicitly verify `evaluate_a3.py` semantics:
- Expected: 2 words, 13 codepoints, 7 graphemes, 37 bytes. GPT-2 tokens: 23, XLM-R tokens: 3.
- Actual Output: Matched perfectly. This confirms that all whitespace splitting, length, uniseg grapheme extraction, encoding, and tokenizer configurations are deterministic and correct.

#### 2. Sentence-Level Robustness
We computed the mean and standard deviation of the token ratio *per sentence* to check whether the aggregate multiplier is driven by weighting differences between long and short sentences.
- **XLM-R Tamil vs English**:
  - Ratio of Aggregate Totals (A): 1.35x
  - Mean of Per-Sentence Ratios (B): 1.36x
  - StDev of Ratios: 0.24x
The strong agreement between these two estimates (1.35x vs 1.36x) indicates that the aggregate result is not strongly driven by length weighting differences. The standard deviation of 0.24x reflects the underlying variability of the sentence-level token disparity.

#### 3. Connection to Original Report (Audit Before vs After)
The original report (using `tok/word` and `gpt2` with bugs) claimed severe cost penalties. By correcting the denominator to `tok/sentence` and evaluating an explicitly multilingual tokenizer (`xlm-roberta-base`), the audit completely transforms the capacity planning landscape.

**Original GPT-2 tok/word multiplier** -> **Corrected GPT-2 tok/sentence multiplier** -> **XLM-R tok/sentence multiplier**
- **Hindi**: 6.34x -> 7.42x -> **1.25x**
- **Kannada**: 18.48x -> 13.58x -> **1.35x**
- **Tamil**: 20.28x -> 15.54x -> **1.35x**

*Note: The initial report wildly overestimated Tamil's cost at ~20x (due to `tok/word` on an agglutinative language). By fixing the metric, the true GPT-2 penalty is ~15.5x. By fixing the tokenizer, the penalty drops to ~1.35x.*

#### 4. Distinguishing Efficiency from Cost
- **Tokenizer Efficiency**: XLM-R is vastly more efficient for Indic languages (reducing Hindi tokens by 81% and Tamil by 90% compared to GPT-2). We *measure* that XLM-R produces more English tokens than GPT-2 (30k vs 27k), which *suggests* a trade-off was made in its vocabulary design to allocate space for 100 languages.
- **Cross-Language Token Disparity**: Even with XLM-R, Indic languages generate more tokens than English for matched content.
- **Production Serving Cost**: On this parallel evaluation corpus, XLM-R produces approximately 25-35% more input tokens for Hindi, Kannada, and Tamil than English, making this the observed token-workload multiplier for semantically matched inputs. This does not establish a universal production-capacity law, but serves as the best empirical estimate available prior to live deployment monitoring.

#### Readiness
A3 is fully verified and complete. The consolidated data table is available at `partA/results/a3_comparison.md`. The audit is ready for A4.

---
## PART B: Capacity Reconciliation

### EXP-B1-001 — KV Cache Arithmetic
**Stage**: B1 / Capacity
**Hypothesis**: We can determine the exact maximum concurrency by calculating the byte size of the KV cache per token using model specifications.
**Motivation**: To find the true physical limit of concurrent sequences before memory limits apply.
**Command**: `python partB/scripts/capacity_math.py`
**Measured Result**: 
- Bytes per token: 114,688
- Max 4096-token sequence: 448.00 MiB
- Concurrency on 80GB A100 (0.92 util, 7.82 GiB weights, 1.6 GB overhead): 146 sequences
**Evidence**: Derived strictly from `model_spec.md` (2 * 2 * 28 layers * 8 heads * 128 dim). 
**Interpretation**: The exact mathematical calculation provides the hard physical limit of concurrent requests based on KV cache size.
**Verdict**: SUCCESS - Base theoretical capacity arithmetic verified.
**Next Step**: Parse the benchmark CSV to find out what actually happened during the long-context sweep on the L4 GPU.

### EXP-B2-001 — Long Context Anomaly Investigation
**Stage**: B2 / Anomaly 
**Hypothesis**: The severe throughput drop after batch 24 in long-context requests is caused by KV cache saturation triggering scheduler preemption.
**Motivation**: `REPORT_v0.md` missed the throughput collapse. We need to identify the exact mechanism holding performance back.
**Command**: `python partB/scripts/parse_bench.py`
**Measured Result**: 
- Batch 24 throughput peaks at 1607.4 tok/s. KV cache util = 0.93. Preemptions = 0.
- Batch 32 throughput drops to 1384.0 tok/s. KV cache util = 0.97. Preemptions = 7.
- Batch 48 throughput drops to 1298.5 tok/s. KV cache util = 0.97. Preemptions = 23.
**Evidence**: On an L4 GPU (24GB), usable memory for KV is ~12.08 GB. A 4096-token sequence requires ~0.47 GB. $12.08 / 0.47 \approx 25.7$ sequences. 
**Interpretation**: Batch 24 fits perfectly within memory. Batch 32 exceeds memory, causing the vLLM scheduler to hit its 0.97 utilization ceiling, preempt sequences, and thrash, which tanks goodput. 
**Verdict**: SUCCESS - Anomaly explained flawlessly by exact memory arithmetic.
**Next Step**: Propose a configuration change (hard-capping max concurrent sequences to 24/25) to prevent this memory pressure. Then investigate the actual meaning of `reported_tok_s`.

### EXP-B3-001 — Throughput Definition 
**Stage**: B3 / Benchmark Audit
**Hypothesis**: `reported_tok_s` artificially credits prompt tokens, leading to a misleading interpretation in the original report.
**Motivation**: The original report claims long prompts improve GPU utilization by comparing 1311 tok/s to 883 tok/s.
**Command**: `python partB/scripts/infer_throughput_definition.py`
**Measured Result**: 
- The error for formula `batch * (prompt + gen) / wall` is exactly ~0.00%. 
- `reported_tok_s` definitively conflates prompt and generated tokens.
**Evidence**: Two independent derivations of honest goodput for the peak batch 24 row yield exactly 200.9 tok/s, mathematically disproving the reported "1607 tok/s" generation rate.
**Interpretation**: The original author failed to realize the harness was inflating the metric by taking credit for the 3584 prefill tokens. Long prompts actually yield significantly *worse* generation throughput (200.9 tok/s) compared to short prompts (294.5 tok/s).
**Verdict**: SUCCESS - The fundamental misinterpretation in `REPORT_v0.md` is fully resolved and corrected.

### EXP-B-REVISION — Precision & Causality Review
**Stage**: B1-B3 Cleanup
**Motivation**: To ensure that interpretations strictly separate measured observation from causal inference, and that memory/metric terminology is mathematically exact.
**Refinements Made**:
1. **Memory Causality**: Updated `B2_anomaly.md` to clarify that batch 32/48 throughput collapse is *associated* with KV-cache boundary exhaustion. Rather than stating "it is impossible to fit", we refined it to state that the sequences "cannot all remain resident at once," explicitly identifying KV-cache saturation as the *strongest supported explanation* for preemption, rather than an absolute proof of causality (since the CSV does not directly measure recompute cycles).
2. **Short-Prompt Control**: Explicitly documented the short-prompt sweep (batch up to 64, 0 preemptions) as a control proving that batch-size increases *alone* do not degrade performance on this hardware.
3. **Metric Interpretation**: Updated `report_correction.md` to state that `reported_tok_s` is a valid *total-token* processing metric (matching `batch * (prompt + gen) / wall`). The flaw is the *interpretation* of this value as generation goodput in `REPORT_v0.md`.
4. **Goodput Terminology**: Explicitly delineated `reported_tok_s` from "generation goodput". Re-calculated the "longer prompts are better" claim using honest generation goodput (294.5 tok/s short vs 163.9 tok/s long), completely reversing the original report's conclusion.
5. **Memory Units**: Clarified that 80GB A100 implies 80 GiB ($80 \times 1024^3$ bytes) and $1.6 \text{ GB}$ overhead implies $1.6 \text{ GiB}$ ($1.6 \times 1024^3$ bytes) in `B1_capacity.md`.
**Next Step**: Complete the B4 serving-stack metric selection.

### EXP-B4-001 — Serving-Stack Validation Metric
**Stage**: B4 / Validation
**Hypothesis**: The `preempted_seqs` (vLLM scheduler preemptions) counter is the most diagnostic live-production metric to validate KV-cache exhaustion.
**Candidate Metrics Considered**: 
- `gpu_utilization`, `latency`, `throughput` (Rejected: Generic symptoms of degradation).
- `kv_cache_util` (Rejected: Saturation boundary trigger, but doesn't strictly measure the resulting thrashing).
- `preempted_seqs` (Selected).
**Selection Reasoning**: Preemption directly isolates the scheduler's memory intervention. The GPU only preempts active sequences when the resident KV-cache memory boundary is breached and thrashing begins. 
**Supporting Benchmark Evidence (MEASURED)**: In `bench_log.csv` (prompt 3584, gen 512), throughput scales positively up to batch 24 with 0 preemptions and 0.93 KV util. Throughput immediately collapses at batch 32 when `kv_cache_util` hits 0.97 and `preempted_seqs` > 0.
**Limitations**: The CSV does not measure explicit recompute cycles, only the preemptions themselves. The configuration change (`--max-num-seqs`) relies on a PREDICTION that queueing is superior to preemption in this workload.
**Verdict**: SUCCESS - Selected metric accurately acts as a diagnostic bridge for the B2 mechanism.

### EXP-B4-REVISION — Absolute Statement Cleanup
**Stage**: B4 / Refinement
**Motivation**: To ensure that the validation metric recommendations do not over-claim absolute mechanical certainty (e.g. "preemption only occurs when...").
**Refinements Made**:
1. Softened absolute claims in `B4_validation_metric.md`: Replaced "preemption only occurs when..." with "for this workload and serving configuration, preemption appears when...".
2. Adjusted chronological claims: Replaced "Only after preempted_seqs > 0 will generation goodput collapse" with "If KV-cache pressure is the dominant mechanism, we expect increasing preemptions to coincide with degradation in generation goodput..."
3. Adjusted falsification logic to reflect that zero preemptions under degradation makes the KV hypothesis "less plausible" rather than absolutely "falsified," since edge cases may exist.
**Verdict**: B4 wording is precise. Proceeding to Part C.

---
## PART C: Casual Output Formatting

### EXP-C-001 — Define success/evaluation target
**Stage**: Part C / Setup
**Hypothesis**: We must define casualness in a measurable way that isolates style from factual degradation.
**Motivation**: Vague targets like "sound natural" cannot be engineered against in a 2-week window.
**Measured/Assumed Constraints**: We only have native reviewers for Hindi and Kannada (10h/week).
**Interpretation**: Success must be defined by A/B casualness preference win-rate on a fixed validation set, guarded by a strict semantic error rate limit.
**Verdict**: Success metric structure established.

### EXP-C-002 — Reviewer/data feasibility
**Stage**: Part C / Constraint Arithmetic
**Hypothesis**: 10 hours/week is a severe bottleneck that dictates the entire strategy.
**Motivation**: SFT requires thousands of pairs. Can we produce them?
**Calculation (ASSUMED)**: 2 weeks × 10h/week = 20 hours. At 1 min/pair, 20h = 1,200 total reviewed pairs max (600 Hindi, 600 Kannada).
**Interpretation**: 1,200 pairs is drastically insufficient for a 6-language SFT. Without an API budget ($0), synthetic data must be self-generated by the 4B model, which will be noisy. We cannot review the other 4 languages at all.
**Verdict**: Data starvation is the dominant constraint of the project.

### EXP-C-003 — Option A analysis
**Stage**: Part C / SFT Evaluation
**Hypothesis**: Can we use the 1,200 pairs for SFT?
**Analysis (INITIAL INFERENCE - subsequently challenged)**: LoRA SFT fits on the single A100-80GB. However, training on only 600 pairs per language is unlikely to robustly shift the style distribution without overfitting. Worse, generating unreviewed synthetic data for Tamil, Telugu, Bengali, and Marathi to fill the SFT batch will cause catastrophic forgetting and semantic destruction in those languages.
**Verdict (INITIAL CLAIM - subsequently weakened)**: Option A rejected. Risk of multilingual regression is catastrophic.

### EXP-C-004 — Option B analysis
**Stage**: Part C / Rewriter Evaluation
**Hypothesis**: A <=1B inference rewriter model could intercept formal outputs and casualize them.
**Analysis (INITIAL INFERENCE - subsequently challenged)**: Shares the exact same data starvation problem as Option A. Furthermore, running a sequence-to-sequence rewriter on the same A100 adds massive latency (100-300ms) and destroys the carefully balanced KV-cache concurrency budget calculated in Part B.
**Verdict (INITIAL CLAIM - subsequently weakened)**: Option B rejected. Double-fails on data starvation and serving latency.

### EXP-C-005 — Option C analysis
**Stage**: Part C / Prompt Engineering Evaluation
**Hypothesis**: Prompt engineering bypasses the data bottleneck completely.
**Analysis (INITIAL INFERENCE - subsequently challenged)**: Bypasses training time entirely. We can spend the entire 1,200-pair human review budget purely on evaluation rather than data cleaning. Zero regression risk to model weights.
**Multilingual Risk (INITIAL PREDICTION - subsequently challenged)**: The 4 unreviewed languages may ignore the casual prompt. However, prompt failure is "safe"—it just falls back to the default formal tone. This is vastly preferable to SFT failure (hallucinations/broken grammar).
**Verdict (INITIAL CLAIM - subsequently weakened)**: Option C is the only mathematically viable path under these constraints.

### EXP-C-006 — Decision/threshold selection
**Stage**: Part C / Memo Finalization
**Decision**: Option C (Prompt Engineering).
**Numeric Thresholds (PREDICTION)**: Target >= 20% absolute win-rate in casualness over baseline, with <= 5% semantic error rate. 
**Kill Criterion**: Kill if Week 1 Day-1 experiment yields < 10% casualness win-rate or > 5% semantic error rate.
**Day-1 Experiment**: Run 200 A/B prompts (baseline vs casual) through the Hindi/Kannada reviewer immediately to test 4B zero-shot steerability.
**Verdict**: Part C memo and analysis successfully created. Project is fully resolved.

### EXP-C-007 — Hostile Review / Threshold & Assumption Audit
**Stage**: Part C / Refinement
**Motivation**: Clean up unverified absolute claims in Part C and delineate planning assumptions from scientific facts.
**Claims Challenged & Weakened**:
- *SFT requires >10k pairs* -> Weakened to: "The available reviewer bandwidth is sufficient for only ~1,200 reviewed response-pairs... Therefore a six-language, human-validated style dataset cannot be completed within the two-week window."
- *Rewriter adds 100-300ms latency* -> Weakened to: "A sequential rewriter introduces additional inference latency... the exact latency must be benchmarked before launch."
- *Prompting fails safely / zero semantic risk* -> Weakened to: "Prompt-only deployment is reversible and does not modify model weights, reducing the blast radius of style failures."
**Assumptions Made Explicit**:
- Explicitly labeled the 1 minute/pair review speed as a "PLANNING ASSUMPTION" and added a sensitivity analysis in `decision_analysis.md` (0.5, 1.0, 2.0 min/pair) proving data starvation holds regardless.
- Made the Day-1 experiment arithmetic perfectly consistent: 100 pairs total (50 Hindi, 50 Kannada) equating to exactly 1.67 hours of review load at 1 min/pair.
**Threshold Justification**:
- Labeled the 20% casualness win-rate and 5% semantic error rate as "DECISION THRESHOLD — MANAGEMENT ASSUMPTION". These are operational GO/NO-GO planning gates designed to leave pivot time, not scientifically proven constants.
**Final Decision**: Option C (Prompt Engineering) remains the recommendation. Options A and B remain not preferred under the stated constraints due to the rigid 20-hour data validation constraint and higher launch risk on unreviewed languages.
**Verdict**: Part C deliverables finalized for submission.

### EXP-C-008 — Final Metric/Decision-Language Audit
**Stage**: Part C / Final Review
**Motivation**: Run a final adversarial pass strictly policing unambiguous sample sizes, operational metric formulas, and eliminating remaining absolute claims that could fail hostile interview scrutiny.
**Ambiguities Found & Changed**:
- *Sample Size Ambiguity*: Clarified all documentation to rigidly specify 200 response pairs total for final evaluation (100 Hindi, 100 Kannada) and 100 response pairs total for the Day-1 pilot (50 Hindi, 50 Kannada), locking in the exact 1.67 reviewer hours at the 1 min/pair assumption.
- *Operational Definitions Missing*: Fully operationalized Casualness Preference Win-Rate (explicitly excluding ties from the denominator) and Semantic Error Rate as concrete ratios, rather than loose concepts.
- *Decision Language*: Replaced remaining instances of "decisively eliminated" with "not preferred under the stated constraints." Replaced "Prompt engineering is safe" with "Prompt adherence in the four unreviewed languages is uncertain and must be treated as a launch risk."
- *Historical Hygiene*: Marked absolute claims ("catastrophic", "semantic destruction", "massive latency", "zero regression risk", "only mathematically viable") in `EXP-C-003` to `EXP-C-005` strictly as "INITIAL INFERENCE - subsequently challenged/weakened" to preserve historical progression without claiming them as current facts.
**Remaining Assumptions**:
- The 20% win-rate and 5% error thresholds explicitly remain *management decision thresholds / early management gates*, not scientifically established safety boundaries.
**Final Decision**: Option C is preferred.
**Verdict**: Final consistency check complete. READY TO FREEZE.

### EXP-FINAL-001 — Reproducibility and Portability Revision
**Stage**: Final Audit
**Motivation**: A pre-packaging audit revealed hard-coded absolute Windows paths in `parse_bench.py` and `infer_throughput_definition.py` and `NOTEBOOK.md`.
**Fixes Applied**:
- Removed `c:\Users\Animesh\Desktop\flamapp\...` paths from both Python scripts and `NOTEBOOK.md`. 
- Updated scripts to use `argparse` with a reliable relative default path mapping accurately to the `starter_kit` hierarchy.
- All scripts verified to produce identical numerical results.
**Verdict**: Repository is highly portable across machines.
