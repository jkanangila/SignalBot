import datetime 

# ANCHOR keys dictionary
keys = {}

# ANCHOR Paramas dictionary
params_binance = {

                'longterm': {"timeframe": '1 year ago UTC', "interval": '1d'},
                'itermediate': {"timeframe": '7 day ago UTC', "interval": '30m'},
                'short': {"timeframe": '2 day ago UTC', "interval": '5m'}
        
        }

params_bitmex = {

                'longterm': {"count": 300, "binSize": '1d'},
                'itermediate': {"count": 300, "binSize": '1h'},
                'short': {"count": 300, "binSize": '5m'}
    
        }

params_oanda = {

                'longterm': {"count": 300, "granularity": 'D'},
                'itermediate': {"count": 300, "granularity": 'M30'},
                'short': {"count": 300, "granularity": 'M5'}
    
        }

params_poloniex = {

                'longterm': {'period' : 24*60*60, 'end' : datetime.datetime.now(), 
                            'start' : [datetime.datetime.now() - 200*datetime.timedelta(days=1)]},
                'itermediate': {'period' : 30*60, 'end' : datetime.datetime.now(),
                            'start' : [datetime.datetime.now() - 7*datetime.timedelta(days=1)]},
                'short': {'period' : 5*60, 'end' : datetime.datetime.now(),
                            'start' : [datetime.datetime.now() - 2*datetime.timedelta(days=1)]}
                            
                            }

# ANCHOR Binance
# list_of_tuples = [
#         ('ADAUSDT', 5, 1), ('BCHABCUSDT', 2, 5), ('BCHSVUSDT', 2, 5), ('BNBUSDT', 4, 2), ('BTCUSDT', 2, 6),
#         ('EOSUSDT', 4, 2), ('ETCUSDT', 4, 2), ('ETHUSDT', 2, 5), ('ICXUSDT', 4, 2), ('IOTAUSDT', 4, 2), 
#         ('LTCUSDT', 2, 5), ('NEOUSDT', 3, 3), ('NULSUSDT', 4, 2), ('ONTUSDT', 3, 3), ('QTUMUSDT', 3, 3),
#         ('TRXUSDT', 5, 1), ('VETUSDT', 5, 1), ('XLMUSDT', 5, 1), ('XRPUSDT', 5, 1)
#                     ] 
#                     #  (Symbol, price, quantity)

