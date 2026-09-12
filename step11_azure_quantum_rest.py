import json
import requests
from step12_qubo_hybrid import build_qubo
from step8_scenario_generation import generate_scenarios, suppliers, context
from step7_dynamic_constraints import compute_dynamic_constraints, base_constraints
from step6_dynamic_weights import compute_dynamic_weights, client_weights
from step9_monte_carlo import simulate_scenario

# ---------------------------------------------------------
# CONFIGURATION AZURE QUANTUM 
# ---------------------------------------------------------
SUBSCRIPTION_ID = "/subscriptions/2919eb1e-05a6-4162-ac79-41bf0362cac4/resourceGroups/rg-supplier-intelligence-quantum/providers/Microsoft.Quantum/Workspaces/azure-quantum-rest"
RESOURCE_GROUP = "rg-supplier-intelligence-quantum"
WORKSPACE_NAME = "aeure-quantum-rest"
LOCATION = "East US"

# Clé d'accès Azure Quantum (depuis le portail Azure)
API_KEY = "YOUR_AZURE_QUANTUM_KEY"

# ---------------------------------------------------------
# Construction du QUBO
# ---------------------------------------------------------
dyn_constraints, T, _, _, _ = compute_dynamic_constraints(base_constraints, context)
dyn_weights, _, _, _, _ = compute_dynamic_weights(client_weights, context)

scenarios = generate_scenarios(suppliers, dyn_constraints, context)

results = {}
for sc in scenarios:
    results[sc["name"]] = simulate_scenario(sc, dyn_weights, context, n=2000)

Q, scenario_vars, alloc_vars = build_qubo(results, scenarios, T)

# ---------------------------------------------------------
# Conversion QUBO → JSON pour Azure Quantum REST API
# ---------------------------------------------------------
qubo_terms = []
for (i, j), coeff in Q.items():
    if i == j:
        qubo_terms.append({"c": coeff, "ids": [i]})
    else:
        qubo_terms.append({"c": coeff, "ids": [i, j]})

payload = {
    "problemType": "qubo",
    "terms": qubo_terms
}

# ---------------------------------------------------------
# Envoi à Azure Quantum via REST API
# ---------------------------------------------------------
url = (
    f"https://{LOCATION}.quantum.azure.com/"
    f"subscriptions/{SUBSCRIPTION_ID}/"
    f"resourceGroups/{RESOURCE_GROUP}/"
    f"providers/Microsoft.Quantum/"
    f"workspaces/{WORKSPACE_NAME}/"
    f"solvers/quantum-inspired/optimize?api-version=2023-10-01-preview"
)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

print("\nAzure Quantum REST API response:")
print(response.status_code)
print(response.text)

# ---------------------------------------------------------
# Décodage de la solution
# ---------------------------------------------------------
try:
    result_json = response.json()
    config = result_json.get("configuration", {})

    print("\nDecoded solution:")
    for var, value in config.items():
        if value == 1:
            print(f"  {var} = 1")

except Exception as e:
    print("Error decoding solution:", e)
