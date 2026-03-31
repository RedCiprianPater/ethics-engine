# API Tests for Ethics Engine

import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys
sys.path.insert(0, '/root/.openclaw/workspace/ethics-engine/src')

from ethics_engine.api.app import app


client = TestClient(app)


class TestHealth:
    """Test health endpoints."""
    
    def test_health_check(self):
        """Test health check returns healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestFrameworks:
    """Test framework endpoints."""
    
    def test_list_frameworks(self):
        """Test listing available frameworks."""
        response = client.get("/frameworks")
        assert response.status_code == 200
        data = response.json()
        assert "frameworks" in data
        assert len(data["frameworks"]) > 0
    
    def test_framework_structure(self):
        """Test framework response structure."""
        response = client.get("/frameworks")
        data = response.json()
        framework = data["frameworks"][0]
        assert "id" in framework
        assert "name" in framework
        assert "philosophers" in framework


class TestResolve:
    """Test resolve endpoint."""
    
    def test_resolve_unauthorized(self):
        """Test resolve without auth fails."""
        response = client.post("/resolve", json={
            "scenario": "Test scenario"
        })
        assert response.status_code == 403  # Missing headers
    
    def test_resolve_with_auth(self):
        """Test resolve with proper auth."""
        response = client.post(
            "/resolve",
            headers={
                "Authorization": "Bearer test_key",
                "X-Agent-ID": "test_agent"
            },
            json={
                "scenario": "Should I refuse an unsafe command?",
                "context": {
                    "environment": "factory",
                    "urgency": "high"
                }
            }
        )
        # Should succeed (mock response)
        assert response.status_code == 200
        data = response.json()
        assert "conclusion" in data
        assert "reasoning_chain" in data


class TestCompare:
    """Test compare endpoint."""
    
    def test_compare_actions(self):
        """Test comparing multiple actions."""
        response = client.post(
            "/compare",
            headers={
                "Authorization": "Bearer test_key",
                "X-Agent-ID": "test_agent"
            },
            json={
                "actions": ["Action A", "Action B"],
                "scenario": "Test scenario"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "best_action" in data
