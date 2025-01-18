import numpy as np
from scipy.stats import norm
from datetime import datetime, timezone

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

    Final Fix for inability to converge using Newton method:
    1. Use secant method with dynamic perturbation for small denominators (Vera) error.
    2. Introducing damping factor to stabilizing updates.
    3. Imposed clamping on volatility within reasonable limit [0.01, 0.5].
    4. Introducing Huag-Johnson approximation for initial guess.
    5. Introducing dynamic damping with residual-based method due to nonlinear relationship between ITM or OTM options, 
    additionally, the residual often directly reflects how close the current guess is to the solution.
    6. Introducing additional modification for ITM/OTM options.
    """
    sigma_0 = max(0.01, np.sqrt(2 * np.pi / T) * (market_price / S))  # HJ approximation
    
    # Additional modification for ITM/OTM options:
    if S > K:  # ITM Call or OTM Put
        sigma_0 *= 0.8
    elif S < K:  # OTM Call or ITM Put
        sigma_0 *= 1.2
    
    sigma_1 = sigma_0 + 0.2 # Slightly perturbed for secant method.
    residual_threshold = 1.0  # Adjust this based on problem characteristics. Increase if converge too slow, decrease otherwise

    for _ in range(max_iter):
        # Compute prices and function values
        price_0 = black_scholes_price(S, K, T, r, sigma_0, call)
        price_1 = black_scholes_price(S, K, T, r, sigma_1, call)
        f_0 = price_0 - market_price
        f_1 = price_1 - market_price

        # Check denominator
        if abs(f_1 - f_0) < 1e-10:
            sigma_1 += 0.01  # Perturb and retry
            continue
        
        # Dynamic damping using residual-based damping:
        damping = min(1, residual_threshold / max(abs(f_1), tol))

        # Secant update with damping
        sigma_new = sigma_1 - damping * f_1 * (sigma_1 - sigma_0) / (f_1 - f_0)

        # Clamp and check convergence
        sigma_new = max(min(sigma_new, 5.0), 0.01)
        if abs(sigma_new - sigma_1) < tol:
            return sigma_new

        # Update guesses
        sigma_0, sigma_1 = sigma_1, sigma_new

    raise ValueError(f"Implied Volatility not computed for strike {K} at expiry {T}: Secant method failed.")