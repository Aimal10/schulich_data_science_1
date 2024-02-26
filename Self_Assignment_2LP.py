import gurobipy as gp
from gurobipy import GRB
import pandas as pd
data = pd.read_csv("/Users/aimaldastagirzada/Downloads/price_response (1).csv")

data = pd.read_csv(data_path)

# Assume the CSV file has columns named 'Intercept', 'Sensitivity', 'Capacity' for each product line
intercepts = data['Intercept'].tolist()
sensitivities = data['Sensitivity'].tolist()
capacities = data['Capacity'].tolist()

# Create a new model
m = gp.Model("price_optimization")

# Create variables for prices
prices = m.addVars(len(data), lb=0, name="P")

# The objective is to maximize revenue
m.setObjective(gp.quicksum(prices[i] * (intercepts[i] + sensitivities[i] * prices[i]) for i in range(len(data))), GRB.MAXIMIZE)

# Add capacity constraints
for i in range(len(data)):
    m.addConstr(prices[i] * (intercepts[i] + sensitivities[i] * prices[i]) <= capacities[i], f"capacity_{i}")

# Optimize the model
m.optimize()

# Print the optimal prices
for v in m.getVars():
    print(f"{v.varName} = {v.x}")

# Print the optimal total revenue
print(f"Total Revenue: {m.objVal}")
