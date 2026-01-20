# %%
"""
# Foreign Exchange Daily Returns Summary

Daily returns for USD invested in foreign currencies via overnight repo markets.
"""

# %%
import sys
sys.path.insert(0, "./src")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import chartbook

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"

# %%
"""
## Methodology

The FX return strategy converts USD to a foreign currency at end of day t-1,
invests in that currency's overnight repo market, then converts back to USD on day t.

$$
ret_{t,i} = \\frac{spot_{t-1,i}}{spot_{t,i}} \\times fret_{t,i}
$$

Where:
- $i$ is the foreign currency
- $ret$ is the return of USD invested in the foreign currency
- $fret$ is the return of the foreign currency in overnight repo market
- $spot$ is the spot price (how much 1 USD is worth in the foreign currency)

### Data Sources

- Bloomberg FX spot rates
- Bloomberg interest rates (OIS)
"""

# %%
"""
## Data Overview
"""

# %%
df = pd.read_parquet(DATA_DIR / "ftsfr_fx_returns.parquet")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nDate range: {df['ds'].min()} to {df['ds'].max()}")
print(f"Number of currencies: {df['unique_id'].nunique()}")

# %%
# Show currencies
print("\nCurrencies:")
for ccy in sorted(df['unique_id'].unique()):
    print(f"  {ccy}")

# %%
"""
### Summary Statistics
"""

# %%
# Pivot to wide format for analysis
fx_wide = df.pivot(index='ds', columns='unique_id', values='y')
fx_stats = fx_wide.describe().T
fx_stats['skewness'] = fx_wide.skew()
fx_stats['kurtosis'] = fx_wide.kurtosis()
print(fx_stats[['mean', 'std', 'min', 'max', 'skewness', 'kurtosis']].round(4).to_string())

# %%
"""
### FX Returns Time Series
"""

# %%
# Plot returns by currency group
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Major currencies
major = ['EUR_return', 'GBP_return', 'JPY_return']
axes[0, 0].set_title('Major Currencies')
for ccy in major:
    if ccy in fx_wide.columns:
        axes[0, 0].plot(fx_wide.index, fx_wide[ccy], label=ccy.replace('_return', ''), alpha=0.7)
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Commodity currencies
commodity = ['AUD_return', 'CAD_return', 'NZD_return']
axes[0, 1].set_title('Commodity Currencies')
for ccy in commodity:
    if ccy in fx_wide.columns:
        axes[0, 1].plot(fx_wide.index, fx_wide[ccy], label=ccy.replace('_return', ''), alpha=0.7)
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# European currencies
european = ['CHF_return', 'SEK_return', 'EUR_return']
axes[1, 0].set_title('European Currencies')
for ccy in european:
    if ccy in fx_wide.columns:
        axes[1, 0].plot(fx_wide.index, fx_wide[ccy], label=ccy.replace('_return', ''), alpha=0.7)
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# USD reference
axes[1, 1].set_title('USD Return (Reference)')
if 'USD_return' in fx_wide.columns:
    axes[1, 1].plot(fx_wide.index, fx_wide['USD_return'], alpha=0.7)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(DATA_DIR.parent / "_output" / "fx_returns.png", dpi=150, bbox_inches='tight')
plt.show()

# %%
"""
### Correlation Matrix
"""

# %%
fig, ax = plt.subplots(figsize=(10, 8))
corr = fx_wide.corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax)
ax.set_title('FX Returns Correlations')
plt.tight_layout()
plt.savefig(DATA_DIR.parent / "_output" / "fx_correlation.png", dpi=150, bbox_inches='tight')
plt.show()

# %%
"""
## Data Definitions

### FX Returns (ftsfr_fx_returns)

| Variable | Description |
|----------|-------------|
| unique_id | Currency identifier (e.g., EUR_return, GBP_return) |
| ds | Date |
| y | Daily annualized return (percent) |

### Currency Codes

| Code | Currency |
|------|----------|
| AUD | Australian Dollar |
| CAD | Canadian Dollar |
| CHF | Swiss Franc |
| EUR | Euro |
| GBP | British Pound |
| JPY | Japanese Yen |
| NZD | New Zealand Dollar |
| SEK | Swedish Krona |
| USD | US Dollar |
"""
