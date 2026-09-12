# step15_classical_solver.py
# Solveur classique "complet" qui prend en compte expected, risque, confiance, tension

def compute_classical_score(result, T):
    """
    Calcule un score classique complet pour un scénario.
    result : dict avec expected_outcome, risk_failure, confidence
    T : tension du marché (contrainte dynamique)
    """
    expected = result["expected_outcome"]
    risk = result["risk_failure"]
    confidence = result["confidence"]

    # Ici, on construit un score global :
    # - plus l'expected est élevé, mieux c'est
    # - plus le risque est élevé, moins c'est bon
    # - plus la confiance est faible, moins c'est bon
    # - plus la tension T est élevée, plus on pénalise l'incertitude

    w_expected = 1.0
    w_risk = 1.0
    w_confidence = 1.0

    # On pénalise (1 - confidence) avec T
    tension_penalty = T * (1 - confidence)

    score = (
        w_expected * expected
        - w_risk * risk
        - w_confidence * tension_penalty
    )

    return score

def solve_classical(results):
    """
    Solveur classique : choisit le scénario avec la meilleure probabilité de succès.
    results : dict {scenario_name: result_dict}
    """
    best_name = None
    best_prob = -1.0

    for name, res in results.items():
        if res["prob_success"] > best_prob:
            best_prob = res["prob_success"]
            best_name = name

    return best_name, best_prob
