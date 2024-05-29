import gurobipy as gp
from gurobipy import GRB
import pandas as pd
supply_data = pd.read_csv('/Users/aimaldastagirzada/Downloads/ecogreen_energy_supply.csv')
demand_data = pd.read_csv('/Users/aimaldastagirzada/Downloads/ecogreen_energy_demand.csv')

model = gp.Model("EcoGreen_Energy_Expansion")

# Indices for plants and provinces
plants = range(len(supply_data))
provinces = range(len(demand_data))

# Decision Variables
# y_i: Binary decision for building plant i
y = model.addVars(plants, vtype=GRB.BINARY, name="Plant")
# x_ij: Continuous variable for energy from plant i to province j
x = model.addVars(plants, provinces, vtype=GRB.CONTINUOUS, name="Transport")

# Objective Function to minimize total cost
model.setObjective(
    gp.quicksum(
        y[i] * supply_data.loc[i, 'Fixed'] +
        gp.quicksum(x[i, j] * supply_data.loc[i, f'Province {j+1}'] for j in provinces)
        for i in plants),
    GRB.MINIMIZE)
# Constraints
# Capacity constraints for each plant
model.addConstrs(
    (gp.quicksum(x[i, j] for j in provinces) <= supply_data.loc[i, 'Capacity'] * y[i]
     for i in plants), name="Capacity")

# Demand fulfillment for each province
model.addConstrs(
    (gp.quicksum(x[i, j] for i in plants) >= demand_data.loc[j, 'Demand']
     for j in provinces), name="Demand")
# Logical and additional constraints
model.addConstr(y[9] + y[14] + y[19] <= 1, "Mutual_Exclusivity")
model.addConstr(y[2] <= y[3], "Site3_to_Site4")
model.addConstr(y[2] <= y[4], "Site3_to_Site5")
model.addConstr(y[4] <= y[7] + y[8], "Site5_dependency")
model.addConstr(gp.quicksum(y[i] for i in range(10)) <= 2 * gp.quicksum(y[i] for i in range(10, 20)), "Region_A_vs_B")
total_output = gp.quicksum(x[i, j] for i in plants for j in provinces)
model.addConstr(gp.quicksum(x[i, j] for i in range(5) for j in provinces) >= 0.3 * total_output, "Minimum_Output_Sites_1_5")

# Single plant output cap
for i in plants:
    for j in provinces:
        model.addConstr(x[i, j] <= 0.5 * demand_data.loc[j, 'Demand'], f"Cap_{i}_{j}")

# Solve the model
model.optimize()

# Display the results
if model.status == GRB.OPTIMAL:
    print("Optimal solution found.")
    # Print the optimal total cost
    print(f"Total Optimal Cost: ${model.ObjVal:,.2f}")

    # Print the decision to build each plant
    for i in plants:
        print(f"Plant {i+1} built: {'Yes' if y[i].X > 0.5 else 'No'}")

    # Print energy sent from each plant to each province, where applicable
    for i in plants:
        for j in provinces:
            if x[i, j].X > 0:
                print(f"Energy from Plant {i+1} to Province {j+1}: {x[i, j].X} GWh")
else:
    print("Optimal solution not found. Status code:", model.status)

# After solving the model, calculate the number of provinces each plant supplies
for i in plants:
    num_provinces_supplied = sum(1 for j in provinces if x[i, j].X > 0)
    print(f"Plant {i+1} supplies energy to {num_provinces_supplied} distinct provinces.")

# Total number of decision variables
total_decision_variables = len(y) + len(x)
print(f"Total decision variables required: {total_decision_variables}")

# Using Gurobi to report the number of variables
print(f"Gurobi reports {model.NumVars} variables.")

# Displaying capacity constraints
for constr in model.getConstrs():
    if "Capacity" in constr.ConstrName:
        print(f"{constr.ConstrName}: {constr}")

# Counting capacity constraints
print(f"Total capacity constraints: {sum(1 for constr in model.getConstrs() if 'Capacity' in constr.ConstrName)}")

##(d) 
print("Constraint for mutual exclusivity between sites 10, 15, and 20:")
print(model.getConstrByName("Mutual_Exclusivity"))

##e
print("Dependency constraint for site 5 on sites 8 or 9:")
print(model.getConstrByName("Site5_dependency"))
##F
if model.status == GRB.OPTIMAL:
    print(f"Optimal Cost: ${model.ObjVal:,.2f}")
else:
    print("Optimal solution was not found.")

##g
num_plants_established = sum(1 for i in plants if y[i].X > 0.5)
print(f"Number of power plants established: {num_plants_established}")
##H
# Calculate the number of plants supplying each province
plants_per_province = {j: sum(1 for i in plants if x[i, j].X > 0) for j in provinces}

# Finding the highest and lowest
max_plants = max(plants_per_province.values())
min_plants = min(plants_per_province.values())
print(f"Highest number of plants for a province: {max_plants}")
print(f"Lowest number of plants for a province: {min_plants}")
##J
# Set MIP gap to 1%
model.Params.MIPGap = 0.01

# Optimize the model
model.optimize()

# Reporting the number of feasible solutions found within 1% of the optimal cost
print("Number of feasible solutions within 1% of the optimal solution:", model.SolCount)
##k
# Remove constraints limiting plant output to 50% of province needs
for i in plants:
    for j in provinces:
        model.remove(model.getConstrByName(f"Cap_{i}_{j}"))

model.optimize()

if model.status == GRB.OPTIMAL:
    print(f"Optimal Cost without 50% cap: ${model.ObjVal:,.2f}")
    print(f"Number of plants established without 50% cap: {sum(1 for i in plants if y[i].X > 0.5)}")
else:
    print("Optimal solution was not found after removing the 50% cap constraints.")


