import pytest

from src.safety import assess_risk, crisis_response


@pytest.mark.parametrize("msg", [
    "I want to kill myself",
    "honestly I don't want to live anymore",
    "I've been thinking about suicide",
    "everyone would be better off without me",
    "I started cutting myself again",
    "I want to end it all",
])
def test_detects_crisis(msg):
    assert assess_risk(msg).is_crisis


@pytest.mark.parametrize("msg", [
    "I'm stressed about my exam tomorrow",
    "my roommate is so annoying",
    "I feel a bit sad today",
    "this homework is killing me lol",
])
def test_no_false_positive_on_everyday_distress(msg):
    assert not assess_risk(msg).is_crisis


def test_crisis_response_includes_988():
    r = crisis_response(assess_risk("I want to die"))
    assert "988" in r and "911" in r
