# models/optimization.py

import pandas as pd
from scipy.optimize import minimize

def payoff_function(vendor_price, competitor_price, demand, inventory):
    """
    Custom payoff function for vendor pricing to maximize profit based on demand and inventory.
    """
    # Demand response calculation (price impact on demand)
    demand_adjustment = demand * (1 - (vendor_price - competitor_price) / competitor_price if competitor_price else 1)
    cost = 0.01 * competitor_price * inventory
    revenue = vendor_price * min(inventory, demand_adjustment)
    return -(revenue - cost)

def optimize_daily_prices(data, inputs):
    """
    Runs the optimization to find the best price for each vegetable product for the day.
    Returns a list of optimized prices and an expected profit estimate.
    """
    optimal_prices = []
    total_profit = 0

    for i, product in enumerate(inputs['product_names']):
        inventory = inputs['quantities'][i]
        competitor_price = inputs['competitor_prices'][i]
        # Placeholder for actual demand calculation
        demand = data[data['Product Name'] == product]['Demand'].mean()

        result = minimize(
            payoff_function,
            x0=[competitor_price or 1.0],
            args=(competitor_price, demand, inventory),
            bounds=[(0, 500)]
        )
        optimal_price = result.x[0]
        optimal_prices.append({"name": product, "price": optimal_price, "inventory": inventory})
        total_profit += payoff_function(optimal_price, competitor_price, demand, inventory)

    return optimal_prices, -total_profit
