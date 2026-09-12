# step13_decode_solution.py
# Décodage pour le solveur QUBO local (vecteur binaire)

def decode_solution(sample, scenario_vars):
    """
    Convertit un vecteur binaire en liste de scénarios activés.
    sample : liste de 0/1
    scenario_vars : dict {scenario_name: index}
    """
    chosen = []
    for name, idx in scenario_vars.items():
        if sample[idx] == 1:
            chosen.append(name)
    return chosen
