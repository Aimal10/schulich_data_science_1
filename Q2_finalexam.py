from gurobipy import Model, GRB
import gurobipy as gp

# Initialize the model
model = gp.Model("Optimal_Coffee_Ordering")

# Problem data
scenarios = [
    {'n': 1, 'p': 0.09, 'd': 90},
    {'n': 2, 'p': 0.12, 'd': 95},
    {'n': 3, 'p': 0.10, 'd': 100},
    {'n': 4, 'p': 0.05, 'd': 105},
    {'n': 5, 'p': 0.16, 'd': 110},
    {'n': 6, 'p': 0.14, 'd': 115},
    {'n': 7, 'p': 0.03, 'd': 120},
    {'n': 8, 'p': 0.08, 'd': 125},
    {'n': 9, 'p': 0.05, 'd': 130},
    {'n': 10, 'p': 0.05, 'd': 135},
    {'n': 11, 'p': 0.04, 'd': 140},
    {'n': 12, 'p': 0.03, 'd': 145},
    {'n': 13, 'p': 0.02, 'd': 150},
    {'n': 14, 'p': 0.01, 'd': 155},
    {'n': 15, 'p': 0.02, 'd': 160},
    {'n': 16, 'p': 0.01, 'd': 165}
]

# Define the decision variables
initial_order = model.addVar(name="InitialOrder", vtype=GRB.INTEGER)
phil_sebastian_order = {s['n']: model.addVar(name=f"PhilSebastian_{s['n']}", vtype=GRB.INTEGER) for s in scenarios}
rosso_order = {s['n']: model.addVar(name=f"Rosso_{s['n']}", vtype=GRB.INTEGER) for s in scenarios}
monogram_order = {s['n']: model.addVar(name=f"Monogram_{s['n']}", vtype=GRB.INTEGER) for s in scenarios}


# Set the objective to minimize the total expected cost
model.setObjective(95 * initial_order + sum(s['p'] * (120 * phil_sebastian_order[s['n']] + 105 * rosso_order[s['n']] + 110 * monogram_order[s['n']]) for s in scenarios), GRB.MINIMIZE)

for s in scenarios:
    model.addConstr(initial_order + phil_sebastian_order[s['n']] + rosso_order[s['n']] + monogram_order[s['n']] >= s['d'], name=f"SupplyRequirement_{s['n']}")

    # Add binary variables and constraints for minimum orders from Rosso and Monogram
    rosso_indicator = model.addVar(vtype=GRB.BINARY, name=f"RossoIndicator_{s['n']}")
    model.addGenConstrIndicator(rosso_indicator, True, rosso_order[s['n']] >= 70, name=f"RossoMinOrder_{s['n']}")
    model.addGenConstrIndicator(rosso_indicator, False, rosso_order[s['n']] == 0, name=f"NoRossoOrder_{s['n']}")

    monogram_indicator = model.addVar(vtype=GRB.BINARY, name=f"MonogramIndicator_{s['n']}")
    model.addGenConstrIndicator(monogram_indicator, True, monogram_order[s['n']] >= 40, name=f"MonogramMinOrder_{s['n']}")
    model.addGenConstrIndicator(monogram_indicator, False, monogram_order[s['n']] == 0, name=f"NoMonogramOrder_{s['n']}")

# Execute the model optimization
model.optimize()

# Output the optimized results
total_initial_cost = 95 * initial_order.X
print(f"Optimal initial order quantity: {initial_order.X}, Total Initial Cost: ${total_initial_cost:.2f}")
for s in scenarios:
    cost_phil = 120 * phil_sebastian_order[s['n']].X
    cost_rosso = 105 * rosso_order[s['n']].X
    cost_monogram = 110 * monogram_order[s['n']].X
    total_cost_local = cost_phil + cost_rosso + cost_monogram
    print(f"Scenario {s['n']}: Local Costs: Phil & Sebastian = ${cost_phil:.2f}, Rosso = ${cost_rosso:.2f}, Monogram = ${cost_monogram:.2f}, Total Local = ${total_cost_local:.2f}")
    
#E
for s in scenarios:
    # Add binary variables and constraints for minimum orders from Rosso
    rosso_indicator = model.addVar(vtype=GRB.BINARY, name=f"RossoIndicator_{s['n']}")
    model.addGenConstrIndicator(rosso_indicator, True, rosso_order[s['n']] >= 70, name=f"RossoMinOrder_{s['n']}")
    model.addGenConstrIndicator(rosso_indicator, False, rosso_order[s['n']] == 0, name=f"NoRossoOrder_{s['n']}")


