# main.py

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from models.optimization import optimize_daily_prices

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates for HTML rendering
templates = Jinja2Templates(directory="templates")

# Load initial data
data = pd.read_csv("data/Updated_Market_Data.csv")

# Global variable to store optimized prices and profit
daily_optimized_prices = []
expected_profit = 0.0

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Renders the main dashboard with optimized price data."""
    return templates.TemplateResponse("index.html", {"request": request, "prices": daily_optimized_prices, "profit": expected_profit})

@app.post("/optimize")
async def optimize_prices(
    product_names: List[str] = Form(...),
    quantities: List[float] = Form(...),
    competitor_prices: List[float] = Form(None)
):
    """Optimizes prices based on input from the vendor and updates the global data for display."""
    global daily_optimized_prices, expected_profit
    # Collect input data
    inputs = {
        "product_names": product_names,
        "quantities": quantities,
        "competitor_prices": competitor_prices if competitor_prices else [None] * len(product_names)
    }
    # Call optimization function to calculate optimal prices and expected profit
    daily_optimized_prices, expected_profit = optimize_daily_prices(data, inputs)
    return {"status": "success"}
