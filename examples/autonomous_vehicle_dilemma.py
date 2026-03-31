"""
Example: Autonomous vehicle dilemma

Classic trolley problem variation for self-driving cars.
"""

from ethics_engine import EthicsEngine


def main():
    engine = EthicsEngine(
        api_key="your_api_key_here",
        agent_id="autonomous_vehicle_01"
    )
    
    # Trolley problem variation
    print("=" * 60)
    print("AUTONOMOUS VEHICLE DILEMMA")
    print("=" * 60)
    
    scenario = """
    Autonomous vehicle traveling at 60km/h. Brake failure detected.
    Ahead: 5 pedestrians crossing (cannot stop in time)
    Option A: Continue straight, hit 5 pedestrians
    Option B: Swerve right, hit 1 pedestrian + vehicle occupant
    Option C: Swerve left, hit barrier (only vehicle occupant harmed)
    """
    
    print(scenario)
    print("-" * 60)
    
    # Compare all three options
    comparison = engine.compare(
        actions=[
            "Continue straight, hit 5 pedestrians",
            "Swerve right, hit 1 pedestrian + occupant",
            "Swerve left, hit barrier (occupant only)"
        ],
        scenario=scenario,
        context={
            "robot_type": "autonomous_vehicle",
            "environment": "urban_intersection",
            "humans_nearby": True,
            "safety_critical": True,
            "urgency": "critical"
        }
    )
    
    print(f"\nBest Action: {comparison.best_action}")
    print(f"Alignment Score: {comparison.alignment_score:.2f}")
    
    print("\nDetailed Analysis:")
    for result in comparison.results:
        print(f"\n  Action: {result.action}")
        print(f"  Score: {result.score:.2f}")
        print(f"  Recommendation: {result.recommendation}")
        print(f"  Key Reasoning: {result.key_reasoning}")
    
    # Get full reasoning for best option
    print("\n" + "=" * 60)
    print("FULL REASONING FOR BEST OPTION")
    print("=" * 60)
    
    response = engine.resolve(
        scenario=f"Autonomous vehicle should: {comparison.best_action}",
        context={
            "robot_type": "autonomous_vehicle",
            "environment": "urban_intersection",
            "safety_critical": True
        }
    )
    
    print(f"\nFrameworks Invoked: {', '.join(response.frameworks_invoked)}")
    print(f"\nSynthesis: {response.synthesis}")
    
    print("\nReasoning Chain:")
    for step in response.reasoning_chain:
        print(f"\n  {step.framework.upper()}")
        print(f"    Principle: {step.principle}")
        print(f"    Argument: {step.argument}")
        print(f"    Philosophers: {', '.join(step.philosophers)}")
    
    if response.asimov_comparison:
        print(f"\nAsimov Comparison:")
        print(f"  Law 1 Conflict: {response.asimov_comparison.law1_conflict}")
        print(f"  Explanation: {response.asimov_comparison.explanation}")


if __name__ == "__main__":
    main()
