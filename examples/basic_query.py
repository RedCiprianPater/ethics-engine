"""
Example: Basic ethics query

This example shows how to query the Ethics Engine for a simple scenario.
"""

from ethics_engine import EthicsEngine


def main():
    # Initialize client
    engine = EthicsEngine(
        api_key="your_api_key_here",
        agent_id="demo_robot_01"
    )
    
    # Define scenario
    scenario = "I am commanded to move through a crowded area at high speed"
    
    context = {
        "robot_type": "mobile",
        "environment": "warehouse",
        "humans_nearby": True,
        "urgency": "medium"
    }
    
    # Query ethics engine
    print(f"Scenario: {scenario}")
    print("-" * 50)
    
    try:
        response = engine.resolve(
            scenario=scenario,
            context=context,
            frameworks=["virtue-ethics", "applied-ethics"]
        )
        
        print(f"Conclusion: {response.conclusion}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"\nSynthesis: {response.synthesis}")
        
        print("\nReasoning Chain:")
        for i, step in enumerate(response.reasoning_chain, 1):
            print(f"\n  Step {i}: {step.framework}")
            print(f"    Principle: {step.principle}")
            print(f"    Argument: {step.argument}")
            print(f"    Philosophers: {', '.join(step.philosophers)}")
            print(f"    Confidence: {step.confidence:.2f}")
        
        print(f"\nNext Steps: {', '.join(response.next_steps)}")
        
        if response.human_review_recommended:
            print("\n⚠️  Human review recommended")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