list_of_pair = [
    'ETHBTC', 'LTCBTC', 'BNBBTC', 'NEOBTC', 'BCCBTC', 'GASBTC', 'BTCUSDT', 'ETHUSDT', 'HSRBTC', 'MCOBTC', 
    'WTCBTC', 'LRCBTC', 'QTUMBTC', 'YOYOBTC', 'OMGBTC', 'ZRXBTC', 'STRATBTC', 'SNGLSBTC', 'BQXBTC', 'KNCBTC', 
    'FUNBTC', 'SNMBTC', 'IOTABTC', 'LINKBTC', 'XVGBTC', 'SALTBTC', 'MDABTC', 'MTLBTC', 'SUBBTC', 'EOSBTC', 
    'SNTBTC', 'ETCBTC', 'MTHBTC', 'ENGBTC', 'DNTBTC', 'ZECBTC', 'BNTBTC', 'ASTBTC', 'DASHBTC', 'OAXBTC', 
    'ICNBTC', 'BTGBTC', 'EVXBTC', 'REQBTC', 'VIBBTC', 'TRXBTC', 'POWRBTC', 'ARKBTC', 'XRPBTC', 'MODBTC', 
    'ENJBTC', 'STORJBTC', 'BNBUSDT', 'VENBTC', 'KMDBTC', 'RCNBTC', 'NULSBTC', 'RDNBTC', 'XMRBTC', 'DLTBTC', 
    'AMBBTC', 'BCCUSDT', 'BATBTC', 'BCPTBTC', 'ARNBTC', 'GVTBTC', 'CDTBTC', 'GXSBTC', 'NEOUSDT', 'POEBTC', 
    'QSPBTC', 'BTSBTC', 'XZCBTC', 'LSKBTC', 'TNTBTC', 'FUELBTC', 'MANABTC', 'BCDBTC', 'DGDBTC', 'ADXBTC', 
    'ADABTC', 'PPTBTC', 'CMTBTC', 'XLMBTC', 'CNDBTC', 'LENDBTC', 'WABIBTC', 'LTCUSDT', 'TNBBTC', 'WAVESBTC', 
    'GTOBTC', 'ICXBTC', 'OSTBTC', 'ELFBTC', 'AIONBTC', 'NEBLBTC', 'BRDBTC', 'EDOBTC', 'WINGSBTC', 'NAVBTC', 
    'LUNBTC', 'TRIGBTC', 'APPCBTC', 'VIBEBTC', 'RLCBTC', 'INSBTC', 'PIVXBTC', 'IOSTBTC', 'CHATBTC', 'STEEMBTC', 
    'NANOBTC', 'VIABTC', 'BLZBTC', 'AEBTC', 'RPXBTC', 'NCASHBTC', 'POABTC', 'ZILBTC', 'ONTBTC', 'STORMBTC', 
    'QTUMUSDT', 'XEMBTC', 'WANBTC', 'WPRBTC', 'QLCBTC', 'SYSBTC', 'GRSBTC', 'ADAUSDT', 'CLOAKBTC', 'GNTBTC', 
    'LOOMBTC', 'XRPUSDT', 'BCNBTC', 'REPBTC', 'TUSDBTC', 'ZENBTC', 'SKYBTC', 'EOSUSDT', 'CVCBTC', 'THETABTC', 
    'TUSDUSDT', 'IOTAUSDT', 'XLMUSDT', 'IOTXBTC', 'QKCBTC', 'AGIBTC', 'NXSBTC', 'DATABTC', 'ONTUSDT', 'TRXUSDT', 
    'ETCUSDT', 'ICXUSDT', 'SCBTC', 'NPXSBTC', 'VENUSDT', 'KEYBTC', 'NASBTC', 'MFTBTC', 'DENTBTC', 'ARDRBTC', 
    'NULSUSDT', 'HOTBTC', 'VETBTC', 'VETUSDT', 'DOCKBTC', 'POLYBTC', 'PHXBTC', 'HCBTC', 'GOBTC', 'PAXBTC', 
    'PAXUSDT', 'RVNBTC', 'DCRBTC', 'USDCBTC', 'MITHBTC', 'BCHABCBTC', 'BCHSVBTC', 'BCHABCUSDT', 'BCHSVUSDT', 
    'RENBTC', 'USDCUSDT', 'LINKUSDT', 'WAVESUSDT', 'BTTBTC', 'BTTUSDT', 'USDSUSDT', 'ONGBTC', 'ONGUSDT', 
    'HOTUSDT', 'ZILUSDT', 'ZRXUSDT', 'FETBTC', 'FETUSDT', 'BATUSDT'
                ]

list_of_pair_v2 = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'LTCUSDT', 'ADAUSDT', 'XRPUSDT', 'EOSUSDT', 'XLMUSDT', 'BTTUSDT', 
    'ETHBTC', 'LTCBTC', 'BNBBTC', 'MCOBTC', 'KNCBTC', 'LINKBTC', 'MDABTC', 'EOSBTC', 'TRXBTC', 'ARKBTC', 
    'XRPBTC', 'ENJBTC', 'STORJBTC', 'ARNBTC', 'ADABTC', 'XLMBTC', 'ICXBTC', 'BRDBTC', 'VIABTC', 'WANBTC', 
    'GRSBTC', 'LOOMBTC', 'TUSDBTC', 'CVCBTC', 'THETABTC', 'RVNBTC', 'BTTBTC', 'FETBTC'
                ]

