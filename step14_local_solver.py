# step14_local_solver.py
# Solveur QUBO local 100% Python, sans dépendance externe.

import random
import math

def energy(sample, Q):
    """Calcule l'énergie du QUBO pour un vecteur binaire."""
    E = 0
    for (i, j), w in Q.items():
        E += w * sample[i] * sample[j]
    return E

def random_flip(sample):
    """Retourne un nouvel échantillon avec un bit retourné."""
    new = sample.copy()
    idx = random.randint(0, len(sample)-1)
    new[idx] = 1 - new[idx]
    return new

def solve_qubo_local(Q, num_reads=50, steps=2000, temp_start=5.0, temp_end=0.1):
   

    n = max(max(i, j) for (i, j) in Q.keys()) + 1
    best_sample = None
    best_energy = float("inf")

    for _ in range(num_reads):
        # Échantillon initial aléatoire
        sample = [random.randint(0, 1) for _ in range(n)]
        E = energy(sample, Q)

        for step in range(steps):
            T = temp_start + (temp_end - temp_start) * (step / steps)
            new_sample = random_flip(sample)
            new_E = energy(new_sample, Q)

            if new_E < E or random.random() < math.exp((E - new_E) / T):
                sample, E = new_sample, new_E

        if E < best_energy:
            best_energy = E
            best_sample = sample

    return best_sample, best_energy
