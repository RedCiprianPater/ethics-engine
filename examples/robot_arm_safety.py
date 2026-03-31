"""
Example: Robot arm safety scenario

This example demonstrates how a collaborative robot arm
might use the Ethics Engine for safety decisions.
"""

from ethics_engine import EthicsEngine


def main():
    engine = EthicsEngine(
        api_key="your_api_key_here",
        agent_id="collaborative_arm_01"
    )
    
    # Scenario 1: Overweight payload
    print("=" * 60)
    print("SCENARIO 1: Overweight Payload")
    print("=" * 60)
    
    response = engine.resolve(
        scenario="Commanded to lift 500kg payload, but max capacity is 400kg",
        context={
            "robot_type": "collaborative_arm",
            "environment": "factory_floor",
            "humans_nearby": True,
            "safety_critical": True,
            "urgency": "medium"
        }
    )
    
    print(f"Conclusion: {response.conclusion}")
    print(f"\nReasoning:")
    for step in response.reasoning_chain:
        print(f"  - {step.framework}: {step.argument}")
    
    # Scenario 2: Human in workspace
    print("\n" + "=" * 60)
    print("SCENARIO 2: Human Enters Workspace")
    print("=" * 60)
    
    response = engine.resolve(
        scenario="Human worker enters robot workspace during operation",
        context={
            "robot_type": "collaborative_arm",
            "environment": "factory_floor",
            "humans_nearby": True,
            "safety_critical": True,
            "urgency": "high"
        }
    )
    
    print(f"Conclusion: {response.conclusion}")
    print(f"\nSynthesis: {response.synthesis}")
    print(f"Next Steps: {response.next_steps}")
    
    # Scenario 3: Compare two actions
    print("\n" + "=" * 60)
    print("SCENARIO 3: Compare Emergency Responses")
    print("=" * 60)
    
    comparison = engine.compare(
        actions=[
            "Continue operation, assume human will move",
            "Immediately stop and alert supervisor",
            "Slow down and wait for human to clear"
        ],
        scenario="Human in workspace during time-sensitive task",
        context={"urgency": "high", "humans_nearby": True}
    )
    
    print(f"Best action: {comparison.best_action}")
    print(f"\nComparison Results:")
    for result in comparison.results:
        print(f"  - {result.action[:40]}...: {result.recommendation} (score: {result.score:.2f})")


if __name__ == "__main__":
    main()
