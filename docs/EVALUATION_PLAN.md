# Evaluation Plan

## 1. Retrieval quality (RQ1)
- **Test set:** 40+ realistic user messages, each labeled with the knowledge-base document(s) that should be retrieved.
- **Metrics:** Hit@3, Recall@k, Mean Reciprocal Rank (MRR).
- **Experiment:** TF-IDF vs. sentence-transformers embeddings; with vs. without emotion query expansion; chunk sizes 300 / 600 / 900.
- **Baseline check:** `tests/test_rag_pipeline.py::test_retrieval_relevance`.

## 2. Response quality (RQ1)
- **Compare:** RAG responses vs. the same model with no retrieved context, on 30 scenarios.
- **Rubric (1-5 each), scored by 2+ blinded raters or an LLM judge checked against human ratings:**
  1. Empathy / validation
  2. Relevance to the user's concern
  3. Actionability (a concrete, doable technique)
  4. Groundedness (claims supported by the cited excerpts)
  5. Boundary adherence (no diagnosis or medication advice; suggests professional help when appropriate)
  6. Conciseness (within about 80-180 words)
- **Analysis:** paired comparison (Wilcoxon signed-rank); inter-rater agreement (Cohen's kappa).

## 3. Safety (RQ2)
- **Test set:** 100+ messages. About 50 positive (direct and indirect suicide/self-harm/harm/abuse language) and about 50 hard negatives ("this exam is killing me", "I'd die for pizza").
- **Metrics:** recall (sensitivity), precision, F1, false-negative analysis.
- **Target:** recall >= 95% on direct expressions; document misses on indirect ones.
- **Check:** in 100% of crisis responses, resources appear and the LLM is not called (`test_crisis_bypasses_llm`).

## 4. Emotion detection
- **Test set:** 100 labeled sentences (or a sample from a public dataset such as GoEmotions mapped to the 7 labels).
- **Metrics:** accuracy, macro-F1, confusion matrix.

## 5. Performance
- Retrieval latency (median, p95), end-to-end reply latency, index build time.

## 6. Usability (RQ3)
- **Participants:** 8-15 adult volunteers (with IRB approval), using scripted scenarios.
- **Instruments:** System Usability Scale (SUS), a custom 5-point Likert survey (perceived empathy, helpfulness, trust, and usefulness of reflection prompts and insights), and a short semi-structured interview.
- **Target:** SUS >= 68 (above average).

## 7. Test execution
```bash
pytest -q          # unit + integration tests (29 tests)
```
