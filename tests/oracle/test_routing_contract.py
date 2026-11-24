"""Routing contract extracted from orchestrator/main.py:78-87.

Does not import the scaffold. Importing main.py builds model clients.
"""

from __future__ import annotations

from pathlib import Path


def route_swarm(task_intent: str) -> str:
    intent = task_intent.lower()
    if "refactor" in intent or "complexity" in intent:
        return "janitor"
    if "500 error" in intent or "incident" in intent:
        return "sre"
    if "cost" in intent or "aws" in intent or "terraform" in intent:
        return "finops"
    if "conversion" in intent or "drop-off" in intent:
        return "growthops"
    return "general"


def test_first_match_wins():
    assert route_swarm("refactor the 500 error path") == "janitor"
    assert route_swarm("complexity is 12") == "janitor"
    assert route_swarm("500 error on login") == "sre"
    assert route_swarm("incident in the api") == "sre"
    assert route_swarm("aws cost rose") == "finops"
    assert route_swarm("terraform plan") == "finops"
    assert route_swarm("conversion drop-off on checkout") == "growthops"
    assert route_swarm("fix mobile login") == "general"


def test_source_contains_the_same_rows():
    text = Path("orchestrator/main.py").read_text(encoding="utf-8")
    for needle in (
        '"refactor" in task_intent or "complexity" in task_intent',
        'assigned_swarm = "janitor"',
        '"500 error" in task_intent or "incident" in task_intent',
        'assigned_swarm = "sre"',
        '"cost" in task_intent or "aws" in task_intent or "terraform" in task_intent',
        'assigned_swarm = "finops"',
        '"conversion" in task_intent or "drop-off" in task_intent',
        'assigned_swarm = "growthops"',
    ):
        assert needle in text
