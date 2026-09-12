from step5_dynamic_constraints import compute_dynamic_constraints, base_constraints, context
from step4_dynamic_weights import compute_dynamic_weights, client_weights

# Fournisseurs (simplifiés pour la génération)
suppliers = {
    "A": {"delivery_days": 20},
    "B": {"delivery_days": 10},
    "C": {"delivery_days": 30}
}

def generate_scenarios(suppliers, dyn_constraints, ctx):
    scenarios = []

    # --- 1. Scénarios simples ---
    for s in suppliers.keys():
        scenarios.append({
            "name": f"{s}_solo",
            "allocation": {s: 1.0},
            "type": "single_supplier",
            "reason": "simple baseline scenario"
        })

    # --- 2. Diversification ---
    min_div = dyn_constraints["min_diversification"]
    if min_div > 0:
        for s1 in suppliers.keys():
            for s2 in suppliers.keys():
                if s1 != s2:
                    scenarios.append({
                        "name": f"{s1}_{s2}_80_20",
                        "allocation": {s1: 0.8, s2: 0.2},
                        "type": "diversification",
                        "reason": "reduce dependency and improve resilience"
                    })
                    scenarios.append({
                        "name": f"{s1}_{s2}_60_40",
                        "allocation": {s1: 0.6, s2: 0.4},
                        "type": "diversification",
                        "reason": "strong diversification scenario"
                    })

    # --- 3. Réduction de dépendance ---
    if ctx["supplier_dependency_A"] > 0.60:
        scenarios.append({
            "name": "reduce_A_20",
            "allocation": {"A": 0.8},
            "type": "dependency_reduction",
            "reason": "reduce dependency on A by 20%"
        })
        scenarios.append({
            "name": "reduce_A_40",
            "allocation": {"A": 0.6},
            "type": "dependency_reduction",
            "reason": "reduce dependency on A by 40%"
        })

    # --- 4. Sécurisation ---
    if ctx["stock_coverage_days"] < dyn_constraints["min_stock_coverage_days"]:
        for s in suppliers.keys():
            if suppliers[s]["delivery_days"] <= dyn_constraints["max_delivery_days"]:
                scenarios.append({
                    "name": f"secure_{s}",
                    "allocation": {s: 0.3},
                    "type": "security",
                    "reason": "secure supply due to low stock coverage"
                })

    # --- 5. Attente ---
    if ctx["stock_coverage_days"] > dyn_constraints["min_stock_coverage_days"]:
        scenarios.append({
            "name": "wait",
            "allocation": {},
            "type": "wait",
            "reason": "stock coverage allows waiting"
        })

    # --- 6. Négociation ---
    scenarios.append({
        "name": "negotiate_A",
        "allocation": {},
        "type": "negotiation",
        "reason": "market tension suggests negotiation with A"
    })

    return scenarios


if __name__ == "__main__":
    dyn_constraints, T, ts, tm, td = compute_dynamic_constraints(base_constraints, context)
    dyn_weights, _, _, _, _ = compute_dynamic_weights(client_weights, context)

    scenarios = generate_scenarios(suppliers, dyn_constraints, context)

    print("\nScénarios générés :\n")
    for sc in scenarios:
        print(f"- {sc['name']} ({sc['type']}) → {sc['reason']}")
