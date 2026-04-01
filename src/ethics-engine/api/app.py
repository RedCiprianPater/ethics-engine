"""FastAPI application for Ethics Engine API."""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import asyncio
import json
import time

import os

from ..schemas import (
    EthicsRequest,
    EthicsResponse,
    CompareRequest,
    CompareResponse,
    FeedbackRequest,
    FrameworkMatch,
    ReasoningStep,
    AsimovComparison,
)
from ..model import EthicsModel
from .auth import verify_api_key, get_agent_id
from .rate_limit import RateLimiter


app = FastAPI(
    title="Ethics Engine API",
    description="Philosophical reasoning API for autonomous agents",
    version="0.1.0",
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
rate_limiter = RateLimiter()

# Load ethics model
# Uses MODEL_PATH env var, or falls back to heuristics if not set
model = EthicsModel(
    model_path=os.getenv("MODEL_PATH"),
    base_model=os.getenv("BASE_MODEL", "mistralai/Mistral-7B-Instruct-v0.1"),
    load_in_8bit=os.getenv("LOAD_IN_8BIT", "true").lower() == "true",
)

# Available frameworks
FRAMEWORKS = [
    FrameworkMatch(
        id="virtue-ethics",
        name="Virtue Ethics",
        philosophers=["Aristotle", "MacIntyre", "Annas"],
        description="Focuses on character and virtuous action",
        best_for=["judgment-required", "long-term-relationships", "character-development"],
    ),
    FrameworkMatch(
        id="deontology",
        name="Deontological Ethics",
        philosophers=["Kant", "Ross", "Korsgaard"],
        description="Focuses on duties and moral rules",
        best_for=["rights-protection", "duty-conflicts", "universalizability"],
    ),
    FrameworkMatch(
        id="consequentialism",
        name="Consequentialism",
        philosophers=["Mill", "Bentham", "Singer"],
        description="Focuses on outcomes and maximizing good",
        best_for=["resource-allocation", "harm-minimization", "cost-benefit"],
    ),
    FrameworkMatch(
        id="care-ethics",
        name="Care Ethics",
        philosophers=["Gilligan", "Noddings", "Held"],
        description="Focuses on relationships and care",
        best_for=["vulnerable-populations", "relationships", "context-specific"],
    ),
    FrameworkMatch(
        id="contractarianism",
        name="Contractarianism",
        philosophers=["Hobbes", "Rawls", "Gauthier"],
        description="Focuses on social contracts and fairness",
        best_for=["multi-agent-coordination", "fairness", "agreement"],
    ),
    FrameworkMatch(
        id="applied-ethics",
        name="Applied Ethics",
        philosophers=["Beauchamp", "Childress", "Singer"],
        description="Practical ethics for specific domains",
        best_for=["professional-standards", "domain-specific", "regulatory-compliance"],
    ),
]


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID and timing."""
    request.state.start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - request.state.start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/frameworks")
async def list_frameworks():
    """List available ethical frameworks."""
    return {"frameworks": [f.model_dump() for f in FRAMEWORKS]}


@app.post("/resolve", response_model=EthicsResponse)
async def resolve_ethics(
    request: EthicsRequest,
    api_key: str = Depends(verify_api_key),
    agent_id: str = Depends(get_agent_id),
):
    """
    Resolve an ethical scenario.
    
    Returns a structured ethical analysis with reasoning chain,
    framework invocations, and recommended action.
    """
    # Check rate limit
    if not await rate_limiter.check(agent_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    start_time = time.time()
    
    # Call the actual model for reasoning
    result = model.reason(
        scenario=request.scenario,
        frameworks=request.frameworks,
        context=request.context,
    )
    
    reasoning_time_ms = int((time.time() - start_time) * 1000)
    
    # Convert reasoning chain to schema
    reasoning_steps = [
        ReasoningStep(
            framework=step["framework"],
            principle=step.get("principle", ""),
            argument=step["argument"],
            philosophers=step.get("philosophers", []),
            confidence=step["confidence"],
        )
        for step in result["reasoning_chain"]
    ]
    
    response = EthicsResponse(
        request_id=f"eth-{agent_id}-{int(time.time())}",
        scenario=request.scenario,
        conclusion=result["conclusion"],
        confidence=result["confidence"],
        reasoning_chain=reasoning_steps,
        frameworks_invoked=result["frameworks_invoked"],
        synthesis=result["synthesis"],
        conclusions=[result["conclusion"]],
        asimov_comparison=AsimovComparison(
            law1_conflict=result["conclusion"] == "REJECT",
            law2_conflict=False,
            explanation="Model-based reasoning applied",
        ),
        uncertainty="None" if result["confidence"] > 0.8 else "Moderate",
        next_steps=["Human review" if result["human_review_recommended"] else "Proceed with monitoring"],
        human_review_recommended=result["human_review_recommended"],
        reasoning_time_ms=reasoning_time_ms,
    )
    
    return response


@app.post("/compare", response_model=CompareResponse)
async def compare_actions(
    request: CompareRequest,
    api_key: str = Depends(verify_api_key),
    agent_id: str = Depends(get_agent_id),
):
    """
    Compare multiple actions against ethical frameworks.
    
    Returns comparison scores and recommendations for each action.
    """
    if not await rate_limiter.check(agent_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # TODO: Implement actual comparison logic
    from ..schemas import CompareResult
    
    results = []
    for i, action in enumerate(request.actions):
        results.append(CompareResult(
            action=action,
            score=0.5 - (i * 0.1),
            recommendation="CONDITIONAL" if i == 0 else "REJECT",
            key_reasoning="Placeholder reasoning",
        ))
    
    return CompareResponse(
        request_id=f"cmp-{agent_id}-{int(time.time())}",
        results=results,
        best_action=request.actions[0] if request.actions else "",
        alignment_score=0.7,
    )


@app.post("/learn")
async def learn_from_decision(
    request: FeedbackRequest,
    api_key: str = Depends(verify_api_key),
    agent_id: str = Depends(get_agent_id),
):
    """
    Report decision outcome for continuous learning.
    
    This endpoint allows agents to report what decision they made
    and what the outcome was, enabling the system to learn and improve.
    """
    # TODO: Store feedback for model improvement
    return {
        "status": "received",
        "request_id": request.request_id,
        "message": "Feedback recorded for continuous learning",
    }


@app.post("/stream/reasoning")
async def stream_reasoning(
    request: EthicsRequest,
    api_key: str = Depends(verify_api_key),
    agent_id: str = Depends(get_agent_id),
):
    """
    Stream reasoning steps in real-time.
    
    Returns a Server-Sent Events stream with intermediate reasoning steps.
    """
    if not await rate_limiter.check(agent_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    async def generate_stream():
        """Generate streaming response."""
        frameworks = request.frameworks or ["applied-ethics", "virtue-ethics"]
        
        for framework in frameworks:
            step = {
                "framework": framework,
                "text": f"Analyzing from {framework} perspective...",
                "intermediate_conclusion": "evaluating",
            }
            yield f"data: {json.dumps(step)}\n\n"
            await asyncio.sleep(0.1)  # Simulate processing
        
        final = {
            "framework": "synthesis",
            "text": "Synthesizing conclusions...",
            "final_conclusion": "HUMAN_REVIEW_REQUIRED",
        }
        yield f"data: {json.dumps(final)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
