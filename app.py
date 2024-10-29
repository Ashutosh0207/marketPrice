# app.py

import pandas as pd
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from scipy.optimize import minimize
import time
import threading

app = FastAPI()

# Mount static files for serving CSS, JS, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 template setup
templates = Jinja2Templates(directory="templates")

# Load and preprocess data for initial training
data = pd.read_csv('Updated_Market_Data.csv')
data['Price'].fillna(data.groupby('Product Name')['Price'].transform('median'), inplace=True)
data['Competitor Price'].fillna(data.groupby('Product Name')['Competitor Price'].transform('median'), inplace=True)
data_encoded = pd.get_dummies(data, columns=['Season', 'Weather', 'Local Event', 'Customer Segment', 'Location'], drop_first=True)
data_encoded['Price Difference'] = data_encoded['Price'] - data_encoded['Competitor Price']
X = data_encoded.drop(columns=['Vendor Name', 'Product Name', 'Category', 'Price'])
y = data_encoded['Price']

# Train the Gradient Boosting model initially
gbr = GradientBoostingRegressor(random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
gbr.fit(X_train, y_train)

# Storage for continuous predictions
latest_predictions = []

# Define payoff function and optimization for game theory
def payoff_function(vendor_price, competitor_price, inventory):
    revenue = vendor_price * (1 - abs(vendor_price - competitor_price) / competitor_price)
    cost = competitor_price * inventory * 0.01
    return -(revenue - cost)

def best_response_optimization(competitor_prices, inventory_levels):
    optimal_prices = []
    for i in range(len(competitor_prices)):
        competitor_price = competitor_prices[i]
        inventory = inventory_levels[i]
        result = minimize(payoff_function, x0=[competitor_price], args=(competitor_price, inventory), bounds=[(0, 500)])
        optimal_prices.append(result.x[0])
    return optimal_prices

# Continuous price predictions update function
def update_predictions():
    global latest_predictions
    while True:
        competitor_prices = np.random.uniform(50, 200, size=len(X))
        inventory_levels = np.random.uniform(10, 500, size=len(X))
        model_predictions = gbr.predict(X_test)
        optimal_vendor_prices = best_response_optimization(competitor_prices, inventory_levels)
        fruit_names = data['Product Name'].unique()[:10]
        fruit_seasons = data['Season'][:10]
        fruit_weather = data['Weather'][:10]
        latest_predictions = [
            {
                "name": fruit_names[i],
                "price": optimal_vendor_prices[i],
                "season": fruit_seasons[i],
                "weather": fruit_weather[i],
                "competitor_price": competitor_prices[i],
                "inventory": inventory_levels[i]
            }
            for i in range(10)
        ]
        time.sleep(10)

# Start background thread for continuous updates
threading.Thread(target=update_predictions, daemon=True).start()

# Response model for API
class PriceData(BaseModel):
    name: str
    price: float
    season: Optional[str] = None
    weather: Optional[str] = None
    competitor_price: float
    inventory: float

class PriceResponse(BaseModel):
    optimal_prices: List[PriceData]

@app.get("/get_latest_prices", response_model=PriceResponse)
async def get_latest_prices():
    return {"optimal_prices": latest_predictions}

# Root route to serve the dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
