from signal_scanner import SignalScanner
from utils import log_exectime

stocks = ["MARA", "MSTR", "AAPL", "COIN", "CNSWF", "Bitcoin USD", "Ethereum USD"]
sig_types = ["MA", "RSI", "BB"]

ss = SignalScanner(stocks)

@log_exectime
def main():
    for sig in sig_types:
        ss.scan(sig)
            
if __name__ == "__main__":
    main()
