# main.py

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import pandas as pd
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
    product_name: str = Form(...),
    quantity: float = Form(...),
    competitor_price: Optional[float] = Form(None)
):
    """Optimizes prices based on form input for a single product and updates global data."""
    global daily_optimized_prices, expected_profit

    try:
        print("Received product name:", product_name)
        print("Received quantity:", quantity)
        print("Received competitor price:", competitor_price)

        # Prepare input in a dictionary format to match the expected input structure
        inputs = {
            "product_names": [product_name],
            "quantities": [quantity],
            "competitor_prices": [competitor_price]
        }

        # Call the optimization function
        daily_optimized_prices, expected_profit = optimize_daily_prices(data, inputs)
        
        # Return the optimized price and expected profit to the frontend
        return {"prices": daily_optimized_prices, "profit": expected_profit}
    
    except Exception as e:
        print("Error during optimization:", str(e))  # Log the error to the console
        raise HTTPException(status_code=500, detail="Optimization failed due to server error.")
