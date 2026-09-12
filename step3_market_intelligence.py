import numpy as np

# Prix du cacao sur 3 mois (USD/tonne)
market_prices = [3650, 3720, 3900]

# Tendance simple
trend = "bull"  # bull / bear / neutral

# Régime de marché
market_regime = {
    "bull": 1.0,
    "bear": 0.3,
    "neutral": 0.6
}

def compute_market_score(prices, trend):
    # Variation
    variation = (prices[-1] - prices[0]) / prices[0]

    # Volatilité
    volatility = np.std(prices)
    max_volatility = max(50, volatility)  # pour normaliser dans le POC
    vol_score = 1 - (volatility / max_volatility)

    # Variation normalisée
    var_score = (variation + 0.1) / 0.2
    var_score = max(0, min(var_score, 1))

    # Tendance
    trend_scores = {
        "bull": 1.0,
        "bear": 0.3,
        "neutral": 0.6
    }
    trend_score = trend_scores.get(trend, 0.6)

    # Régime
    regime_score = market_regime.get(trend, 0.6)

    # Market Score final
    market_score = (
        0.4 * var_score +
        0.3 * vol_score +
        0.2 * trend_score +
        0.1 * regime_score
    )

    return {
        "variation": variation,
        "volatility": volatility,
        "var_score": var_score,
        "vol_score": vol_score,
        "trend_score": trend_score,
        "regime_score": regime_score,
        "market_score": market_score
    }


if __name__ == "__main__":
    result = compute_market_score(market_prices, trend)

    print("\nMarket Intelligence :\n")
    for k, v in result.items():
        print(f"{k}: {v:.4f}")
