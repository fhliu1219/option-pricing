import numpy as np
from scipy.stats import norm

def black_scholes_price(S,K,T,r,sigma, call = True):
    """
    Calculating the Black-Scholes price for European Options

    Parameters:
    S: Current Stock Price
    K: Strike Price
    T: Time to maturity (in years)
    r: Risk-free interest rate
    sigma: Volatility 
    call: True for call option, else False.
    """
    
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2)*T) / (sigma * (T**0.5))
    d2 = (d1 - sigma*T**0.5)
    if call:
        return S * norm.cdf(d1) - K * np.exp(-r*T)*norm.cdf(d2)
    else:
        return K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
def implied_volatility(market_price, S, K, T, r, call = True, tol =1e-6, max_iter = 1000):
    """
    Calculating the implied volatility for an option using Newton method

    Parameters:
    market_price : Observed market price of the option
    tol: Tolerance for convergence
    max_iter: Maximum number of iterations
    """
    
    # Initial guesses
    sigma = 0.2

    for _ in range(max_iter):
        # Calculate the option price with the current sigma
        bs_price = black_scholes_price(S, K, T, r, sigma, call)
        # Derivative of Black-Scholes price with respect to sigma (vega)
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T)  # PDF of d1

        # Update sigma using Newton-Raphson
        sigma_new = sigma - (bs_price - market_price) / vega
        if abs(sigma_new - sigma) < tol:
            return sigma_new
        sigma = sigma_new
    raise ValueError("Implied volatility did not converge")