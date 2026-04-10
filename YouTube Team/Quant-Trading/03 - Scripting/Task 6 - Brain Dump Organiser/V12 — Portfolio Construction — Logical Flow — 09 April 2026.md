# V12 — Portfolio Construction: From Signals to Positions (4 Methods Compared) — Logical Flow

**Title:** "How to Allocate Capital Across Positions: Mean-Variance vs HRP vs Black-Litterman"
**Length:** ~40 min
**Date:** 09 April 2026

---

## 1. THE HOOK (0:00–2:00)

**[INFORMATION GAIN]** "You have 100 stock signals. Which stocks should you buy? How much of each? Equal weight? Proportional to signal strength? I'll show you 4 portfolio construction methods — from naive to sophisticated — and when to use each."

---

## 2. THE STARTING POINT: 100 SIGNALS (2:00–6:00)

Each stock has:
- Fusion prediction (from V10): expected return
- Volatility forecast (from V11): risk
- Correlation matrix (how stocks move together)

**Challenge:** Construct a portfolio that maximizes Sharpe ratio given these inputs.

---

## 3. METHOD 1: EQUAL WEIGHT (6:00–10:00)

```python
def equal_weight(n_assets):
    return np.ones(n_assets) / n_assets
```

Simplest. Surprisingly robust. Popular with index funds and is a good baseline to beat.

---

## 4. METHOD 2: RISK PARITY (10:00–16:00)

"Each position contributes equally to portfolio risk."

```python
class RiskParity:
    def __init__(self, cov_matrix):
        self.cov = cov_matrix
    
    def construct(self, volatilities):
        # Allocate inversely to volatility
        weights = 1 / volatilities
        weights /= weights.sum()  # Normalize
        return weights
```

**Example:**
- Stock A: vol = 20%, weight = 1/20 = 5%
- Stock B: vol = 10%, weight = 1/10 = 10%

**Intuition:** Volatile stocks deserve smaller positions.

**Weakness:** Ignores correlations and expected returns.

---

## 5. METHOD 3: MEAN-VARIANCE (MODERN PORTFOLIO THEORY, 1952) (16:00–24:00)

"Find the portfolio that has the best return per unit of risk (highest Sharpe). 70+ years old, still used."

```python
from scipy.optimize import minimize

class MeanVarianceOptimizer:
    def __init__(self, expected_returns, cov_matrix):
        self.mu = expected_returns  # From fusion model
        self.sigma = cov_matrix  # From market data
    
    def portfolio_return(self, weights):
        return np.sum(weights * self.mu)
    
    def portfolio_vol(self, weights):
        return np.sqrt(weights @ self.sigma @ weights.T)
    
    def portfolio_sharpe(self, weights, rf_rate=0.04):
        return -(self.portfolio_return(weights) - rf_rate) / self.portfolio_vol(weights)
    
    def optimize(self):
        n = len(self.mu)
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # sum to 1
        bounds = [(0, 0.25) for _ in range(n)]  # max 25% per stock (no concentration)
        
        result = minimize(
            self.portfolio_sharpe,
            x0=np.ones(n) / n,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        return result.x
```

**Key hyperparameters:**
- `bounds = (0, 0.25)`: No short-selling, max weight 25% per stock
- Could use `bounds = (-0.10, 0.25)`: Allow 10% shorts (if your brokerage permits)

### Weakness: Concentrated positions

"Mean-variance often recommends: 25% Stock A, 25% Stock B,dropouts, 5% others."
- High turnover
- Concentrated risk
- Sensitive to small input changes

---

## 6. METHOD 4: HIERARCHICAL RISK PARITY (HRP, 2016) (24:00–32:00)

"Use machine learning (hierarchical clustering) to group correlated stocks, then allocate risk across clusters."

```python
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist

class HRP:
    def __init__(self, cov_matrix):
        # Step 1: Convert correlations to distances
        corr = (cov_matrix / np.outer(np.diag(cov_matrix)**0.5, np.diag(cov_matrix)**0.5))
        dist = np.sqrt(0.5 * (1 - corr))
        
        # Step 2: Hierarchical clustering
        self.Z = linkage(pdist(dist), method='ward')  # Z is the dendrogram
        self.leaves = get_leaves(self.Z)  # Order stocks by similarity
    
    def construct(self, volatilities):
        # Step 3: Walk down the tree, allocate inverse-volatility
        weights = np.ones(len(volatilities))
        self._recurse_tree(self.Z, volatilities, weights)
        return weights / weights.sum()
    
    def _recurse_tree(self, node, vols, weights):
        # Recursive algorithm: for each subtree, allocate based on sub-volatility
        ...
```

**Intuition:**
- Tech stocks cluster together (high correlation)
- Healthcare stocks cluster separately
- Allocate 50% to each cluster
- Within Tech cluster: allocate based on individual stock vol
- Result: diversified across sectors, risk-allocated within sectors

**Advantages:**
- Diversified (less concentrated than mean-variance)
- Robust to small input changes
- Adapts to changing correlations

**Disadvantages:**
- Ignores expected returns (purely risk-based)
- Slower to compute (hierarchical clustering)
- Less intuitive

---

## 7. BONUS: BLACK-LITTERMAN (1990) (32:00–35:00)

"Combine market-implied returns (from prices) with YOUR views."

```python
class BlackLitterman:
    def __init__(self, market_cov, market_caps):
        # Implied returns from market equilibrium
        self.market_returns = market_caps / market_caps.sum()  # Rough
    
    def update_with_views(self, view_stocks, view_returns, view_confidence):
        # If you're confident: "Tech will outperform Health by 2%"
        # Update priors using Bayes' rule
        posterior = self.bayesian_update(self.market_returns, view_returns, view_confidence)
        return posterior
```

**When to use:** When you have strong convictions about specific stock outperformance and want to embed them mathematically.

---

## 8. COMPARISON: PERFORMANCE (35:00–37:00)

```
| Method         | Annual Return | Volatility | Sharpe | Max Drawdown | Concentration |
|----------------|----------------|------------|--------|-------------------|---------------|
| Equal Weight   | 8.2%           | 12.5%      | 0.66   | -18%          | 1%            |
| Risk Parity    | 7.8%           | 11.2%      | 0.70   | -15%          | 1.2%          |
| Mean-Variance  | 9.5%           | 11.8%      | 0.81   | -22%          | 8% (concentrated) |
| HRP            | 8.9%           | 11.5%      | 0.77   | -16%          | 2%            |
| Black-Litterman| 9.1%           | 12.1%      | 0.75   | -19%          | 3%            |
```

"Mean-Variance is efficient but concentrated. HRP balance return + diversification."

---

## 9. PRODUCTION RULES (37:00–39:00)

- **Rebalance frequency:** Weekly (balance between drift and transaction costs)
- **Downside protection:** Max position size = min(0.25, 1 / sqrt(n_stocks))
- **Concentration limit:** No single stock > 10% (systemic risk safeguard)
- **Monitoring:** Track implied correlations (if they spike, recompute weights)

---

## 10. THE PAYOFF (39:00–40:00)

"Portfolio construction is the difference between a good strategy and one that survives in live trading. HRP my default — good balance of return, diversification, robustness."

"Next: The backtester. VectorBT — how to test all of this on historical data."

**CTA:**
1. "Subscribe"
2. "Comment: which portfolio method would you use?"
3. GitHub (all 4 methods, comparison code)

---

## [NEEDS MORE]

- Your portfolio weights using each method
- Performance comparison on your data
- Rebalancing transaction costs
- Specific periods where HRP outperf mean-variance
