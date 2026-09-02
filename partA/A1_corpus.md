# A1 Corpus Documentation

## 1. Corpus Source
- **Dataset:** FLORES-200 (devtest split)
- **Domain:** Evaluation benchmark created from Wikipedia. This is a standard resource for modern NMT evaluation.
- **Source:** HuggingFace Datasets mirror `yash9439/flores200`
- **Why this source:** The official Meta FLORES-200 repositories on HuggingFace are gated and require authentication, which hindered automated programmatic access. The GitHub raw links also returned 404s due to structural changes (tarballs instead of raw files). This public mirror provides an accessible Parquet format intended to mirror the standard FLORES-200 devtest set, enabling programmatic extraction.

## 2. Dataset Selection
- **Languages Included:** 
  - English (`eng_Latn` -> `eng.txt`)
  - Hindi (`hin_Deva` -> `hin.txt`)
  - Kannada (`kan_Knda` -> `kan.txt`)
  - Tamil (`tam_Taml` -> `tam.txt`)
- **Total Aligned Examples:** 1012 parallel sentences.

## 3. Preprocessing & Filtering
- **Extraction:** Pulled directly from the `devtest` split via the `datasets` library.
- **Normalization:** Applied Unicode NFC (Normalization Form C) to all text to ensure character representations (especially combining marks in Indic scripts) are canonical and consistent.
- **Filtering:** 
  - Empty lines (post-strip) were checked and dropped (none found).
- **Validation:** 
  - Validated that all language files have exactly 1012 non-empty lines.
  - No lines were discarded during processing.

## 4. Final Corpus Statistics
| Language | Sentences | Words (Whitespace) | Codepoints | UTF-8 Bytes |
|----------|-----------|--------------------|------------|-------------|
| English  | 1012      | 21,901             | 131,966    | 132,096     |
| Hindi    | 1012      | 25,643             | 131,180    | 337,439     |
| Kannada  | 1012      | 16,100             | 138,027    | 375,341     |
| Tamil    | 1012      | 16,775             | 154,131    | 421,635     |

*Note: Whitespace word counts differ substantially across these languages for aligned content, demonstrating that whitespace-word count is not held constant across languages.*

## 5. Limitations
- **Size:** 1012 sentences is sufficient for a reliable fertility and token-cost evaluation but is strictly an evaluation set, not a training set.
- **Domain:** The text is formal Wikipedia prose. It does not perfectly reflect casual chat or varied prompts that an LLM in production might see. 
- **What this corpus cannot tell us:** It does not capture tokenization efficiency on code, colloquial text, or varied formatting (markdown, code blocks). However, for evaluating pure linguistic representation efficiency across languages, it is highly robust.
