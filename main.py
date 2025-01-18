import yfinance as yf
from functions.black_scholes import black_scholes_price, implied_volatility
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
from datetime import datetime, timezone
import numpy as np

# Global Parameters:
r = 0.05 # General assumption for Risk-free rate

def fetch_market_data(ticker):
    try:
        # Fetch option data for a stock (e.g., AAPL)   
        stock = yf.Ticker(ticker)
        # Getting expiration dates
        expirations = stock.options
        S = stock.history(period="1d")["Close"].iloc[-1] # Current Stock prices
    except Exception as e:
        print(f"Error fetching market data for {ticker}: {e}")
        return None, None

    # Fetch option chain for multiple expiration
    data = {}
    for expiry in expirations: # Could limit to 3 expirations for simplicity, but let's expand!
        chain = stock.option_chain(expiry)
        calls = chain.calls.dropna(subset = ["lastPrice"]) # Filter out NaN prices
        data[expiry] = {
            'strike' : calls['strike'].tolist(),
            'lastPrice' : calls['lastPrice'].tolist(),
            'expiration' : expiry
        }
    
    return S, data

def calculate_time_to_maturity(expiry):
    expiry_date = datetime.strptime(expiry, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    today = datetime.now(timezone.utc) # Use UTC for consistency
    return (expiry_date - today).days / 365.0

def calculate_vol_surface(market_data, S, r):
    """
    Calculate implied Volatility for options in the market data
    """
    
    vol_surface = []
    for expiry, options in market_data.items():
        T = calculate_time_to_maturity(expiry)
        strikes = options['strike']
        market_prices = options['lastPrice']
        implied_vols = []
        for K, market_price in zip(strikes, market_prices):
            try:
                iv = implied_volatility(market_price, S, K, T, r, call = True)
                implied_vols.append(iv)
            except ValueError as e:
                print(f"Implied Volatility not computed for strike {K} at expiry {expiry}:{e}")
                implied_vols.append(None)
        vol_surface.append({
            'expiry': expiry,
            'T': T,
            'strike': strikes,
            'implied_vols': implied_vols
        })
    
    return vol_surface

def plot_vol_surface(vol_surface):
    strike_prices = []
    time_to_maturities = []
    volatilities = []

    for entry in vol_surface:
        T = entry['T']
        for strike, iv in zip(entry['strike'], entry['implied_vols']):
            if iv is not None:
                strike_prices.append(strike)
                time_to_maturities.append(T)
                volatilities.append(iv)

    # Filter any missing volatilities before plotting
    valid_data = [(K, T, iv) for K, T, iv in zip(strike_prices, time_to_maturities, volatilities) if iv is not None]
    
    if not valid_data: # Checking if valid_data is not empty
        print("No valid data available for plotting")
    X,Y,Z = np.array(valid_data).T

    # 2) Create a regular 2D grid for strike (K) and time (T)
    K_lin = np.linspace(X.min(), X.max(), 50)  # 50 points in strike dimension
    T_lin = np.linspace(Y.min(), Y.max(), 50)  # 50 points in time dimension
    K_grid, T_grid = np.meshgrid(K_lin, T_lin)

    # 3) Interpolate implied volatilities onto the grid
    Z_grid = griddata(
        (X, Y),   # Known (strike, time) points
        Z,        # Known implied volatilities
        (K_grid, T_grid),
        method='cubic'  # 'cubic', 'linear', or 'nearest'
        
    )

    # 4) Plot the surface
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    # Optionally mask invalid values (NaNs) if interpolation fails outside data range
    # Z_grid = np.ma.masked_invalid(Z_grid)

    # plot_surface for a continuous 3D representation
    surf = ax.plot_surface(
        K_grid, T_grid, Z_grid,
        cmap='viridis',
        edgecolor='none',
        alpha=0.8
    )

    ax.set_title("Implied Volatility Surface")
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Time to Maturity (Years)")
    ax.set_zlabel("Implied Volatility")

    # Add a color bar (optional)
    fig.colorbar(surf, shrink=0.5, aspect=10, label='Vol')

    plt.show()

    ## 3D plot Generation for non-smooth function

    # fig = plt.figure(figsize = (10, 7))
    # ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(X,Y,Z, c=Z, cmap='viridis', marker='o')
    # ax.set_title("Implied Volatility Surface")
    # ax.set_xlabel("Strike prices")
    # ax.set_ylabel("Time to Maturity (Years)")
    # ax.set_zlabel("Implied Volatility")
    # plt.show()

def main(ticker):
    S, market_data = fetch_market_data(ticker)
    vol_surface = calculate_vol_surface(market_data, S = S, r = r)
    plot_vol_surface(vol_surface)
    
if __name__ == "__main__":
    main("AAPL") # Could be any stock symbol