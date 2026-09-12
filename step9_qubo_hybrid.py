from step8_optimization import compute_dynamic_objective_weights
from step7_monte_carlo import simulate_scenario
from step6_scenario_generation import generate_scenarios, suppliers, context
from step5_dynamic_constraints import compute_dynamic_constraints, base_constraints
from step4_dynamic_weights import compute_dynamic_weights, client_weights

# niveaux d'allocation possibles
levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

def build_qubo(results, scenarios, T):
    Q = {}

    # pondérations dynamiques
    wE, wS, wR, wC = compute_dynamic_objective_weights(T)

    # -------------------------
    # 1. Variables binaires
    # -------------------------
    scenario_vars = {sc["name"]: f"x_s_{sc['name']}" for sc in scenarios}
    alloc_vars = {
        supplier: {lvl: f"x_{supplier}_{lvl}" for lvl in levels}
        for supplier in suppliers
    }

    # -------------------------
    # 2. Fonction objectif
    # -------------------------
    for sc_name, var in scenario_vars.items():
        r = results[sc_name]
        score = (
            wE * r["expected_outcome"] +
            wS * r["prob_success"] -
            wR * r["risk_failure"] +
            wC * r["confidence"]
        )
        Q[(var, var)] = -score

    # -------------------------
    # 3. Pénalité : un seul scénario
    # -------------------------
    lambda_s = 5.0
    scen_list = list(scenario_vars.values())

    for v in scen_list:
        Q[(v, v)] = Q.get((v, v), 0) + lambda_s

    for i in range(len(scen_list)):
        for j in range(i + 1, len(scen_list)):
            Q[(scen_list[i], scen_list[j])] = Q.get((scen_list[i], scen_list[j]), 0) + 2 * lambda_s

    # -------------------------
    # 4. Pénalité : une seule allocation par fournisseur
    # -------------------------
    lambda_alloc = 5.0

    for supplier in alloc_vars:
        vars_list = list(alloc_vars[supplier].values())

        for v in vars_list:
            Q[(v, v)] = Q.get((v, v), 0) + lambda_alloc

        for i in range(len(vars_list)):
            for j in range(i + 1, len(vars_list)):
                Q[(vars_list[i], vars_list[j])] = Q.get((vars_list[i], vars_list[j]), 0) + 2 * lambda_alloc

    # -------------------------
    # 5. Pénalité : somme allocations = 1
    # -------------------------
    lambda_sum = 10.0

    for supplier in alloc_vars:
        for lvl, var in alloc_vars[supplier].items():
            Q[(var, var)] = Q.get((var, var), 0) + lambda_sum * (lvl ** 2)

    for supplier1 in alloc_vars:
        for lvl1, var1 in alloc_vars[supplier1].items():
            for supplier2 in alloc_vars:
                for lvl2, var2 in alloc_vars[supplier2].items():
                    if var1 != var2:
                        Q[(var1, var2)] = Q.get((var1, var2), 0) + 2 * lambda_sum * lvl1 * lvl2

    return Q, scenario_vars, alloc_vars


if __name__ == "__main__":
    dyn_constraints, T, _, _, _ = compute_dynamic_constraints(base_constraints, context)
    dyn_weights, _, _, _, _ = compute_dynamic_weights(client_weights, context)

    scenarios = generate_scenarios(suppliers, dyn_constraints, context)

    results = {}
    for sc in scenarios:
        results[sc["name"]] = simulate_scenario(sc, dyn_weights, context, n=3000)

    Q, scenario_vars, alloc_vars = build_qubo(results, scenarios, T)

    print("\nQUBO Hybrid built successfully.")
    print(f"Total terms: {len(Q)}")
