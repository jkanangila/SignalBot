# fill manually for the instruments in the  list returned by the the main loop
# determine resistance and support levels by examining the chart.
# level = +1 if the overal trend is an uptrend (resistance)
# level = -1 if the overal trend is an support (downtrend)

from pandas import DataFrame

#  SECTION Binance
watchlistBinance = [
    {'instrument': 'BTCUSDT', 'price_level': 3946.80, 'res/supp': 1},
    {'instrument': 'ETHUSDT', 'price_level': 134.16, 'res/supp': 1},
    {'instrument': 'LTCUSDT', 'price_level': 58.64, 'res/supp': 1},
    {'instrument': 'EOSUSDT', 'price_level': 3.6583, 'res/supp': 1},
    {'instrument': 'LTCBTC', 'price_level': 0.014862, 'res/supp': 1},
    {'instrument': 'NEOBTC', 'price_level': 0.002232, 'res/supp': 1},
    {'instrument': 'MTLBTC', 'price_level': 0.0000890, 'res/supp': 1},
    {'instrument': 'EOSBTC', 'price_level': 0.0009168, 'res/supp': 1},
    {'instrument': 'ENJBTC', 'price_level': 0.00004096, 'res/supp': 1},
    {'instrument': 'IOSTBTC', 'price_level': 0.00000211, 'res/supp': 1},
    {'instrument': 'ONTBTC', 'price_level': 0.0002948, 'res/supp': 1}
                    ]
watchlistBinance = DataFrame(watchlistBinance)
watchlistBinance.set_index('instrument', inplace=True)
# !SECTION 

# SECTION Bitmex
# {'instrument': 'XBTUSD',
#     'price_level': 3998.43,
#     'res/supp': 1} 2nd res for xbt

watchlistBitmex = [
    {'instrument': 'XBTUSD', 'price_level': 3985.89, 'res/supp': 1}, 
    {'instrument': 'ETHUSD', 'price_level': 136.88, 'res/supp': 1}
]
watchlistBitmex = DataFrame(watchlistBitmex)
watchlistBitmex.set_index('instrument', inplace=True)
# !SECTION 

# SECTION Oanda
watchlistOanda = [
    {'instrument': 'SPX500_USD', 'price_level': 2806.5, 'res/supp': 1},
    {'instrument': 'UK100_GBP', 'price_level': 7214.6, 'res/supp': 1},
    {'instrument': 'NAS100_USD', 'price_level': 7336.0, 'res/supp': 1},
    {'instrument': 'XCU_USD', 'price_level': 2.84778, 'res/supp': 1},
    {'instrument': 'IN50_USD', 'price_level': 11383.0, 'res/supp': 1},
    {'instrument': 'HK33_HKD', 'price_level': 28660.4, 'res/supp': 1},
    {'instrument': 'AU200_AUD', 'price_level': 6135.0, 'res/supp': 1},
    {'instrument': 'CN50_USD', 'price_level': 12509.0, 'res/supp': 1},
    {'instrument': 'FR40_EUR', 'price_level': 5298.1, 'res/supp': 1},
    {'instrument': 'XAU_EUR', 'price_level': 1164.110, 'res/supp': 1},
    {'instrument': 'EU50_EUR', 'price_level': 3314.2, 'res/supp': 1},
    {'instrument': 'WHEAT_USD', 'price_level': 4.544, 'res/supp': -1}, 
    {'instrument': 'XAU_JPY', 'price_level': 144570, 'res/supp': 1},
    {'instrument': 'XAU_AUD', 'price_level': 1855.796, 'res/supp': 1},
    {'instrument': 'NL25_EUR', 'price_level': 545.020, 'res/supp': 1},
    {'instrument': 'XAU_CAD', 'price_level': 1767.916, 'res/supp': 1},
    {'instrument': 'TWIX_USD', 'price_level': 388.3, 'res/supp': 1},
    {'instrument': 'GBP_USD', 'price_level': 1.32218, 'res/supp': 1},
    {'instrument': 'GBP_JPY', 'price_level': 145.484, 'res/supp': 1},
    {'instrument': 'NZD_USD', 'price_level': 0.68931, 'res/supp': 1},
    {'instrument': 'GBP_AUD', 'price_level': 1.86713, 'res/supp': 1},
    {'instrument': 'EUR_GBP', 'price_level': 0.85319, 'res/supp': -1},
    {'instrument': 'GBP_CAD', 'price_level': 1.77469, 'res/supp': 1},
    {'instrument': 'EUR_NZD', 'price_level': 1.63785, 'res/supp': -1},
    {'instrument': 'NZD_CAD', 'price_level': 0.92389, 'res/supp': 1},
    {'instrument': 'AUD_NZD', 'price_level': 1.02932, 'res/supp': -1},
    {'instrument': 'GBP_CHF', 'price_level': 1.31454, 'res/supp': 1},
    {'instrument': 'AUD_CHF', 'price_level': 0.70336, 'res/supp': -1},
    {'instrument': 'NZD_CHF', 'price_level': 0.68455, 'res/supp': 1},
    {'instrument': 'GBP_PLN', 'price_level': 5.03851, 'res/supp': 1},
    {'instrument': 'USD_INR', 'price_level': 69.037, 'res/supp': -1},
    {'instrument': 'USD_SGD', 'price_level': 1.35135, 'res/supp': -1},
    {'instrument': 'AUD_SGD', 'price_level': 0.95707, 'res/supp': -1},
    {'instrument': 'USD_CNH', 'price_level': 6.71429, 'res/supp': -1},
    {'instrument': 'USD_SEK', 'price_level': 9.29139, 'res/supp': 1},
    {'instrument': 'EUR_SGD', 'price_level': 1.52543, 'res/supp': -1},
    {'instrument': 'GBP_SGD', 'price_level': 1.78761, 'res/supp': 1},
    {'instrument': 'GBP_ZAR', 'price_level': 19.19162, 'res/supp': 1},
    {'instrument': 'EUR_HUF', 'price_level': 315.567, 'res/supp': -1},
    {'instrument': 'DE30_EUR', 'price_level': 11390.8, 'res/supp': 1}
] # NOTE (FIXME: Additional review) XCU_USD, IN50_USD, HK33_HKD, 
# AU200_AUD, CN50_USD, FR40_EUR, EU50_EUR, XAU_AUD, XAU_CAD, TWIX_USD,
# NZD_USD, EUR_GBP, GBP_CAD, NZD_CAD, GBP_CHF, USD_INR, USD_CNH, USD_SEK,
# GBP_ZAR, EUR_HUF
watchlistOanda = DataFrame(watchlistOanda)
watchlistOanda.set_index('instrument', inplace=True)
# !SECTION 


# SECTION Poloniex
watchlistPoloniex = [
    {'instrument': 'BTC_DGB', 'price_level': 0.00000318, 'res/supp': 1},
    {'instrument': 'ETH_CVC', 'price_level': 0.00060552, 'res/supp': 1}, 
    {'instrument': 'ETH_EOS', 'price_level': 0.02691585, 'res/supp': 1}
]
watchlistPoloniex = DataFrame(watchlistPoloniex)
watchlistPoloniex.set_index('instrument', inplace=True)
# !SECTION 