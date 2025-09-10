import pytest
from src.agents.coordinator import Coordinator

@pytest.fixture
def coordinator():
    return Coordinator()

@pytest.mark.parametrize("query", [
    "What are the main types of neural networks?",
    "Research transformer architectures, analyze their computational efficiency, and summarize key trade-offs.",
    "What did we discuss about neural networks earlier?",
    "Find recent papers on reinforcement learning, analyze their methodologies, and identify common challenges.",
    "Compare two machine-learning approaches and recommend which is better for our use case.",
])
def test_scenarios_run_without_errors(coordinator, query):
    ans = coordinator.handle(query)
    assert isinstance(ans, str)
    assert len(ans) > 0
