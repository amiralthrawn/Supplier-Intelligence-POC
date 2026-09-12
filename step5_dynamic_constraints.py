from step4_dynamic_weights import compute_tension_index, context

base_constraints = {
    "min_diversification": 0.0,
    "max_delivery_days": 30,
    "min_stock_coverage_days": 15
}

def compute_dynamic_constraints(base, ctx):
    # On récupère la tension globale T
    T, ts, tm, td = compute_tension_index(ctx)

    # Diversification minimale
    min_div = base["min_diversification"] + 0.3 * T

    # Règle : si dépendance > 60 %, diversification min >= 20 %
    if ctx["supplier_dependency_A"] > 0.60:
        min_div = max(min_div, 0.20)

    # Délai maximum acceptable
    max_delivery = base["max_delivery_days"] - 20 * T

    # Règles supplémentaires
    if ctx["stock_coverage_days"] < 20:
        max_delivery = min(max_delivery, 15)
    if ctx["stock_coverage_days"] < 10:
        max_delivery = min(max_delivery, 7)

    # Stock minimum souhaité
    min_stock = base["min_stock_coverage_days"] + 20 * T

    dynamic_constraints = {
        "min_diversification": round(min_div, 3),
        "max_delivery_days": round(max_delivery, 3),
        "min_stock_coverage_days": round(min_stock, 3)
    }

    return dynamic_constraints, T, ts, tm, td


if __name__ == "__main__":
    dyn_constraints, T, ts, tm, td = compute_dynamic_constraints(base_constraints, context)

    print("\nDynamic Constraints :\n")
    for k, v in dyn_constraints.items():
        print(f"  {k}: {v}")

    print("\nTension globale T:", T)
