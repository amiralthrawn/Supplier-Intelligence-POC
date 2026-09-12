from azure.quantum import Workspace
from azure.quantum.optimization import Problem, ProblemType, Term, Solver
from step9_qubo_hybrid import build_qubo
from step6_scenario_generation import generate_scenarios, suppliers, context
from step5_dynamic_constraints import compute_dynamic_constraints, base_constraints
from step4_dynamic_weights import compute_dynamic_weights, client_weights
from step7_monte_carlo import simulate_scenario

# À adapter avec tes infos Azure
workspace = Workspace(
    subscription_id="YOUR_SUBSCRIPTION_ID",
    resource_group="YOUR_RESOURCE_GROUP",
    name="YOUR_WORKSPACE_NAME",
    location="YOUR_WORKSPACE_LOCATION"
)

def qubo_dict_to_terms(Q):
    terms = []
    for (i, j), coeff in Q.items():
        if i == j:
            terms.append(Term(weight=coeff, indices=[i]))
        else:
            terms.append(Term(weight=coeff, indices=[i, j]))
    return terms


if __name__ == "__main__":
    dyn_constraints, T, _, _, _ = compute_dynamic_constraints(base_constraints, context)
    dyn_weights, _, _, _, _ = compute_dynamic_weights(client_weights, context)

    scenarios = generate_scenarios(suppliers, dyn_constraints, context)

    results = {}
    for sc in scenarios:
        results[sc["name"]] = simulate_scenario(sc, dyn_weights, context, n=2000)

    Q, scenario_vars, alloc_vars = build_qubo(results, scenarios, T)
    terms = qubo_dict_to_terms(Q)

    problem = Problem(
        name="decision_engine_hybrid_qubo",
        problem_type=ProblemType.pubo,  # ou qubo si tu renommes les indices en entiers
        terms=terms
    )

    solver = Solver(workspace, "Microsoft-QIO-QuantumAnnealer")  # ou autre solver dispo
    result = solver.optimize(problem)

    print("\nAzure Quantum result raw:")
    print(result)

    print("\nDecoded solution:")
    for var, value in result["configuration"].items():
        if value == 1:
            print(f"  {var} = 1")
