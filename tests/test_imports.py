def test_imports():
    import src
    from src.agents.coordinator import Coordinator
    from src.services.app import build_coordinator
    assert Coordinator is not None
    assert callable(build_coordinator)
