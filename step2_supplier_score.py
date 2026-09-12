# Étape 2 — Supplier Score déterministe avec pondérations client

client_weights = {
    "quality": 0.40,
    "price": 0.20,
    "origin": 0.15,
    "delivery_time": 0.10,
    "currency": 0.05,
    "experience": 0.10
}

suppliers = [
    {
        "name": "A",
        "price": 8.20,
        "delivery_time": 20,
        "quality": 8.0,
        "origin": "Cote d'Ivoire",
        "currency": "USD",
        "experience": 10,
        "data_reliability": 0.8
    },
    {
        "name": "B",
        "price": 7.90,
        "delivery_time": 25,
        "quality": 7.5,
        "origin": "Ghana",
        "currency": "EUR",
        "experience": 0,
        "data_reliability": 0.7
    },
    {
        "name": "C",
        "price": 8.50,
        "delivery_time": 15,
        "quality": 8.5,
        "origin": "Cote d'Ivoire",
        "currency": "USD",
        "experience": 0,
        "data_reliability": 0.6
    }
]

origin_scores = {
    "Cote d'Ivoire": 0.9,
    "Ghana": 0.85,
    "Autre": 0.6
}

currency_risk_scores = {
    "USD": 0.7,
    "EUR": 0.9,
    "Autre": 0.5
}


def normalize_suppliers(suppliers):
    prices = [s["price"] for s in suppliers]
    deliveries = [s["delivery_time"] for s in suppliers]
    experiences = [s["experience"] for s in suppliers]

    price_min, price_max = min(prices), max(prices)
    delivery_min, delivery_max = min(deliveries), max(deliveries)
    exp_max = max(experiences)

    normalized = []

    for s in suppliers:
        reliability = s["data_reliability"]

        # Qualité (sur 10)
        quality_score = (s["quality"] / 10.0) * reliability

        # Prix (min-max inversé)
        price_score_raw = (price_max - s["price"]) / (price_max - price_min) if price_max != price_min else 1.0
        price_score = price_score_raw * reliability

        # Délais (min-max inversé)
        delivery_score_raw = (delivery_max - s["delivery_time"]) / (delivery_max - delivery_min) if delivery_max != delivery_min else 1.0
        delivery_score = delivery_score_raw * reliability

        # Origine
        origin_score_raw = origin_scores.get(s["origin"], origin_scores["Autre"])
        origin_score = origin_score_raw * reliability

        # Devise
        currency_score_raw = currency_risk_scores.get(s["currency"], currency_risk_scores["Autre"])
        currency_score = currency_score_raw * reliability

        # Expérience
        exp_score_raw = s["experience"] / exp_max if exp_max != 0 else 0.0
        exp_score = exp_score_raw * reliability

        normalized.append({
            "name": s["name"],
            "quality": quality_score,
            "price": price_score,
            "origin": origin_score,
            "delivery_time": delivery_score,
            "currency": currency_score,
            "experience": exp_score
        })

    return normalized


def compute_supplier_score(norm_supplier, weights):
    score = 0.0
    for crit, w in weights.items():
        score += w * norm_supplier[crit]
    return score


if __name__ == "__main__":
    normalized_suppliers = normalize_suppliers(suppliers)

    print("Scores normalisés par fournisseur :\n")
    for ns in normalized_suppliers:
        print(f"Fournisseur {ns['name']}:")
        for k, v in ns.items():
            if k != "name":
                print(f"  - {k}: {v:.3f}")
        print()

    print("Supplier Scores :\n")
    for ns in normalized_suppliers:
        score = compute_supplier_score(ns, client_weights)
        print(f"Fournisseur {ns['name']} — Score total: {score:.3f}")
