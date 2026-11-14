import pytest

from src.llm import LLMReply
from src.rag_pipeline import Conversation, WellnessCompanion
from src.retriever import Retriever


@pytest.fixture
def retriever(cfg):
    return Retriever(cfg, rebuild=True)


@pytest.mark.parametrize("query,expected_title", [
    ("I can't sleep at night, my thoughts keep racing", "Sleep and Emotional Health"),
    ("how do I do box breathing", "Breathing and Relaxation Exercises"),
    ("I feel like a failure and so ashamed", "Self-Compassion"),
    ("I'm burned out and overwhelmed with too many tasks", "Stress and Burnout"),
])
def test_retrieval_relevance(retriever, query, expected_title):
    titles = [h.source for h in retriever.retrieve(query, k=3)]
    assert expected_title in titles


def test_index_persists_and_reloads(cfg, retriever):
    reloaded = Retriever(cfg)
    assert len(reloaded.store.chunks) == len(retriever.store.chunks)


def test_offline_chat_returns_sources(cfg, retriever):
    bot = WellnessCompanion(cfg, retriever=retriever)
    r = bot.chat("I'm really anxious about my exam tomorrow", Conversation())
    assert r.emotion == "anxiety"
    assert r.sources and not r.is_crisis
    assert r.model == "offline"


def test_crisis_bypasses_llm(cfg, retriever):
    class ExplodingLLM:
        online = True
        def generate(self, messages):
            raise AssertionError("LLM must not be called for crisis messages")

    bot = WellnessCompanion(cfg, retriever=retriever, llm=ExplodingLLM())
    r = bot.chat("I want to kill myself", Conversation())
    assert r.is_crisis and "988" in r.text


def test_history_is_append_only(cfg, retriever):
    class FakeLLM:
        online = True
        def __init__(self):
            self.calls = []
        def generate(self, messages):
            self.calls.append(list(messages))
            return LLMReply(text="I hear you.", content=[{"type": "text", "text": "I hear you."}], model="fake")

    llm = FakeLLM()
    bot = WellnessCompanion(cfg, retriever=retriever, llm=llm)
    convo = Conversation()
    bot.chat("I'm stressed", convo)
    bot.chat("Still stressed", convo)
    first, second = llm.calls
    assert second[:len(first)] == first           # earlier turns unchanged
    assert [m["role"] for m in second] == ["user", "assistant", "user"]
    assert "<knowledge_base>" in second[-1]["content"]
