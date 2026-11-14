# AI Companion for Emotional Wellness and Self-Reflection
### Capstone Project Proposal

---

## 1. Title
**Ember: A Retrieval-Augmented AI Companion for Emotional Wellness and Self-Reflection**

## 2. Problem Statement
Mental health challenges among college students and young adults are widespread and rising. Anxiety, depression, stress, and loneliness are common, yet many people never seek help. The usual barriers are cost, long waits for counseling appointments, stigma, and limited access outside office hours. Many students struggle at night, during exam periods, or between appointments, when no human support is available.

General-purpose chatbots are always available, but they are not designed for emotional support. They can give generic or inaccurate advice, "hallucinate" facts, miss signs of crisis, and store sensitive conversations without clear privacy controls. Self-help resources such as worksheets, apps, and articles are reliable but static. They don't respond to what a person is actually feeling in the moment.

**There is a need for an accessible, private, and safe conversational tool that grounds its responses in vetted wellness knowledge, helps users reflect on their emotions over time, and reliably directs people in crisis to human help.**

## 3. Purpose Statement
The purpose of this project is to design, build, and evaluate an AI companion that uses **Retrieval-Augmented Generation (RAG)** to provide empathetic, evidence-informed emotional support and guided self-reflection. The system combines a curated wellness knowledge base, emotion detection, a private journal and mood tracker, and a safety layer that runs before the AI model. The goal is to support everyday emotional wellbeing as a complement to professional care, never a replacement for it.

## 4. Project Objectives
1. **Build a RAG pipeline** that retrieves relevant content from a curated knowledge base covering CBT reframing, grounding, breathing, journaling, self-compassion, stress, sleep, anger, sadness, and crisis resources, and uses it to ground the language model's responses (OpenAI).
2. **Detect the user's emotional state** (anxiety, sadness, stress, anger, shame, joy, neutral) and use it to tailor the retrieval and the tone of each reply.
3. **Implement a safety-first crisis layer** that finds high-risk language (suicide, self-harm, harm to others, abuse) and immediately gives human crisis resources such as 988, 741741, and 911, without relying on the AI model.
4. **Support self-reflection** through a private journal, mood check-ins, personalized reflection prompts, and visual mood/emotion trends.
5. **Protect user privacy** with local storage, informed consent, data export, and full data deletion.
6. **Evaluate the system** on retrieval relevance, response quality, safety-detection accuracy, latency, and usability.

## 5. Research Questions
- **RQ1:** Does grounding responses in a curated wellness knowledge base (RAG) produce responses that are more relevant, accurate, and actionable than the same model without retrieval?
- **RQ2:** How accurately can a lightweight, explainable safety screen detect crisis language, and what is the trade-off between recall and false positives?
- **RQ3:** Do users find guided reflection (journaling prompts and mood trends) useful for understanding their emotional patterns?

## 6. Scope
**In scope**
- Text-based chat companion (Streamlit web app, REST API, CLI)
- RAG over a curated set of wellness documents (Markdown/TXT/PDF)
- Rule-based emotion detection and crisis detection
- Private journal, mood logging, insights dashboard, export/delete
- Offline demo mode for use without an API key

**Out of scope**
- Diagnosis, treatment, therapy, or medication advice
- Real-time human escalation or emergency dispatch
- Voice/video interaction
- Clinical trials or use with patients under clinical care
- Users under 18

## 7. Significance
- **For students:** low-barrier support available 24/7, with coping skills based on established techniques and a private space to reflect.
- **For institutions:** a model for how AI can extend, not replace, campus counseling by encouraging help-seeking and sending people in crisis to human services.
- **Technically:** shows a responsible RAG design with a layered approach to safety, grounding, and privacy that can be reused in other sensitive domains.

## 8. Methodology (summary)
1. **Requirements and literature review:** digital mental health tools, RAG, and AI safety in sensitive domains.
2. **Knowledge base curation:** write and review psychoeducation content based on public-domain guidance (CBT, mindfulness, sleep hygiene, crisis resources).
3. **System design and implementation:** see `ARCHITECTURE.md`.
4. **Testing:** unit and integration tests (pytest), a safety test set, and a retrieval relevance test set.
5. **Evaluation:** see `EVALUATION_PLAN.md`.
6. **Documentation and presentation.**

## 9. Timeline (15 weeks)
| Week | Milestone |
|---|---|
| 1-2 | Proposal, literature review, requirements |
| 3-4 | Knowledge base curation; architecture design |
| 5-6 | Document loading, chunking, embeddings, vector store |
| 7-8 | Retriever, prompt design, OpenAI integration |
| 9 | Safety layer and emotion detection |
| 10 | Journal, mood tracking, insights |
| 11 | Streamlit UI and FastAPI |
| 12 | Testing and safety evaluation |
| 13 | User study / usability evaluation |
| 14 | Analysis, refinement, final report |
| 15 | Final presentation and demo |

## 10. Expected Outcomes
- A working, tested prototype (web app, API, and CLI)
- A curated, extensible wellness knowledge base
- An evaluation report covering retrieval, response quality, safety, and usability
- Documentation: requirements, architecture, ethics and safety statement, user guide

## 11. Ethical Statement
This project treats user wellbeing and safety as its top priorities. The companion is clearly labeled as **not a therapist or crisis service**. It checks every message for crisis language before any AI processing and gives human crisis resources first. It does not diagnose or give medical advice, gets informed consent before use, stores journal data only on the user's device, and lets users export or permanently delete their data. Any user testing will be done with IRB approval (or the institution's equivalent), using adult volunteers and synthetic or non-identifying data. See `ETHICS_AND_SAFETY.md`.

## 12. Disclaimer Statement (shown to users)
> Ember is an AI companion for self-reflection and general wellness skills. It is not a substitute for professional mental health care, diagnosis, or treatment. If you are in crisis or thinking about harming yourself or others, call 911 or call/text 988 (US Suicide & Crisis Lifeline), or visit findahelpline.com.
