# Tests for Ethics Engine

import pytest
from ethics_engine import EthicsEngine
from ethics_engine.schemas import EthicsRequest, ScenarioContext
from ethics_engine.exceptions import AuthenticationError


class TestEthicsEngine:
    """Test the EthicsEngine client."""
    
    def test_client_initialization(self):
        """Test client can be initialized."""
        engine = EthicsEngine(
            api_key="test_key",
            agent_id="test_agent"
        )
        assert engine.api_key == "test_key"
        assert engine.agent_id == "test_agent"
    
    def test_request_schema(self):
        """Test request schema validation."""
        request = EthicsRequest(
            scenario="Test scenario",
            context=ScenarioContext(environment="test"),
            frameworks=["virtue-ethics"]
        )
        assert request.scenario == "Test scenario"
        assert request.context.environment == "test"


class TestSchemas:
    """Test Pydantic schemas."""
    
    def test_scenario_context_defaults(self):
        """Test scenario context default values."""
        context = ScenarioContext()
        assert context.urgency == "medium"
        assert context.humans_nearby == False
        assert context.safety_critical == False
    
    def test_ethics_request_validation(self):
        """Test ethics request validation."""
        request = EthicsRequest(scenario="Test")
        assert request.return_reasoning == True
        assert request.mode == "reasoning"


class TestExceptions:
    """Test custom exceptions."""
    
    def test_authentication_error(self):
        """Test authentication error."""
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("Invalid key")


# API Tests (would require running server)
class TestAPI:
    """Test API endpoints (requires server)."""
    
    @pytest.mark.skip(reason="Requires running server")
    def test_health_endpoint(self):
        """Test health check endpoint."""
        import httpx
        response = httpx.get("http://localhost:8000/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @pytest.mark.skip(reason="Requires running server")
    def test_frameworks_endpoint(self):
        """Test frameworks list endpoint."""
        import httpx
        response = httpx.get("http://localhost:8000/frameworks")
        assert response.status_code == 200
        assert "frameworks" in response.json()
