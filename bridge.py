from convert import convert_bytes
# Add this global variable
last_sol_price_in_usdc = None

# Add WSOL constant
WSOL_MINT = "So11111111111111111111111111111111111111112"
USDC_SYMBOL = "USDC"

def is_wsol(mint_address_bytes):
    return convert_bytes(mint_address_bytes) == WSOL_MINT

def bridge_trade_prices(tx_block):
    global last_sol_price_in_usdc
    # print(tx_block)
    for tx in tx_block.Transactions:
        print(tx.Signature)
        # print(tx.Trades)
        for trade in tx.Trades:
            if not (trade.HasField("Buy") and trade.HasField("Sell")):
                continue

            buy = trade.Buy
            sell = trade.Sell

            if not (buy.HasField("Currency") and sell.HasField("Currency")):
                continue

            buy_currency = buy.Currency
            sell_currency = sell.Currency

            try:
                buy_amount = buy.Amount / (10 ** buy_currency.Decimals)
                sell_amount = sell.Amount / (10 ** sell_currency.Decimals)
            except ZeroDivisionError:
                continue

            if buy_amount == 0 or sell_amount == 0:
                continue

            buy_is_usdc = buy_currency.Symbol == USDC_SYMBOL
            sell_is_usdc = sell_currency.Symbol == USDC_SYMBOL
            buy_is_sol = is_wsol(buy_currency.MintAddress)
            sell_is_sol = is_wsol(sell_currency.MintAddress)

            if buy_is_usdc or sell_is_usdc:
                token_price_in_usdc = (buy_amount / sell_amount) if buy_is_usdc else (sell_amount / buy_amount)
                token_name = sell_currency.Symbol if buy_is_usdc else buy_currency.Symbol

                print(f"Token {token_name} price in USDC: {token_price_in_usdc}")

                if buy_is_sol or sell_is_sol:
                    last_sol_price_in_usdc = (sell_amount / buy_amount) if buy_is_sol else (buy_amount / sell_amount)
                    print(f"Updated SOL price in USDC => {last_sol_price_in_usdc:.6f}")

            elif buy_is_sol or sell_is_sol:
                if last_sol_price_in_usdc is not None:
                    token_in_sol = (buy_amount / sell_amount) if buy_is_sol else (sell_amount / buy_amount)
                    token_name = sell_currency.Symbol if buy_is_sol else buy_currency.Symbol
                    token_price_in_usdc = token_in_sol * last_sol_price_in_usdc
                    print(f"Token {token_name} price in USDC (via SOL bridging): {token_price_in_usdc}")
