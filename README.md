# Token Price Bridging  (USDC Pricing via Bitquery Streams)
This Python module processes real-time Solana transaction data from Bitquery Streams and calculates token prices in USDC

- either through direct trades with USDC 
- or by bridging through SOL (Wrapped SOL).

## How does it work?
- Extract buy/sell data from trades in Solana transactions.
- Determine if either trade side involves USDC or Wrapped SOL (WSOL).
- Compute and print token prices in USDC:
  - Directly, if USDC is part of the trade.
  - Indirectly, via bridging through SOL if only WSOL is present and a cached SOL price is available.



