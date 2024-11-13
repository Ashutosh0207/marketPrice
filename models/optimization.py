# models/optimization.py

import pandas as pd
from scipy.optimize import minimize
import numpy as np

def payoff_function(vendor_price, competitor_price, demand, inventory):
    """Calculates the profit given vendor price, competitor price, demand, and inventory."""
    # Demand response calculation with price sensitivity
    price_sensitivity = 0.7  # Adjust this as needed to simulate demand impact
    demand_adjustment = demand * (1 - price_sensitivity * (vendor_price - competitor_price) / (competitor_price if competitor_price else 1))
    
    # Prevent demand from going negative
    demand_adjustment = max(demand_adjustment, 0)

    # Calculate cost and revenue
    cost = 0.01 * (competitor_price or vendor_price) * inventory
    revenue = vendor_price * min(inventory, demand_adjustment)
    
    # Negative profit for minimization
    return -(revenue - cost)

def optimize_daily_prices(data, inputs):
    """Optimizes prices for each product and calculates total profit."""
    # Verify required columns exist
    if 'Product Name' not in data.columns or 'Competitor Price' not in data.columns or 'Inventory Levels (kg)' not in data.columns:
        raise ValueError("The required columns 'Product Name', 'Competitor Price', or 'Inventory Levels (kg)' are missing from the data.")

    optimal_prices = []
    total_profit = 0

    for i, product in enumerate(inputs['product_names']):
        inventory = inputs['quantities'][i]
        competitor_price = inputs['competitor_prices'][i]
        
        # Filter product data and estimate demand (e.g., using average inventory)
        product_data = data[data['Product Name'] == product]
        if product_data.empty:
            print(f"Warning: No data found for product '{product}'. Skipping optimization for this product.")
            continue
        
        # Placeholder for demand estimate
        demand = product_data['Inventory Levels (kg)'].mean() * 0.8  # Adjust multiplier as needed

        # Set initial guess for optimization (slightly different from competitor price)
        initial_price = competitor_price * 1.05 if competitor_price else 1.0  # Start 5% above competitor price

        # Run optimization
        result = minimize(
            payoff_function,
            x0=[initial_price],
            args=(competitor_price, demand, inventory),
            bounds=[(0, 500)]
        )
        optimal_price = result.x[0]
        optimal_prices.append({"name": product, "price": optimal_price, "inventory": inventory})
        total_profit += payoff_function(optimal_price, competitor_price, demand, inventory)

    return optimal_prices, -total_profit
