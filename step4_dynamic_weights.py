client_weights = {
    "price": 0.50,
    "quality": 0.20,
    "delivery": 0.20,
    "risk": 0.10
}

context = {
    "market_price_change": 0.15,        # +15 %
    "market_volatility_change": 0.02,   # +2 %
    "market_regime": "bull",            # bull / bear / neutral

    "stock_change": -0.35,              # -35 %
    "stock_coverage_days": 14,          # jours de couverture
    "demand_change": 0.08,              # +8 %
    "supplier_dependency_A": 0.72       # 72 % dépendance sur A
}


def compute_tension_index(ctx):
    # Tension stock : plus le stock baisse et la couverture est faible, plus tension ↑
    stock_drop = max(0.0, -ctx["stock_change"])  # -(-0.35) = 0.35
    coverage = ctx["stock_coverage_days"]
    coverage_factor = max(0.0, (30 - coverage) / 30.0)  # si <30 jours, tension ↑
    tension_stock = 0.6 * stock_drop + 0.4 * coverage_factor

    # Tension marché : prix ↑ + volatilité ↑ + régime bull
    price_change = max(0.0, ctx["market_price_change"])
    vol_change = max(0.0, ctx["market_volatility_change"])
    regime_factor = 1.0 if ctx["market_regime"] == "bull" else (0.5 if ctx["market_regime"] == "neutral" else 0.2)
    tension_market = 0.5 * price_change + 0.3 * vol_change + 0.2 * regime_factor

    # Tension dépendance : plus dépendance A est forte, plus tension ↑
    dep = ctx["supplier_dependency_A"]
    tension_dependency = dep  # simple pour le POC

    # Tension globale (on peut ajuster les poids)
    T = 0.4 * tension_stock + 0.4 * tension_market + 0.2 * tension_dependency

    # On borne entre 0 et 1 pour rester propre
    T = max(0.0, min(T, 1.0))
    return T, tension_stock, tension_market, tension_dependency


def compute_dynamic_weights(client_w, ctx):
    T, ts, tm, td = compute_tension_index(ctx)

    # On part des poids client
    price = client_w["price"]
    quality = client_w["quality"]
    delivery = client_w["delivery"]
    risk = client_w["risk"]

    # Ajustements en fonction de la tension
    # Plus T est élevé, plus on réduit le poids du prix et on augmente délai + risque
    price_dyn = price * (1 - 0.6 * T)          # prix perd jusqu'à 60% de son poids
    delivery_dyn = delivery + 0.4 * T          # délai gagne jusqu'à +0.4
    risk_dyn = risk + 0.5 * T                  # risque gagne jusqu'à +0.5
    quality_dyn = quality                      # qualité reste relativement stable

    # On évite les valeurs négatives
    price_dyn = max(0.0, price_dyn)
    delivery_dyn = max(0.0, delivery_dyn)
    risk_dyn = max(0.0, risk_dyn)
    quality_dyn = max(0.0, quality_dyn)

    # Renormalisation pour que la somme = 1
    total = price_dyn + quality_dyn + delivery_dyn + risk_dyn
    if total == 0:
        # cas pathologique, on revient aux poids client
        return client_w, T, ts, tm, td

    dyn_weights = {
        "price": price_dyn / total,
        "quality": quality_dyn / total,
        "delivery": delivery_dyn / total,
        "risk": risk_dyn / total
    }

    return dyn_weights, T, ts, tm, td


if __name__ == "__main__":
    dyn_w, T, ts, tm, td = compute_dynamic_weights(client_weights, context)

    print("\nContexte :")
    for k, v in context.items():
        print(f"  {k}: {v}")

    print("\nTension index :")
    print(f"  tension_stock: {ts:.3f}")
    print(f"  tension_market: {tm:.3f}")
    print(f"  tension_dependency: {td:.3f}")
    print(f"  Tension globale T: {T:.3f}")

    print("\nPondérations client (structurelles) :")
    for k, v in client_weights.items():
        print(f"  {k}: {v:.3f}")

    print("\nPondérations dynamiques (contextuelles) :")
    for k, v in dyn_w.items():
        print(f"  {k}: {v:.3f}")