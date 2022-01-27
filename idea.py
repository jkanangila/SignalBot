from configuration import *
from exchanges import *
from pause import seconds

from strategy_TendAlignment import *
from watchlistConfg import *

binance = BinanceExchange(**keys['binance'])

# SECTION Binance exchange
binance_watchlst = {
    'symbol': ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'EOSUSDT', 'LTCBTC', 'NEOBTC',
            'MTLBTC', 'EOSBTC', 'ENJBTC', 'IOSTBTC', 'ONTBTC'], 

    'long_term':['uptrend', 'uptrend', 'uptrend', 'uptrend',
                 'uptrend', 'uptrend', 'uptrend', 'uptrend',
                 'uptrend','uptrend','uptrend']}  # NOTE should be a pd df

binance_watchlst = pd.DataFrame(binance_watchlst)
list_of_levels = []
for instrument, trend in zip(binance_watchlst['symbol'], 
                                     binance_watchlst['long_term']):
    # request ohlc data from the exchange
    print('Requesting ohlc data for %s' % instrument)
    ohlc = binance.get_klines(pair=instrument,
                                         **params_binance['short'])
    ohlc2 = ohlc[-120:]
    print('    success')
    
    # determine the short-term trend over the last 2 days
    print('Deciding on short-term trend for the last 2 days')
    sTrend = Strategy().short_term_trend(ohlc)
    print('    success')
    
    if trend[1] == 'uptrend':
        # determine the key level using the resistance_level method
        # from the Strategy module
        print('computing resistance level')
        key_level = Strategy().resistance_level(datafr=ohlc2, trend=trend)
        
        # if the level has been test more than 4 times keep value else discard
        if Strategy().key_level_test(level=key_level, datafr=ohlc2) > 4:
            print('testing strength of resistance level')
            list_of_levels.append(key_level)
        else:
            list_of_levels.append('N/A')
    
    elif trend[1] == 'downtrend':
        # determine the key level using the support_level method
        # from the Strategy module
        key_level = Strategy().support_level(datafr=ohlc2, trend=trend)
        
        # if the level has been test more than 4 times keep value else discard
        if Strategy().key_level_test(level=key_level, datafr=ohlc2) > 4:
            list_of_levels.append(key_level)
        else:
            list_of_levels.append('N/A')
            
    else:
        list_of_levels.append('N/A')
        
binance_watchlst['key levels'] = list_of_levels
print('Process completed')