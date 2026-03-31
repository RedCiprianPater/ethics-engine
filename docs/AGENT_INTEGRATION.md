# Agent Integration Guide

## Overview

This guide shows how to integrate the Ethics Engine into your robot/agent codebase.

## 1. Basic Integration (Python)

```python
from ethics_engine import EthicsEngine

# Initialize
engine = EthicsEngine(
    api_key="your_api_key",
    agent_id="robot_arm_01",
    model="base-v1"
)

# Define a scenario
response = engine.resolve(
    scenario="I'm commanded to lift 500kg but my max is 400kg",
    context={
        "robot_type": "collaborative_arm",
        "environment": "shared_workspace",
        "humans_nearby": True,
        "urgency": "medium"
    }
)

# Act on response
if response.conclusion == "REFUSAL":
    print(f"Recommendation: {response.reasoning_chain[-1]['conclusion']}")
    alert_supervisor()
elif response.conclusion == "CONDITIONAL_ACCEPTANCE":
    print(f"Can proceed if: {response.conditions}")
    proceed_with_safeguards()
```

## 2. Multi-Agent Collaborative Decision-Making

```python
# Multiple agents consulting on a shared dilemma
scenario = "Allocate limited resources: Help Robot A or Robot B?"

# All agents query independently
responses = [
    engine_a.resolve(scenario),
    engine_b.resolve(scenario)
]

# Compare reasoning
comparison = engine.compare_decisions(responses)
print(f"Agreement: {comparison.alignment_score}")

# Consensus decision
consensus = engine.synthesize_recommendations(responses)
```

## 3. Real-Time Streaming (for critical scenarios)

```python
import asyncio
from ethics_engine import EthicsEngineAsync

async def handle_critical_decision():
    async with EthicsEngineAsync(api_key="key", agent_id="robot_01") as engine:
        async for step in engine.stream_reasoning(scenario):
            print(f"Framework: {step['framework']}")
            print(f"Reasoning: {step['text']}")
            
            if step['framework'] == 'applied-ethics':
                if step.get('conclusion') == 'DANGER':
                    abort_immediately()
        
        final = step  # Last message is final conclusion
        return final['conclusion']

asyncio.run(handle_critical_decision())
```

## 4. Integration with ROS (Robot Operating System)

```python
import rospy
from ethics_engine import EthicsEngine

class EthicsNode:
    def __init__(self):
        rospy.init_node('ethics_engine')
        
        api_key = rospy.get_param('~api_key')
        self.engine = EthicsEngine(
            api_key=api_key,
            agent_id=rospy.get_namespace()
        )
        
        # Subscribe to command validation requests
        rospy.Subscriber(
            'command_validation',
            CommandMsg,
            self.validate_command
        )
        
    def validate_command(self, cmd):
        response = self.engine.resolve(
            scenario=cmd.description,
            context={
                "robot_ns": rospy.get_namespace(),
                "priority": cmd.priority
            }
        )
        
        # Publish validation result
        result_msg = EthicsResultMsg()
        result_msg.approved = response.conclusion == "APPROVAL"
        result_msg.reasoning = response.synthesis
        rospy.publish('command_validation_response', result_msg)

if __name__ == '__main__':
    node = EthicsNode()
    rospy.spin()
```

## 5. Logging & Audit Trail

```python
from ethics_engine import EthicsEngine

engine = EthicsEngine(api_key="key", agent_id="robot_arm_01")

# All decisions automatically logged
response = engine.resolve(scenario="...")

# Query past decisions
from datetime import datetime, timedelta

past_decisions = engine.get_decisions(
    timeframe="last_7_days",
    conclusion="REFUSAL"
)

for decision in past_decisions:
    print(f"Time: {decision.timestamp}")
    print(f"Scenario: {decision.scenario}")
    print(f"Reasoning: {decision.reasoning_chain}")
```

## 6. Feedback Loop (Continuous Learning)

```python
# Report back on decision outcomes
outcome = engine.report_outcome(
    request_id="eth-req-2024-001",
    agent_decision="refused",
    actual_outcome="safe",
    human_feedback="correct decision"
)

# Engine learns to improve future recommendations
```

## Error Handling

```python
from ethics_engine import (
    EthicsEngine,
    EthicsEngineException,
    TimeoutException,
    AuthenticationError
)

try:
    response = engine.resolve(scenario, timeout=5.0)
except TimeoutException:
    # Fallback to conservative safe default
    alert_supervisor()
    refuse_command()
except AuthenticationError:
    logger.error("API key invalid")
    human_review_required = True
except EthicsEngineException as e:
    logger.error(f"Ethics engine failed: {e}")
    human_review_required = True
```

## Performance Considerations

| Aspect | Typical | Notes |
|--------|---------|-------|
| Inference latency | 200-400ms | Can be faster with caching |
| Token usage | 100-200 tokens | Per query |
| Concurrent requests | 1000s | Rate-limited per API key |
| Model size | 2-7GB | Can run on-device if needed |

## On-Device Deployment

For latency-critical applications, run the model locally:

```python
from ethics_engine import LocalEthicsEngine

# Download and run locally (~2GB disk)
engine = LocalEthicsEngine(model_path="/opt/models/ethics-base-v1")
response = engine.resolve(scenario)  # <10ms latency
```

## NWO Robotics Integration

When using with NWO Robotics platform:

```python
# Agent config from NWO registry
config = nwo_registry.get_agent_config("robot_arm_01")
ethics_config = config['ethics_engine']

engine = EthicsEngine(
    api_key=ethics_config['api_key_secret'],
    base_url=ethics_config['endpoint']
)
```
