from step7_monte_carlo import simulate_scenario
from step6_scenario_generation import generate_scenarios, suppliers, context
from step5_dynamic_constraints import compute_dynamic_constraints, base_constraints
from step4_dynamic_weights import compute_dynamic_weights, client_weights

def compute_dynamic_objective_weights(T):
    w_E = 0.4 * (1 - T)
    w_S = 0.3 + 0.2 * T
    w_R = 0.2 + 0.3 * T
    w_C = 0.1 * (1 - T)
    return w_E, w_S, w_R, w_C


def optimize_scenarios(results, T):
    w_E, w_S, w_R, w_C = compute_dynamic_objective_weights(T)

    scored = []
    for name, r in results.items():
        score = (
            w_E * r["expected_outcome"] +
            w_S * r["prob_success"] -
            w_R * r["risk_failure"] +
            w_C * r["confidence"]
        )
        scored.append((name, score, r))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


if __name__ == "__main__":
    dyn_constraints, T, _, _, _ = compute_dynamic_constraints(base_constraints, context)
    dyn_weights, _, _, _, _ = compute_dynamic_weights(client_weights, context)

    scenarios = generate_scenarios(suppliers, dyn_constraints, context)

    results = {}
    for sc in scenarios:
        results[sc["name"]] = simulate_scenario(sc, dyn_weights, context, n=3000)

    ranked = optimize_scenarios(results, T)

    print("\nDynamic Optimization Results:\n")
    for name, score, r in ranked:
        print(f"{name:15} → Score: {score:.3f} | Expected: {r['expected_outcome']:.3f} | "
              f"Success: {r['prob_success']:.2f} | Risk: {r['risk_failure']:.3f} | "
              f"Confidence: {r['confidence']:.3f}")

    print("\nBest scenario:", ranked[0][0])