##F
# After optimization
model.optimize()

# Retrieve the optimal number of gallons to order initially
optimal_gallons = initial_order.X

# Calculate the total initial cost based on the optimal initial order quantity
total_initial_cost = 95 * optimal_gallons

# Retrieve the optimal objective function value (total expected cost including scenarios)
optimal_total_cost = model.ObjVal

print(f"Optimal gallons to order in advance: {optimal_gallons}")
print(f"Total Initial Cost: ${total_initial_cost:.2f}")
print(f"Optimal Total Expected Cost: ${optimal_total_cost:.2f}")


#G
# Calculate the total expected cost of supplying all demand from local suppliers
expected_cost_without_initial_order = sum(s['p'] * min(120 * s['d'], 105 * max(s['d'] - 70, 0) + 70 * 105, 110 * max(s['d'] - 40, 0) + 40 * 110) for s in scenarios)
# Calculate total expected demand
total_demand = sum(s['p'] * s['d'] for s in scenarios)
# Calculate the threshold price
threshold_price_no_order = expected_cost_without_initial_order / total_demand
print(f"Threshold price for no initial order: ${round(threshold_price_no_order, 1)} per gallon")

##H
max_demand = max(s['d'] for s in scenarios)  # The maximum demand from the scenarios
cost_if_max_ordered = 95 * max_demand
threshold_price_max_order = cost_if_max_ordered / total_demand
print(f"Threshold price for maximum order: ${round(threshold_price_max_order, 1)} per gallon")

# I 
# Assume perfect_info_costs are calculated by simulating the minimum cost for each scenario
perfect_info_costs = [min(95 * s['d'], 120 * s['d'], 105 * max(s['d'] - 70, 0) + 70 * 105, 110 * max(s['d'] - 40, 0) + 40 * 110) for s in scenarios]
perfect_information_cost = sum(s['p'] * cost for s, cost in zip(scenarios, perfect_info_costs))

# EVPI
evpi = model.ObjVal - perfect_information_cost
print(f"Expected Value of Perfect Information (EVPI): ${evpi:.2f}")

import gurobipy as gp
from gurobipy import GRB


# Calculate mean demand
mean_demand = sum(s['p'] * s['d'] for s in scenarios)

# Model setup for the deterministic mean value problem
m_mean = gp.Model("Deterministic_Mean_Value_Problem")

# Decision variables
x_mean = m_mean.addVar(name="x_mean", vtype=GRB.INTEGER)  # Base order

# Objective function to minimize cost
m_mean.setObjective(95 * x_mean, GRB.MINIMIZE)

# Constraint to ensure demand is met using average demand
m_mean.addConstr(x_mean >= mean_demand, "AverageDemand")

# Solve the model
m_mean.optimize()

print("Objective for the Average:", m_mean.objVal)

#Step 2: stochastic solution holding first-stage variables fixed
# Create a new optimization model
m_stochastic = gp.Model("Stochastic_Model")

# Use first-stage decisions from the mean value problem
fs_x = x_mean.X

# Scenario-specific decision variables
y1 = m_stochastic.addVars(len(scenarios), vtype=GRB.INTEGER, name="y1")
y2 = m_stochastic.addVars(len(scenarios), vtype=GRB.INTEGER, name="y2")
y3 = m_stochastic.addVars(len(scenarios), vtype=GRB.INTEGER, name="y3")

# Objective function to minimize total expected cost
objective = gp.quicksum(s['p'] * (95 * fs_x + 120 * y1[i] + 105 * y2[i] + 110 * y3[i]) for i, s in enumerate(scenarios))
m_stochastic.setObjective(objective, GRB.MINIMIZE)

# Constraints for each scenario
for i, s in enumerate(scenarios):
    m_stochastic.addConstr(fs_x + y1[i] + y2[i] + y3[i] >= s['d'], name=f"Demand_{i}")

# Additional constraints for minimum orders if any

# Solve our model
m_stochastic.optimize()

print("Objective for the Stochastic Solution:", m_stochastic.objVal)

# EEV from the mean value problem
EEV = m_mean.objVal

# SP from the stochastic model
SP = m_stochastic.objVal

# Calculate VSS
VSS = abs(EEV - SP)

print("EEV (Expected Ex-Post Value):", EEV)
print("SP (Expected Value of Stochastic Solution):", SP)
print("VSS (Value of Stochastic Solution):", VSS)


