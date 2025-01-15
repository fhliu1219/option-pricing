# Option Pricing Project

This project implements and explores financial models to compute the fair price of options and analyze volatility patterns in financial markets, using mathematical and computational tools to solve problems relevant to quantitative finance.

## Installation
Install dependencies:

## Goals:
1. Understand option pricing models:
- Implement and analyze models like Black-Scholes
- Explore volatility smiles and implied volatility

2. Build a Scalable Codebase:
- Develop modular, reusable, and well-documented code.
- Organize project into logical components for readability and collaboration

4. Perform Real-Word Analysis:
- Fetch and process real market data
- Use the models to analyze real-world options and draw insights.

5. Create Visualizations:
- Plot option prices, volatility surfaces, and other financial metrics to aid in understanding.

## Challenges:
1. Compute implied volatility from market option prices using iterative methods like Newton-Raphson method to understand how implied volatility differences from historical volatility and visualize it over different strike prices (volatility smile).

2. Extend the volatility smile to a volatility surface, incorporating both strike prices and time to maturity to analyze how volatility changes with respect to these variables.

3. Calibrate the BS model or other stochastic models such as Heston model using real market data to make model realistic by optimizing parameters to fit market data.

4. Use Monte Carlo methods to simulate stock price paths and compute option prices for more complex derivatives to explore how Monte Carlo compares to analytical solution

5. Delve into the concept of a risk-neutral measure, which underpins most pricing models, to write code to simulate under the risk-neutral probability and validate theoretical results.
