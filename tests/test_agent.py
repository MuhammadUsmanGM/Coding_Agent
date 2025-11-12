"""
Basic tests for the coding agent
"""
import pytest
from coding_agent.agent import CodingAgent


def test_agent_initialization():
    """Test that the agent initializes properly with providers"""
    agent = CodingAgent()
    assert agent.providers is not None
    assert len(agent.providers) >= 1  # Should have at least one provider
    assert agent.history == []


def test_system_prompt():
    """Test that system prompt is returned properly"""
    agent = CodingAgent()
    prompt = agent.system_prompt()
    assert "You are an advanced AI coding agent" in prompt
    assert "read_file" in prompt
    assert "write_file" in prompt
    assert "git_commit" in prompt
    assert "web_search" in prompt


def test_get_available_models():
    """Test model listing functionality"""
    agent = CodingAgent()
    models = agent.get_available_models()
    assert isinstance(models, dict)
    assert len(models) >= 1  # Should have at least one model


if __name__ == "__main__":
    pytest.main()