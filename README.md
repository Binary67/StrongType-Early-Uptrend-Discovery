# Strongly‑Typed Genetic Programming for Early Uptrend Detection

> **Goal:** Evolve symbolic trading rules that can spot the *precursors* of an EMA‑12/EMA‑50 bullish crossover **1–10 trading days** in advance, across any daily‑bar asset class, while rewarding rules that precede **longer‑lasting** uptrends and produce attractive risk‑adjusted returns.

---

## Table of Contents

1. [Why This Project?](#why-this-project)
2. [How It Works](#how-it-works)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Directory Layout](#directory-layout)
6. [Scoring & Fitness](#scoring--fitness)
7. [Extending the Indicator Set](#extending-the-indicator-set)
8. [Development & Contributing](#development--contributing)

---

## Why This Project?

Financial markets rarely telegraph sustained rallies with a single indicator.  By letting *Strongly Typed Genetic Programming* (STGP) invent composite signals—while rigorously enforcing sensible data types—we can discover early patterns that human chart‑readers may miss.  The end result is a transparent algebraic rule that fires up to **10 days** before a classic EMA crossover, giving traders a precious head‑start.

---

## How It Works

```
flowchart TD
    subgraph Training Pipeline
        A[Daily OHLCV Loader] --> B[Feature Matrix Builder]
        B --> C[Typed GP Engine (DEAP)]
        C --> D[Rule Candidate]
        D --> E[Walk‑Forward Backtester (backtesting.py)]
        E --> F[Fitness Scorer]
        F -->|Sharpe, ReturnPct, Lead & Confirm| C
    end
    C --> G[Best Individual.pkl]
    subgraph Inference
        H[Live Daily Bar] --> I[Rule Evaluation]
        I --> J[Signal: Uptrend Imminent?]
    end
```

* **Typed GP Engine:** Uses DEAP’s strongly‑typed primitives so, e.g., *EMA(Price, Window)* is always legal, while nonsensical calls are impossible.
* **Indicator Library:** Starts small—see below—but the type system makes it easy to add more.
* **Walk‑Forward Testing:** Sequential, expanding‑window evaluation mirrors a live trading scenario.
* **Backtesting:** Delegated to **backtesting.py** for fast vectorised equity‑curve computation.

---

> **Tip:** All artefacts (logs, configs, pickled individuals, equity curves) land in `runs/<timestamp>/` for tidy experiment management.

---

## Configuration

All runtime options live in a single YAML file.  Values below are *sensible defaults*—tweak freely.

```yaml
# configs/default.yaml
Data:
  Source: "yfinance"            # or "csv", "alpha_vantage", ...
  Tickers: ["AAPL"]             # any number of symbols
  Start: "2000-01-01"
  End:   "2025-01-01"

Indicators:                     # initial menu – add more anytime
  - {Name: "EMA",  Inputs: ["Close"],  Window: 12}
  - {Name: "EMA",  Inputs: ["Close"],  Window: 50}
  - {Name: "RSI",  Inputs: ["Close"],  Window: 14}
  - {Name: "ATR",  Inputs: ["High", "Low", "Close"], Window: 14}
  - {Name: "BBANDS", Inputs: ["Close"], Window: 20, Std: 2}

GP:
  PopulationSize: 300
  NumGenerations: 40
  TournamentSize: 5
  CrossoverProb:  0.90
  MutationProb:   0.10

Fitness:
  Weights: {Lead: 0.30, Confirm: 0.30, Sharpe: 0.20, ReturnPct: 0.20}
  MaxConfirmDays: 20              # cut‑off for bonus credits

WalkForward:
  TrainWindow:  4y                # Sliding training window length
  TestWindow:   1y                # Out‑of‑sample window length
```

> **PascalCase Everywhere:** Variable names in code follow the **PascalCase** convention to honour internal style rules.

---

## Directory Layout

```text
stgp‑uptrend/
├─ backtest/            # Thin wrappers around backtesting.py
├─ configs/
│   └─ default.yaml
├─ data/                # Raw & processed CSV cache
├─ gp/
│   ├─ primitives.py    # Strongly‑typed nodes & protected ops
│   ├─ engine.py        # GP setup, evolution loop
│   └─ scoring.py       # Lead/confirm + trading‑metric fitness
├─ indicators/
│   └─ ta.py            # EMA, RSI, ATR, …
├─ runs/                # Auto‑created experiment folders
├─ scripts/
│   ├─ fetch_data.py
│   └─ plot_equity.py
└─ main.py              # Entry point – `python main.py --config ‹yaml›`
```

---

## Scoring & Fitness

```text
LeadScore     = (clip(LeadDays, 1, 10) / 10)             # 10d early ⇒ 1.0
ConfirmScore  = (clip(ConfirmDays, 1, MaxConfirm) / MaxConfirm)
TradingScore  = Sharpe * 1.0                              # Risk‑adjusted edge
ReturnScore   = FinalReturnPct / 100.0                   # Scale 0‑1
TotalFitness  = Σ(Weight_i × Score_i) – IndividualSize × 1e‑4
```

*Signals firing >10 days ahead receive ****0 LeadScore****; those firing ≤0 days ahead are outright false‑positives.*  A tiny parsimony penalty (`IndividualSize × 1e‑4`) discourages bloated trees.

---

## Extending the Indicator Set

1. Add a function in `indicators/ta.py`, with a precise type signature (`float[] → float`).
2. Register it in `gp/primitives.py` using DEAP’s `addPrimitive` along with an appropriate return type.
3. Reference it in your YAML.

Because every primitive is strongly typed, nonsensical expressions (e.g., `EMA(RSI, ATR)`) won’t compile.

---

## Roadmap:

  * Expand indicator catalog (MACD, OBV, Keltner Channels…).
  * Add Bayesian‑optimised hyper‑parameter tuner.
  * Support intraday bar compression.
