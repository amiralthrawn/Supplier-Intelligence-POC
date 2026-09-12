from step6_scenario_generation import generate_scenarios, suppliers, context
from step7_monte_carlo import simulate_scenario
from step4_dynamic_weights import compute_dynamic_weights, client_weights
from step5_dynamic_constraints import compute_dynamic_constraints, base_constraints
from step12_qubo_build import build_qubo
from step14_local_solver import solve_qubo_local
from step15_classical_solver import solve_classical
from step16_comparaison import compare_classical_vs_qubo

# 1. Contraintes dynamiques
dyn_constraints, T, _, _, _ = compute_dynamic_constraints(base_constraints, context)

# 2. Pondérations dynamiques
dyn_weights, _, _, _, _ = compute_dynamic_weights(client_weights, context)

# 3. Scénarios
scenarios = generate_scenarios(suppliers, dyn_constraints, context)

# 4. Monte Carlo → SPECTRE DES SCÉNARIOS
results = {}
for sc in scenarios:
    results[sc["name"]] = simulate_scenario(sc, dyn_weights, context, n=2000)

print("\n--- SPECTRE DES SCÉNARIOS ---")
for name, res in results.items():
    print(f"Scénario : {name}")
    print(f"  - Probabilité de succès : {res['prob_success']*100:.2f} %")
    print(f"  - Risque d'échec       : {res['risk_failure']*100:.2f} %")
    print(f"  - Stabilité            : {res['stability']*100:.2f} %")
    print(f"  - Coût moyen simulé    : {res['avg_cost']:.3f}")
    print(f"  - Délai moyen simulé   : {res['avg_delivery']:.3f}")
    print(f"  - Qualité moyenne      : {res['avg_quality']:.3f}")
    print(f"  - Performance          : {res['performance']:.6f}")
    print()

# 5. Solveur classique
classical_choice, classical_prob = solve_classical(results)

print("\n--- SOLVEUR CLASSIQUE COMPLET ---")
print("Scénario choisi (classique) :", classical_choice)
print(f"Probabilité de succès (classique) : {classical_prob*100:.2f} %")

# 6. QUBO
Q, scenario_vars, alloc_vars = build_qubo(results, scenarios, T)
sample, E = solve_qubo_local(Q)

def decode_solution_local(sample, scenario_vars):
    return [name for name, idx in scenario_vars.items() if sample[idx] == 1]

qubo_choice = decode_solution_local(sample, scenario_vars)
qubo_prob = results[qubo_choice[0]]["prob_success"]

print("\n--- SOLVEUR QUBO ---")
print("Scénario choisi (QUBO) :", qubo_choice)
print(f"Probabilité de succès (QUBO) : {qubo_prob*100:.2f} %")
print("Énergie QUBO :", E)

# 7. Comparaison détaillée
comparison = compare_classical_vs_qubo(results, scenarios, T)

print("\n--- COMPARAISON CLASSIQUE VS QUBO ---")
print("Choix classique :", comparison["classical"])
print(f"  - Probabilité de succès : {comparison['classical_prob_success']*100:.2f} %")
print(f"  - Risque d'échec        : {comparison['classical_risk_failure']*100:.2f} %")
print(f"  - Stabilité             : {comparison['classical_stability']*100:.2f} %")
print(f"  - Performance           : {comparison['classical_performance']:.6f}")

print("Choix QUBO :", comparison["qubo"])
print(f"  - Probabilité de succès : {comparison['qubo_prob_success']*100:.2f} %")
print(f"  - Risque d'échec        : {comparison['qubo_risk_failure']*100:.2f} %")
print(f"  - Stabilité             : {comparison['qubo_stability']*100:.2f} %")
print(f"  - Performance           : {comparison['qubo_performance']:.6f}")
print("  - Énergie QUBO          :", comparison["qubo_energy"])
