"""Terminal chat with the companion.  Usage:  python cli.py"""
from src.rag_pipeline import Conversation, WellnessCompanion

DISCLAIMER = ("Ember is an AI companion for reflection and coping skills - not a therapist or crisis "
              "service. In an emergency call 911; in the US call or text 988.\nType 'quit' to exit.\n")


def main() -> None:
    companion = WellnessCompanion()
    convo = Conversation()
    print(DISCLAIMER)
    print(f"[mode: {'OpenAI ' + companion.cfg.llm_model if companion.llm.online else 'offline demo'}]\n")
    while True:
        try:
            msg = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if msg.lower() in {"quit", "exit"}:
            break
        if not msg:
            continue
        r = companion.chat(msg, convo)
        print(f"\nEmber: {r.text}\n")
        meta = f"emotion={r.emotion} ({r.intensity})"
        if r.sources:
            meta += " | sources: " + ", ".join(s["title"] for s in r.sources)
        print(f"  [{meta}]\n")


if __name__ == "__main__":
    main()