# list_of_pair = [i[0] for i in list_of_tuples]
# price_dcmls = [j[1] for j in list_of_tuples]
# qty_dcmls =  [j[2] for j in list_of_tuples]



# ANCHOR  Bitmex
# LTCH19, TRXH19,  too volatile
#longterm_binSize = '6h'
# list_of_symbols = ['XBTUSD', 'XBTJPY', 'ADAH19', 'BCHH19', 'EOSH19', 'ETHXBT', 'XRPH19' ]
list_of_symbols = ['XBTUSD', 'ETHUSD' ]



# ANCHOR Oanda
list_of_instruments = [

                        'XAU_USD', 'US30_USD', 'JP225_USD', 'BCO_USD', 'WTICO_USD', 'SPX500_USD', 'UK100_GBP', 'NATGAS_USD',  
                        'NAS100_USD', 'XAG_USD', 'XCU_USD', 'IN50_USD', 'XPT_USD', 'HK33_HKD', 'XPD_USD', 'AU200_AUD', 
                        'CN50_USD', 'FR40_EUR', 'XAU_EUR', 'SOYBN_USD', 'SUGAR_USD', 'US2000_USD', 'EU50_EUR', 'WHEAT_USD', 
                        'CORN_USD', 'XAU_SGD', 'XAU_JPY', 'XAU_AUD', 'DE10YB_EUR', 'XAG_EUR', 'XAU_XAG', 'SG30_SGD',  
                        'NL25_EUR', 'XAU_GBP', 'XAU_CAD', 'TWIX_USD', 'USB30Y_USD', 'UK10YB_GBP', 'XAG_CAD', 'XAU_CHF',
                        'XAG_GBP', 'XAU_NZD', 'USB02Y_USD', 'XAG_AUD', 'USB05Y_USD', 'XAG_SGD', 'XAG_NZD', 'XAG_CHF', 
                        'EUR_USD', 'USD_JPY', 'GBP_USD', 'GBP_JPY', 'AUD_USD', 'USD_THB', 'EUR_JPY', 'NZD_USD', 'USD_CHF', 
                        'AUD_JPY', 'GBP_AUD', 'EUR_GBP', 'EUR_AUD', 'EUR_CAD', 'GBP_NZD', 'GBP_CAD', 'EUR_NZD', 'AUD_CAD', 
                        'CAD_JPY', 'NZD_JPY', 'NZD_CAD', 'AUD_NZD', 'GBP_CHF', 'EUR_CHF', 'CAD_CHF', 'AUD_CHF', 'NZD_CHF', 
                        'CHF_JPY', 'GBP_PLN', 'USD_TRY', 'USD_MXN', 'USD_PLN', 'USD_INR', 'USD_SGD', 'USD_ZAR', 'EUR_PLN', 
                        'EUR_ZAR', 'AUD_SGD', 'USD_NOK', 'USD_CNH', 'USD_SEK', 'EUR_SGD', 'EUR_TRY', 'GBP_SGD', 'GBP_ZAR', 
                        'SGD_JPY', 'TRY_JPY', 'EUR_HUF', 'USD_DKK', 'DE30_EUR', 'USB10Y_USD',
                    
                    ]

# ANCHOR Poloniex

