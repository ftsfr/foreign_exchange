# Foreign Exchange Returns

Daily FX returns for USD invested in foreign currencies via overnight repo markets.

## Overview

This pipeline calculates FX returns using the strategy:

```
ret_{t,i} = (spot_{t-1,i} / spot_{t,i}) × fret_{t,i}
```

Where:
- spot: Exchange rate (how much 1 USD is worth in foreign currency)
- fret: Foreign currency return in overnight repo market

## Currencies

- AUD (Australian Dollar)
- CAD (Canadian Dollar)
- CHF (Swiss Franc)
- EUR (Euro)
- GBP (British Pound)
- JPY (Japanese Yen)
- NZD (New Zealand Dollar)
- SEK (Swedish Krona)
- USD (US Dollar)

## Data Sources

- **Bloomberg**: FX spot rates and OIS interest rates

## Outputs

- `ftsfr_fx_returns.parquet`: Daily FX returns for all currencies

## Requirements

- Bloomberg Terminal running
- Python 3.10+
- xbbg package

## Setup

1. Ensure Bloomberg Terminal is running
2. Install dependencies: `pip install -r requirements.txt`
3. Run pipeline: `doit`

## Credits

Code adapted with permission from https://github.com/Kunj121/CIP
