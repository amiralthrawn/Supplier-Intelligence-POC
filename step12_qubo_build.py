# step12_qubo_build.py
# Construction du QUBO complet (local solver compatible)

def build_qubo(results, scenarios, T):
    """
    Construit le QUBO pour le solveur local.
    results : dict des résultats Monte Carlo
    scenarios : liste des scénarios
    T : contrainte dynamique (budget, tension, etc.)
    """

    Q = {}
    scenario_vars = {}
    alloc_vars = {}

    # --- 1. Variables de scénario ---
    idx = 0
    for sc in scenarios:
        scenario_vars[sc["name"]] = idx
        idx += 1

    # --- 2. Variables d'allocation (si présentes) ---
    for sc in scenarios:
        if "alloc" in sc:
            for alloc_name, alloc_value in sc["alloc"].items():
                alloc_vars[(sc["name"], alloc_name)] = idx
                idx += 1

    # --- 3. Objectif : expected outcome, risk, tension ---
    for sc in scenarios:
        name = sc["name"]
        i = scenario_vars[name]

        expected = results[name]["expected_outcome"]
        risk = results[name]["risk_failure"]
        tension = 1 - results[name]["confidence"]   # plus la variance est forte, plus la tension est forte

        # pondérations simples
        w_expected = 1.0
        w_risk = 1.0
        w_tension = 1.0

        score = w_expected * expected - w_risk * risk - w_tension * tension

        Q[(i, i)] = Q.get((i, i), 0) - score

    # --- 4. Contrainte : un seul scénario doit être choisi ---
    lambda_scenario = 50  # pénalité forte

    # pénalité quadratique : interdit plusieurs scénarios
    for name_i, idx_i in scenario_vars.items():
        for name_j, idx_j in scenario_vars.items():
            if idx_i != idx_j:
                Q[(idx_i, idx_j)] = Q.get((idx_i, idx_j), 0) + lambda_scenario

    # pénalité linéaire : encourage un seul scénario
    for name, idx_i in scenario_vars.items():
        Q[(idx_i, idx_i)] = Q.get((idx_i, idx_i), 0) - lambda_scenario

    # --- 5. Contrainte d'allocation (si présente) ---
    lambda_alloc = 10

    for sc in scenarios:
        name = sc["name"]
        if "alloc" in sc:
            for alloc_name, alloc_value in sc["alloc"].items():
                i = scenario_vars[name]
                j = alloc_vars[(name, alloc_name)]

                # allocation doit être active si scénario actif
                Q[(i, j)] = Q.get((i, j), 0) - lambda_alloc
                Q[(j, j)] = Q.get((j, j), 0) - lambda_alloc

    return Q, scenario_vars, alloc_vars
