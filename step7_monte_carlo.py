import numpy as np
from step6_scenario_generation import generate_scenarios, suppliers, context
from step5_dynamic_constraints import compute_dynamic_constraints, base_constraints
from step4_dynamic_weights import compute_dynamic_weights, client_weights

supplier_data = {
    "A": {"price": 8.2, "delivery": 20, "quality": 7, "capacity": 2},
    "B": {"price": 7.9, "delivery": 10, "quality": 6, "capacity": 9},
    "C": {"price": 8.5, "delivery": 30, "quality": 5, "capacity": 9}
}


def scenario_score_one_sim(scenario, dyn_weights, ctx):
    eco_score = 0.0
    op_score = 0.0
    risk_score = 0.0

    for supplier, allocation in scenario["allocation"].items():
        data = supplier_data[supplier]

        price_sim = data["price"] * (1 + np.random.normal(0, ctx["market_volatility_change"]))
        delivery_sim = data["delivery"] * (1 + np.random.lognormal(0, 0.15))
        quality_sim = data["quality"] * (1 + np.random.normal(0, 0.05))
        capacity_sim = data["capacity"]

        eco_score += allocation * (1 / price_sim)
        op_score += allocation * ((1 / delivery_sim) + 0.5 * (quality_sim / 10.0))
        risk_score += allocation * ((capacity_sim / 10.0) - ctx["market_volatility_change"])

    return 0.4 * eco_score + 0.3 * op_score + 0.3 * risk_score


def simulate_scenario(scenario, dyn_weights, ctx, n=3000):
    scores = []
    objectives_counts = []

    cost_list = []
    delivery_list = []
    quality_list = []

    for _ in range(n):
        eco_score = 0.0
        op_score = 0.0
        risk_score = 0.0

        objectives_met = 0

        total_price = 0.0
        total_delivery = 0.0
        total_quality = 0.0

        for supplier, allocation in scenario["allocation"].items():
            data = supplier_data[supplier]

            price_sim = data["price"] * (1 + np.random.normal(0, ctx["market_volatility_change"]))
            delivery_sim = data["delivery"] * (1 + np.random.lognormal(0, 0.15))
            quality_sim = data["quality"] * (1 + np.random.normal(0, 0.05))

            eco_score += allocation * (1 / price_sim)
            op_score += allocation * ((1 / delivery_sim) + 0.5 * (quality_sim / 10.0))
            risk_score += allocation * ((data["capacity"] / 10.0) - ctx["market_volatility_change"])

            total_price += allocation * price_sim
            total_delivery += allocation * delivery_sim
            total_quality += allocation * quality_sim

        score = 0.4 * eco_score + 0.3 * op_score + 0.3 * risk_score
        scores.append(score)

        # OBJECTIFS MÉTIER
        if total_delivery <= ctx["stock_coverage_days"]:
            objectives_met += 1

        if total_price <= np.median([supplier_data[s]["price"] for s in supplier_data]):
            objectives_met += 1

        if score > 0.5:
            objectives_met += 1

        if "A" in scenario["allocation"] and ctx["supplier_dependency_A"] > 0.60:
            if scenario["allocation"]["A"] <= 0.80:
                objectives_met += 1
        else:
            objectives_met += 1

        if score > 0.0:
            objectives_met += 1

        objectives_counts.append(objectives_met)

        cost_list.append(total_price)
        delivery_list.append(total_delivery)
        quality_list.append(total_quality)

    scores = np.array(scores)
    objectives_counts = np.array(objectives_counts)

    prob_success = np.mean(objectives_counts >= 3)
    risk_failure = 1 - prob_success
    stability = 1 - np.std(scores)

    return {
        "prob_success": float(prob_success),
        "risk_failure": float(risk_failure),
        "stability": float(stability),
        "avg_cost": float(np.mean(cost_list)),
        "avg_delivery": float(np.mean(delivery_list)),
        "avg_quality": float(np.mean(quality_list)),
        "performance": float(np.mean(scores))
    }
