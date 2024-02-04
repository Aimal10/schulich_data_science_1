import gurobipy as gp
from gurobipy import GRB

try:
    # Create a new model
    m = gp.Model("SunnyshoreBayFinances")

    # Months and interest rates
    months = ['May', 'June', 'July', 'August']
    terms = [1, 2, 3]
    interest_rates = {1: 0.0175, 2: 0.0225, 3: 0.0275}

    # Revenue and expense data
    revenues = {'May': 180000, 'June': 260000, 'July': 420000, 'August': 580000}
    expenses = {'May': 300000, 'June': 400000, 'July': 350000, 'August': 200000}

    # Borrowing limits
    borrowing_limits = {'May': 250000, 'June': 150000, 'July': 350000}

    # Minimum cash balance requirements
    min_cash_balance = {'May': 25000, 'June': 20000, 'July': 35000, 'August': 18000}

    # Variables
    # Borrowed amounts
    borrow = m.addVars(months[:-1], terms, vtype=GRB.CONTINUOUS, name="borrow")

    # Cash balances
    cash_balance = m.addVars(months, vtype=GRB.CONTINUOUS, name="cash_balance")

    # Initial cash balance
    cash_balance['May'].lb = 140000

    # Constraints
    # Cash flow constraints
    m.addConstrs((cash_balance[month] == cash_balance[months[i-1]] + revenues[month] - expenses[month] -
                  gp.quicksum(borrow[month, t] for t in terms if i + t - 1 < len(months))
                  for i, month in enumerate(months[1:], start=1)), "CashFlow")

    # Minimum cash balance constraints
    for month in months:
        m.addConstr(cash_balance[month] >= min_cash_balance[month], "MinCash_" + month)

    # Borrowing limits
    for month in months[:-1]:
        m.addConstr(gp.quicksum(borrow[month, t] for t in terms) <= borrowing_limits[month], "BorrowLimit_" + month)

    # July cash balance constraint
    m.addConstr(cash_balance['July'] >= 0.65 * (cash_balance['May'] + cash_balance['June']), "JulyCashBalanceRequirement")

    # Objective: Minimize total repayment
    total_repayment = gp.quicksum(borrow[month, t] * (1 + interest_rates[t]) for month in months[:-1] for t in terms)
    m.setObjective(total_repayment, GRB.MINIMIZE)

    # Optimize model
    m.optimize()

    # Print solution
    if m.status == GRB.Status.OPTIMAL:
        print('\nOptimal Borrowing and Cash Balances:')
        m.printAttr('X')

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')
