# step16_comparaison.py

from step15_classical_solver import solve_classical
from step12_qubo_build import build_qubo
from step14_local_solver import solve_qubo_local


def compare_classical_vs_qubo(results, scenarios, T):
    """
    Compare solveur classique vs QUBO sur des métriques métier.
    """

    # 1. Solveur classique
    classical_choice, classical_prob = solve_classical(results)
    classical_metrics = results[classical_choice]

    # 2. QUBO
    Q, scenario_vars, alloc_vars = build_qubo(results, scenarios, T)
    sample, E = solve_qubo_local(Q)

    qubo_choice = [name for name, idx in scenario_vars.items() if sample[idx] == 1]

    if len(qubo_choice) == 1:
        qc = qubo_choice[0]
        qubo_metrics = results[qc]
    else:
        qc = None
        qubo_metrics = None

    return {
        "classical": classical_choice,
        "classical_prob_success": classical_metrics["prob_success"],
        "classical_risk_failure": classical_metrics["risk_failure"],
        "classical_stability": classical_metrics["stability"],
        "classical_performance": classical_metrics["performance"],
        "qubo": qubo_choice,
        "qubo_prob_success": qubo_metrics["prob_success"] if qubo_metrics else None,
        "qubo_risk_failure": qubo_metrics["risk_failure"] if qubo_metrics else None,
        "qubo_stability": qubo_metrics["stability"] if qubo_metrics else None,
        "qubo_performance": qubo_metrics["performance"] if qubo_metrics else None,
        "qubo_energy": E
    }