list_of_tickers = [
    
                        'BTC_BCN', 'BTC_BTS', 'BTC_BURST', 'BTC_CLAM', 'BTC_DASH', 'BTC_DGB', 'BTC_DOGE', 'BTC_GAME', 
                        'BTC_HUC', 'BTC_LTC', 'BTC_MAID', 'BTC_OMNI', 'BTC_NAV', 'BTC_NMC', 'BTC_NXT', 'BTC_PPC', 
                        'BTC_STR', 'BTC_SYS', 'BTC_VIA', 'BTC_VTC', 'BTC_XCP', 'BTC_XEM', 'BTC_XMR', 'BTC_XPM', 
                        'BTC_XRP', 'USDT_BTC', 'USDT_DASH', 'USDT_LTC', 'USDT_NXT', 'USDT_STR', 'USDT_XMR', 'USDT_XRP',
                        'XMR_BCN', 'XMR_DASH', 'XMR_LTC', 'XMR_MAID', 'XMR_NXT', 'BTC_ETH', 'USDT_ETH', 'BTC_SC', 
                        'BTC_FCT', 'BTC_DCR', 'BTC_LSK', 'ETH_LSK', 'BTC_LBC', 'BTC_STEEM', 'ETH_STEEM', 'BTC_SBD', 
                        'BTC_ETC', 'ETH_ETC', 'USDT_ETC', 'BTC_REP', 'USDT_REP', 'ETH_REP', 'BTC_ARDR', 'BTC_ZEC', 
                        'ETH_ZEC', 'USDT_ZEC', 'XMR_ZEC', 'BTC_STRAT', 'BTC_PASC', 'BTC_GNT', 'ETH_GNT', 'BTC_BCH',
                        'ETH_BCH', 'USDT_BCH', 'BTC_ZRX', 'ETH_ZRX', 'BTC_CVC', 'ETH_CVC', 'BTC_OMG', 'ETH_OMG', 
                        'BTC_GAS', 'ETH_GAS', 'BTC_STORJ', 'BTC_EOS', 'ETH_EOS', 'USDT_EOS', 'BTC_SNT', 'ETH_SNT',
                        'USDT_SNT', 'BTC_KNC', 'ETH_KNC', 'USDT_KNC', 'BTC_BAT', 'ETH_BAT', 'USDT_BAT', 'BTC_LOOM',
                        'ETH_LOOM', 'USDT_LOOM', 'USDT_DOGE', 'USDT_GNT', 'USDT_LSK', 'USDT_SC', 'USDT_ZRX', 'BTC_QTUM',
                        'ETH_QTUM', 'USDT_QTUM', 'USDC_BTC', 'USDC_ETH', 'USDC_USDT', 'BTC_MANA', 'ETH_MANA', 'USDT_MANA',
                        'BTC_BNT', 'ETH_BNT', 'USDT_BNT', 'USDC_BCH', 'BTC_BCHABC', 'USDC_BCHABC', 'BTC_BCHSV', 
                        'USDC_XRP', 'USDC_XMR', 'USDC_STR', 'USDC_DOGE', 'USDC_LTC', 'USDC_ZEC', 'BTC_FOAM', 'USDC_FOAM', 
                        'BTC_NMR', 'BTC_POLY', 'BTC_LPT', 'BTC_GRIN', 'USDC_GRIN', 'BTC_ATOM', 'USDC_ATOM', 'USDC_BCHSV'
    
                      ]

list_of_tickers2 = [
        
                        'BTC_BCN', 'BTC_BURST', 'BTC_DGB', 'BTC_DOGE', 'BTC_STR', 'BTC_XEM', 'BTC_XRP', 
                        'BTC_SC', 'USDT_NXT', 'USDT_STR', 'USDT_XRP', 'USDT_DOGE', 'USDT_SC', 'USDC_USDT', 
                        'USDC_XRP', 'USDC_STR', 'ETH_GNT', 'ETH_KNC', 'ETH_LOOM', 'ETH_MANA', 'XMR_BCN', 
                        'XMR_NXT'
        
                        ]

# ANCHOR color dict
color = {
                'black' : '#000000',
                'white' : '#FFFFFF',
                'maroon' : '#800000',
                'green' : '#008000',
                'navy' : '#000080',
                'silver' : '#C0C0C0',
                'red' : '#FF0000',
                'lime' : '#00FF00',
                'blue' : '#0000FF',
                'gray' : '#808080',
                'purple' : '#800080',
                'olive' : '#808000',
                'teal' : '#008080',
                'fuchsia' : '#FF00FF',
                'yellow' : '#FFFF00',
                'aqua' : '#00FFFF',
                'orange' : '#FF9900'
        }
