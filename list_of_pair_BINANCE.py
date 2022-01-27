# This code contains the logic used to decide on the list of instrument from binance that 
# that appear on the signal bot

from configuration import *
from exchanges import *

binance = BinanceExchange(**keys['binance'])

# request quoteVolume and volume for each instrument in USDT and BTC market
output = {'symbol':[], 'quoteVolume':[]}
for i in list_of_pair:
    tick = binance.client.get_ticker(symbol=i)
    output['symbol'].append(i)
    output['quoteVolume'].append(float(tick['quoteVolume']))
tickersVolumeBinance = pd.DataFrame(output)

# create 2 different df for usdt and btc markets
maskUSDT = [i[-3:]=='SDT' for i in tickersVolumeBinance['symbol']]
maskBTC = [i[-3:]=='BTC' for i in tickersVolumeBinance['symbol']]

tickersBTC = tickersVolumeBinance[maskBTC]
tickersUSDT = tickersVolumeBinance[maskUSDT]

# isolate instrument with a quote volume higher than the market's average
mask_meanBTC = [i >= tickersBTC['quoteVolume'].mean() for i in tickersBTC['quoteVolume']]
mask_meanUSDT = [i >= tickersUSDT['quoteVolume'].mean() for i in tickersUSDT['quoteVolume']]

tickersBTC = tickersBTC[mask_meanBTC]
tickersUSDT = tickersUSDT[mask_meanUSDT]

# create the list of pair
list_symbols_USDT = [i for i in tickersUSDT['symbol']]
list_symbols_BTC = [i for i in tickersBTC['symbol']]
list_of_pair = list_symbols_USDT + list_symbols_BTC