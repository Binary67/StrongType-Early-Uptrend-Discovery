# Strong Typed Genetic Programming for Uptrend Pattern Discovery

## Project Objective

This project uses **Genetic Programming (GP)** to automatically discover patterns in financial data that can predict when an uptrend is about to happen. Think of it like teaching a computer to recognize the "fingerprints" that appear in stock price data just before prices start going up consistently.

### What is an Uptrend?
In this project, we define an uptrend as occurring when:
- **EMA 12 > EMA 50** (12-period exponential moving average is greater than 50-period exponential moving average)

This is like saying "the short-term average price is higher than the long-term average price," which typically indicates the stock is gaining momentum upward.

## What is Strong Type Genetic Programming?

### Simple Explanation
Regular GP is like giving someone random Lego blocks and hoping they build something useful. **Strong Type GP** is like giving them specific blocks that only fit together in meaningful ways.

### Technical Details
In traditional GP, you might accidentally create nonsensical expressions like:
```
if (price > "hello") then buy
```

Strong Type GP prevents this by ensuring:
- **Numbers** can only be compared with **numbers**
- **Booleans** (true/false) can only be used in **logical operations**
- **Technical indicators** return the **correct data types**

### Benefits
1. **Faster Evolution**: No time wasted on impossible combinations
2. **Better Results**: Only creates mathematically valid expressions
3. **Easier to Understand**: Generated formulas make logical sense

## Project Structure

```
genetic_uptrend_discovery/
├── data/
│   ├── raw/                 # Raw stock data
│   └── processed/           # Cleaned and prepared data
├── src/
│   ├── gp/
│   │   ├── primitives.py    # GP building blocks
│   │   ├── types.py         # Strong type definitions
│   │   └── evolution.py     # Evolution engine
│   ├── indicators/
│   │   └── technical.py     # Technical analysis functions
│   └── evaluation/
│       └── fitness.py       # Fitness evaluation functions
├── notebooks/
│   └── analysis.ipynb       # Data exploration and results
├── config/
│   └── gp_config.yaml       # Evolution parameters
└── README.md
```

## Why Strong Type GP Matters for This Project

In financial data analysis, mixing up data types can lead to meaningless results. For example:
- Comparing a price (like $150.50) with a percentage (like RSI at 65%) without proper context
- Using volume data in price calculations incorrectly
- Creating impossible logical conditions

Strong Type GP ensures our evolved trading rules make mathematical and financial sense, leading to more reliable and interpretable patterns.
