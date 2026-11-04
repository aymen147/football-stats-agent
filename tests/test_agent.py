"""Agent graph tests with a scripted model: no API key, no network."""

import json
from collections.abc import Sequence
from typing import Any

import pytest
from conftest import SYNTHETIC_MATCHES
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.errors import GraphRecursionError

from football_stats_agent.agent import MAX_GRAPH_STEPS, ask, build_agent
from football_stats_agent.tools import run_sql


class ScriptedChatModel(FakeMessagesListChatModel):
    """Replays scripted replies and accepts tools like a real chat model."""

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> "ScriptedChatModel":
        return self


def tool_call(name: str, args: dict[str, Any]) -> AIMessage:
    return AIMessage("", tool_calls=[{"name": name, "args": args, "id": f"call_{name}"}])


def tool_messages(messages: list[BaseMessage]) -> list[ToolMessage]:
    return [message for message in messages if isinstance(message, ToolMessage)]


def test_agent_calls_the_chosen_tool_and_answers(db_path, tmp_path):
    model = ScriptedChatModel(responses=[
        tool_call("team_stats", {"team": "Lyon"}),
        AIMessage("Lyon has 4 points."),
    ])

    messages = ask(build_agent(model, db_path, tmp_path), "How many points for Lyon?")

    [result] = tool_messages(messages)
    assert result.name == "team_stats"
    assert json.loads(result.content)["points"] == 4
    assert messages[-1].content == "Lyon has 4 points."


def test_tool_errors_go_back_to_the_model_instead_of_crashing(db_path, tmp_path):
    model = ScriptedChatModel(responses=[
        tool_call("run_sql", {"query": "DELETE FROM matches"}),
        AIMessage("I cannot modify the data."),
    ])

    messages = ask(build_agent(model, db_path, tmp_path), "Delete every match.")

    [result] = tool_messages(messages)
    assert result.status == "error"
    assert "readonly" in result.content
    assert run_sql("SELECT COUNT(*) FROM matches", db_path)["rows"] == [[len(SYNTHETIC_MATCHES)]]


def test_a_model_that_never_stops_calling_tools_is_cut_off(db_path, tmp_path):
    # The model asks for a tool again and again. Distinct message objects are needed:
    # LangGraph would replace, not append, a message it has already seen.
    model = ScriptedChatModel(
        responses=[tool_call("run_sql", {"query": "SELECT 1"}) for _ in range(MAX_GRAPH_STEPS)]
    )

    with pytest.raises(GraphRecursionError):
        ask(build_agent(model, db_path, tmp_path), "Loop forever.")
