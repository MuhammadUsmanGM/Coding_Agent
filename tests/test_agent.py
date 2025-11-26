"""
Basic tests for the coding agent
"""
import pytest
from codeius.core.agent import CodingAgent



def test_agent_initialization():
    """Test that the agent initializes properly with providers"""
    agent = CodingAgent()
    assert agent.providers is not None
    assert len(agent.providers) >= 1  # Should have at least one provider
    assert agent.conversation_manager.history == []


def test_system_prompt():
    """Test that system prompt is returned properly"""
    agent = CodingAgent()
    prompt = agent.system_prompt()
    assert "Codeius AI Agent Instructions" in prompt
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


def test_run_test_command_not_found(capsys):
    """Test the /run_test command with a file that does not exist"""
    from codeius.cli import run_test
    run_test("non_existent_file.py")
    captured = capsys.readouterr()
    assert "Test file not found" in captured.out


def test_run_all_tests_command(capsys):
    """Test the /test command"""
    from codeius.cli import run_all_tests
    run_all_tests()
    captured = capsys.readouterr()
    assert "Running all tests" in captured.out
    assert "Test Results" in captured.out

if __name__ == "__main__":
    pytest.main()