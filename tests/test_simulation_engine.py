from src.ww2ops.services.simulation_engine import SimulationEngine, SimulationInputs


def test_simulation_engine_is_deterministic_for_same_seed():
    engine = SimulationEngine()
    inputs = SimulationInputs(
        seed=12345,
        turn_number=2,
        decision_type="resource_allocation",
        decision_data={"amount": 1200, "resource": "oil", "target": "production"},
        baseline={"morale": 60, "resource_index": 58, "leadership_index": 63, "intelligence_index": 61},
    )
    first = engine.evaluate(inputs)
    second = engine.evaluate(inputs)
    assert first == second


def test_simulation_engine_returns_probability_and_impact():
    engine = SimulationEngine()
    result = engine.evaluate(
        SimulationInputs(
            seed=9876,
            turn_number=1,
            decision_type="military_action",
            decision_data={"forces": 8000, "location": "Normandy", "operation_type": "offensive"},
            baseline={"morale": 62, "resource_index": 61, "leadership_index": 70, "intelligence_index": 66},
        )
    )
    assert 0.05 <= result["probability"] <= 0.95
    assert "message" in result
    assert "casualties" in result
