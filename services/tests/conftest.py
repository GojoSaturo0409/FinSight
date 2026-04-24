import pytest
import os
import sys

# Ensure services directory is in PYTHONPATH so shared.models works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session")
def setup_test_db():
    """Setup an in-memory SQLite DB for tests."""
    os.environ["DATABASE_URL"] = "sqlite:///test_temp.db"
    yield
    if os.path.exists("test_temp.db"):
        os.remove("test_temp.db")
