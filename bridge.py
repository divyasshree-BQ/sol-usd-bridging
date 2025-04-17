from convert import convert_bytes
# Add this global variable
last_sol_price_in_usdc = None


WSOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

def is_wsol(mint_address_bytes):
    return convert_bytes(mint_address_bytes) == WSOL_MINT

def is_usdc(mint_address_bytes):
    return convert_bytes(mint_address_bytes) == USDC_MINT

def bridge_trade_prices(tx_block):
    global last_sol_price_in_usdc
   
    for tx in tx_block.Transactions:
        print(convert_bytes(tx.Signature))
       
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

            buy_is_usdc = is_usdc(buy_currency.MintAddress)
            sell_is_usdc = is_usdc(sell_currency.MintAddress)

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
