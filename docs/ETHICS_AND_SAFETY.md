# Ethics, Safety and Privacy Statement

## Ethical principles
1. **Do no harm (non-maleficence).** The system puts the safety of people at risk ahead of every other goal. Crisis language triggers a fixed response with human resources, and the AI model is not used for that message.
2. **Beneficence.** It offers evidence-informed coping skills (CBT reframing, grounding, breathing, self-compassion, sleep hygiene) in an empathetic way.
3. **Autonomy.** It invites rather than instructs, gets informed consent, and gives users full control of their data.
4. **Justice and accessibility.** It is free to run, works offline in demo mode, and uses plain language.
5. **Transparency.** It is clearly labeled as an AI. It shows the detected emotion and the knowledge sources behind each reply, and it states its limitations.

## Scope of care statement
Ember is a **wellness and self-reflection tool**, not a medical device, therapist, or crisis service. It does not diagnose mental health conditions, recommend or change medication, or provide treatment. It encourages professional help when difficulties persist or are severe.

## Safety design
| Risk | Mitigation |
|---|---|
| A user in crisis | A regex screen runs before the LLM and returns 988 / 741741 / 911 / findahelpline.com; the system prompt repeats the crisis rule for indirect cases; crisis info is in the sidebar at all times |
| Harmful or inaccurate advice | Responses are grounded in a curated knowledge base; the system prompt forbids diagnosis and medical advice and tells the model not to invent facts |
| Over-reliance on the AI | Users are encouraged to build human connection and use professional services; disclaimers are shown |
| Emotion misclassification | Labeled to the model as an "automatic estimate; may be wrong"; used only to adjust tone and retrieval |
| Model refusal or outage | Refusals are handled gracefully; failures fall back to a grounded template |
| Minors | An 18+ confirmation is required; the system is not designed for or tested with minors |

## Known limitations
- Keyword screening can miss indirect, coded, misspelled, or non-English expressions of risk, and can sometimes over-trigger. It is tuned toward recall.
- Crisis numbers are US-focused (with an international directory).
- The knowledge base is general and has not been clinically validated.
- Chat text is processed by a third-party LLM provider (OpenAI) under its data policies.

## Privacy statement
- **Data minimization:** no accounts, names, emails, or identifying information are collected.
- **Local storage:** journal entries and mood logs are stored in a local SQLite file (`data/user_data/journal.db`), which is excluded from version control.
- **Third-party processing:** only chat messages, with the retrieved excerpts, are sent to the OpenAI API to generate replies.
- **User control:** one-click **export** (JSON) and **delete all data**.
- **Secrets:** API keys are kept in `.env` and never committed.

## Research ethics (for user evaluation)
- Get IRB approval or an exemption before any study with human participants.
- Recruit adult volunteers only; get written informed consent; allow withdrawal at any time.
- Use scripted or synthetic scenarios rather than asking participants to disclose real distress.
- Give every participant crisis and counseling resources.
- Do not collect identifying data; store study data securely and delete it after analysis.
