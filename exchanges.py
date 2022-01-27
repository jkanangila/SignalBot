""" Changes:    1. Added functions to plot using matplotlib
v1.4.0
"""

import datetime
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bitmex
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import oandapyV20.endpoints.trades as trades
import pandas as pd
from binance.client import Client
from mpl_finance import candlestick2_ohlc
from oandapyV20 import API  # the client
from oandapyV20.contrib.factories import InstrumentsCandlesFactory
from poloniex.poloniex import Poloniex
from scipy.signal import argrelmax, argrelmin

import configuration as config


# SECTION  OandaExchange
class OandaExchange(object):
    
    def __init__(self, access_token, accountID, environment=None):
        "default environment is live"
        self.access_token = access_token
        self.accountID = accountID
        if environment == None:
            self.environment = 'live'
        else:
            self.environment = environment
    
    def Client(self):
        return API(access_token=self.access_token, environment=self.environment)
    
    def TradesList(self):
        r = trades.TradesList(self.accountID)
        return self.Client().request(r)
    
    # @staticmethod
    # def Time_strp(timeSTR):
    #     _format = "%Y-%m-%dT%H:%M:%S"
    #     _interm = timeSTR.replace('.', ' ').split(' ')[0]
    #     return datetime.datetime.strptime(_interm,_format)

    @staticmethod
    def parse_time(datetimeStr):
        newStr = datetimeStr.split('.')[0] + 'Z'
        return datetime.datetime.strptime(newStr, '%Y-%m-%dT%H:%M:%SZ')

    def curr_price(self, symbol):
        InstrumentsCandles = []
        for r in InstrumentsCandlesFactory(
                instrument=symbol,
                params={"count": 1, "granularity": 'M1'}):
            t = self.Client().request(r)
            InstrumentsCandles.append(t)
            
        return float(InstrumentsCandles[0]['candles'][0]['mid']['c'])
    
    def CandlesticksData(self, instrument, params):
        # iterate through the generator to get price data
        # the exchange places various information in a dictionary. The  next of codes is to get these data to the
        # right format
        InstrumentsCandles = []
        for r in InstrumentsCandlesFactory(instrument=instrument,params=params):
            t = self.Client().request(r)
            InstrumentsCandles.append(t)
        
        # select the candlestick values from the returned dictionary
        kline = InstrumentsCandles[0]['candles']
        
        # extract the actual ohlc value and place it in a dataframe
        ohlc_list = []
        for i in range(len(kline)):
            element = kline[i]['mid']
            interm_dict = {
                'o':float(element['o']), 'h':float(element['h']),
                'l': float(element['l']), 'c': float(element['c'])
                            }
            ohlc_list.append(interm_dict)
        CandlesDF = pd.DataFrame(ohlc_list)
        
        # extract volume, state, and time information 
        interm_dic = {
            'complete' :[],
            'volume': [],
            'time' : []
                    }
        for i in kline:
            _complete, _volume, _time = i['complete'], i['volume'], self.parse_time(i['time'])
            interm_dic['complete'].append(_complete)
            interm_dic['volume'].append(_volume)
            interm_dic['time'].append(_time)

        CandlesDF['volume'], CandlesDF['complete'] = interm_dic['volume'], interm_dic['complete']
        CandlesDF['time'] = interm_dic['time']
        CandlesDF.set_index('time', inplace=True)
        
        return CandlesDF
# !SECTION end of OandaExchange class

# SECTION  Binance Exchange
class BinanceExchange(object):
    """ 
        Initialize the program creating the client instaces used by the rest of the methods

        Parameters
        -----------
        proxy : dict
            optional
            
            e.g. -> proxy = {
                        'http': 'http://mulambak:Soundsoul3@10.47.3.231:3128',
                        'https': 'https://mulambak:Soundsoul3@10.47.3.231:3128'
                            }
        Returns
        --------
        >>> binance client
    """
    list_of_tuples = [
        ('ADAUSDT', 5, 1), ('BCHABCUSDT', 2, 5), ('BCHSVUSDT', 2, 5), ('BNBUSDT', 4, 2), ('BTCUSDT', 2, 6),
        ('EOSUSDT', 4, 2), ('ETCUSDT', 4, 2), ('ETHUSDT', 2, 5), ('ICXUSDT', 4, 2), ('IOTAUSDT', 4, 2), 
        ('LTCUSDT', 2, 5), ('NEOUSDT', 3, 3), ('NULSUSDT', 4, 2), ('ONTUSDT', 3, 3), ('QTUMUSDT', 3, 3),
        ('TRXUSDT', 5, 1), ('VETUSDT', 5, 1), ('XLMUSDT', 5, 1), ('XRPUSDT', 5, 1)
                    ] 
                    #  (Symbol, price, quantity)

    list_of_pair = [i[0] for i in list_of_tuples]
    price_dcmls = [j[1] for j in list_of_tuples]
    qty_dcmls =  [j[2] for j in list_of_tuples]
    interval = Client.KLINE_INTERVAL_5MINUTE
    time_frame = '1 day ago UTC'
    
    def __init__(self, api_key, api_secret, proxy=None): # didn't initialize class with pair because of the curr_pair_selection method. The method needs to run automatically, and it assumes we don't know the pair yet.
        self.api_key = api_key
        self.api_secret = api_secret

        if proxy == None:
            self.client = Client(self.api_key, self.api_secret)
        else:
            self.client = Client(self.api_key, self.api_secret, {'proxies': proxy})
    
    def curr_price(self, symbol):
        """ 
        Return the current price for input symbol
        \n-----------------------------------------\n
        Params
        ------
        symbol: str - Instrument symbol
        eg.
        >>> curr_price('XBTUSD')
        """
        ticker = self.client.get_ticker(symbol=symbol)
        return float(ticker['lastPrice'])

    def instruments_binance(self, list_of_pair):
        """ Return list of instruments with volume higher than the market's average
        >>> instruments_binance(list)
        """
        try:
            output = {'symbol':[], 'quoteVolume':[]}
            response = {}
            data = {}

            for i in list_of_pair:
                tick = self.client.get_ticker(symbol=i)
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
            self.list_of_pair = list_symbols_USDT + list_symbols_BTC
            data['USDT_symbols'] = list_symbols_USDT
            data['BTC_symbols'] = list_symbols_BTC
            data['both'] = self.list_of_pair
            data['nbr_symbols'] = len(self.list_of_pair)

            response['status'] = 'OK'
            response['data'] = data
            response['message'] = ''

            print('\nStatus Update: \n    On %s' % 
                datetime.datetime.now().replace(microsecond=0) 
                + "\n    BINANCE Exchange: %s instruments" % len(self.list_of_pair)
                + " selected for watchlist.\n")
        
        except:
            response['status'] = 'ERROR'
            response['data'] = config.list_of_pair_v2
            response['message'] = 'An Exception occured during handling BINANCE request. Alternate list of instruments has been set'

        return response
    
    @staticmethod
    def dateconv(dateSTR):
        return datetime.datetime.fromtimestamp(dateSTR)
    
    def get_klines(self, pair, interval, timeframe):
        """ Get historical klines from binance

            Parameters
            ----------
            pair : str, required
                currency pair symbol
            
            The parameters time_frame and interval are defined as class variables

            Returns   
            --------
            list of OHLCV values
        """  
        klines = self.client.get_historical_klines(pair, interval, timeframe)
        
        # dateconv = np.vectorize(datetime.datetime.fromtimestamp)
        
        candles = {
                    'time':[self.dateconv(int(kline[0]/1000)) for kline in klines],
                    'o':[float(kline[1]) for kline in klines],
                    'h':[float(kline[2]) for kline in klines],
                    'l':[float(kline[3]) for kline in klines],
                    'c':[float(kline[4]) for kline in klines],
                    'v':[float(kline[5]) for kline in klines]
                        }
        return pd.DataFrame(candles)
# !SECTION end of BinanceExchange

# SECTION  BitmexExchange
class BitmexExchange(object):
    def __init__(self, api_key, api_secret, test):
        self.api_key=api_key
        self.api_secret=api_secret
        self.test=test
    
    # ANCHOR client
    def client(self):
        client = bitmex.bitmex(
            test=self.test,
            api_key=self.api_key,
            api_secret=self.api_secret)
        return client
    
    # ANCHOR get_klines
    def get_klines(self, instrument=str, binSize=str, count=int):
            ohlc = pd.DataFrame(self.client().Trade.Trade_getBucketed(
                    binSize=binSize,
                    columns='close,high,open,low,timestamp,volume',
                    symbol=instrument,
                    partial=True,
                    count=count,
                    reverse=True
                ).result()[0])

            _time = [i.to_pydatetime() for i in ohlc['timestamp']]
            ohlc = ohlc[['open', 'high', 'low', 'close', 'volume']]
            ohlc['time'] = _time
            ohlc.columns = ['o', 'h', 'l', 'c', 'v', 'time']

            # Change count to appropriate number of days
            return ohlc.reindex(index=ohlc.index[::-1])
    
    # ANCHOR curr_price
    def curr_price(self, symbol):
        ticker = self.client().Trade.Trade_getBucketed(
            symbol=symbol, 
            binSize='1m', 
            count=1, 
            partial=True, 
            reverse=True
                        ).result()[0]
        return float(ticker[0]['close'])

    # ANCHOR new_order
    def new_order(symbol, orderQty, text, side=None, price=None, stopPx=None, ordType=None):
        """
        Post a mew order
        Params
        ------
        symbol: string - Instrument symbol. e.g. 'XBTUSD'.
        side: string - Valid options: Buy, Sell. Defaults to 'Buy' unless orderQty is negative.
        orderQty: double - Optional Order quantity in units of the instrument (i.e. contracts)
        price: double - Optional limit price for 'Limit', 'StopLimit', and 'LimitIfTouched' orders.
        stopPx: double - Optional trigger price for 'Stop', 'StopLimit', 'MarketIfTouched', and 
                'LimitIfTouched' orders. Use a price below the current price for stop-sell 
                orders and buy-if-touched orders. Use execInst of 'MarkPrice' or 'LastPrice' 
                to define the current price used for triggering.
        ordType: string - Order type. Valid options: Market, Limit, Stop, StopLimit, MarketIfTouched, 
                LimitIfTouched, Pegged. Defaults to 'Limit' when price is specified. Defaults 
                to 'Stop' when stopPx is specified. Defaults to 'StopLimit' when price and 
                stopPx are specified.
        text: string - order annotation. e.g. 'Take profit'.
        """
        # NOTE always update leverage then place order
        return self.client().Order.Order_new(
            symbol=symbol ,
            side=side,
            orderQty=orderQty,
            price=price,
            stopPx=stopPx,
            ordType=ordType,
            timeInForce='GoodTillCancel',
            text=text
        ).result()[0]

    # ANCHOR order_quantity
    def order_quantity(symbol, frctn):
        """ 
        Calculate the order quantity as a fraction of the account's balance
        Params
        ------
        symbol: string - Instrument symbol. e.g. 'XBTUSD'.
        frctn: double - Fraction of the account to use. (units - percent) 
        """
        margin = self.client().User.User_getMargin().result()[0]
        balanceBTC = margin['availableMargin']
        balanceBTC = balanceBTC/100000000
        price = self.curr_price(symbol=symbol)
        balanceQuote = balanceBTC*price
        
        perc_balance = frctn/100
        quantity = balanceQuote*perc_balance
        if quantity < 1:
            return 1
        else:
            return quantity

    # ANCHOR update_leverage
    def update_leverage(symbol, leverage):
        """ 
        Update leverage of position for a specific symbol
        Params
        ------
        symbol: string - Instrument symbol. e.g. 'XBTUSD'.
        leverage:   Leverage value. Send a number between 0.01 and 100 
                    to enable isolated margin with a fixed leverage. 
                    Send 0 to enable cross margin.
        """
        # NOTE cross margin means using the entire account's margin
        # NOTE always update leverage then place order
        return self.client().Position.Position_updateLeverage(
            symbol=symbol, 
            leverage=leverage).result()[0]
    
    # ANCHOR get_orderID
    def get_orderID(symbol, text):
        """
        Retrieve orderID from account using the text provide when placing order
        Params
        ------
        symbol: string - Instrument symbol. e.g. 'XBTUSD'.\n
        text: string - order annotation. e.g. 'Take profit'.
        """
        orderbook = self.client().Order.Order_getOrders(symbol=symbol).result()[0]
        orderbook = pd.DataFrame(orderbook)
        orderID_index = orderbook[orderbook['text']==text].index[0]
        return orderbook.loc[orderID_index]['orderID']

    # ANCHOR cancel_order
    def cancel_order(orderID, text=None):
        """
        Cancel a specific active order\n
        Params
        ------
        orderID: Order ID(s);\n
        text: e.g. Optional cancellation annotation. e.g. 'Spread Exceeded'
        """
        return self.client().Order.Order_cancel(
                orderID=orderID, 
                text=text).result()[0]
    
    # ANCHOR cancel_allOrders
    def cancel_allOrders(symbol=None):
        """
        Cancel all open orders
        Params
        ------
        symbol: str - Optional. If provided, only cancels orders for that symbol
        """
        return self.client().Order.Order_cancelAll(symbol=symbol).result()[0]

    # ANCHOR close_position
    def close_position(symbol, orderQty, price=None):
        """
        symbol: string - Instrument symbol. e.g. 'XBTUSD'.
        price: if price is not provided, the position will be closed at market price
        orderQty: the sign of the orderQty should be opposition to the sign of the orderQty in the entry order
        """
        return self.client().Order.Order_new(
            symbol=symbol, 
            orderQty=orderQty, 
            price=price, 
            execInst='Close'
            ).result()[0]
# !SECTION end of BitmexExchange class

# SECTION  PoloniexEchange
class PoloniexEchange(Poloniex):
    
    def __init__(self, apikey=None, secret=None):
        Poloniex.__init__(self, apikey=None,secret=None)
        self.apikey = apikey
        self.secret = secret
    
    def client(self):
        if self.apikey==self.secret==None:
            return Poloniex()
        else:
            return Poloniex(apikey=self.apikey, secret=self.secret)
    
    @staticmethod
    def unix_converter(dt=datetime):
        """ Convert datetime object to 
            unix timestamp
        """
        return time.mktime(dt.timetuple())
    
    def get_klines(self, currencyPair, period, start, end):
        start = self.unix_converter(start[0])
        end = self.unix_converter(end)
        ohlc = self.client().returnChartData(
            currencyPair=currencyPair,
            period=period, 
            start=start,
            end=end
                )
        
        ohlc = pd.DataFrame(ohlc)
        date = [datetime.datetime.fromtimestamp(i)
                for i in ohlc['date']]
        ohlc = ohlc[['open','high','low','close','volume']]
        ohlc.columns = ['o','h','l','c','v']
        ohlc['time'] = date
        
        return ohlc
    
    def curr_price(self, symbol):
        end = datetime.datetime.now()
        start = end - datetime.timedelta(seconds=600)
        end = self.unix_converter(end)
        start = self.unix_converter(start)
        ticker = self.client().returnChartData(
            currencyPair=symbol, 
            period=300, 
            start=start, 
            end=end
                )
        
        return ticker[-1]['close']
    
    def instruments_poloniex(self, list_of_tickers):
        try:
            tickers_df = pd.DataFrame({'symbol':list_of_tickers})
            response = {}
            data = {}

            # request quote volumes for every curr pair in exchange
            qVol = []
            ticker_dict = self.client().returnTicker()
            for i in list_of_tickers:
                element = ticker_dict[i]['quoteVolume']
                qVol.append(element)
            tickers_df['qVolume'] = qVol
                
            # Create masks to separe out different markets
            mask1 = [i[:3]=='BTC' for i in tickers_df['symbol']]
            mask2 = [i[:4]=='USDT' for i in tickers_df['symbol']]
            mask3 = [i[:4]=='USDC' for i in tickers_df['symbol']]
            mask4 = [i[:3]=='ETH' for i in tickers_df['symbol']]
            mask5 = [i[:3]=='XMR' for i in tickers_df['symbol']]

            # Separate instruments based on baseCoin
            BTC_market = tickers_df[mask1]
            USDT_market = tickers_df[mask2]
            USDC_market = tickers_df[mask3]
            ETH_market = tickers_df[mask4]
            XMR_market = tickers_df[mask5]

            # select curr pair with a higher than
            # avg vol in each market
            mask1 = [i >= BTC_market.mean()[0] for i in BTC_market['qVolume']]
            mask2 = [i >= USDT_market.mean()[0] for i in USDT_market['qVolume']]
            mask3 = [i >= USDC_market.mean()[0] for i in USDC_market['qVolume']]
            mask4 = [i >= ETH_market.mean()[0] for i in ETH_market['qVolume']]
            mask5 = [i >= XMR_market.mean()[0] for i in XMR_market['qVolume']]
                    
            BTC_market = BTC_market[mask1]
            USDT_market = USDT_market[mask2]
            USDC_market = USDC_market[mask3]
            ETH_market = ETH_market[mask4]
            XMR_market = XMR_market[mask5]
                    
            # create final list_of_tickers
            # list_of_tickers = [
                
            #     list(BTC_market['symbol']) +
            #     list(USDT_market['symbol']) +
            #     list(USDC_market['symbol']) +
            #     list(ETH_market['symbol']) +
            #     list(XMR_market['symbol'])
                
            #                 ]
            # list_of_tickers = list_of_tickers[0]
            # print('\nStatus Update: \n    On %s' % 
            #     datetime.datetime.now().replace(microsecond=0) 
            #     + "\n     Exchange: %s instruments" % len(list_of_tickers)
            #     + " selected.\n")

            # # return list_of_tickers

            self.list_of_tickers = [
                                    list(BTC_market['symbol']) +
                                    list(USDT_market['symbol']) +
                                    list(USDC_market['symbol']) +
                                    list(ETH_market['symbol']) +
                                    list(XMR_market['symbol'])
                            ]

            data['BTC_market'] = list(BTC_market['symbol'])
            data['USDT_market'] = list(USDT_market['symbol'])
            data['USDC_market'] = list(USDC_market['symbol'])
            data['ETH_market'] = list(ETH_market['symbol'])
            data['XMR_market'] = list(XMR_market['symbol'])
            data['overall'] = self.list_of_tickers
            data['nbr_symbols'] = len(self.list_of_tickers)

            response['status'] = 'OK'
            response['data'] = data
            response['message'] = ''

            print('\nStatus Update: \n    On %s' % 
                datetime.datetime.now().replace(microsecond=0) 
                + "\n    BINANCE Exchange: %s instruments" % len(list_of_pair)
                + " selected for watchlist.\n")
        
        except:
            response['status'] = 'ERROR'
            response['data'] = config.list_of_tickers2
            response['message'] = 'An Exception occured during handling POLONIEX request. Alternate list of instruments has been set'

        return response
# !SECTION End of PoloniexExchange class

# SECTION  UserDefinedFxns
class UserDefinedFxns(object):
    
    # ANCHOR turning_points
    @staticmethod
    def turning_points(datafr):
        c = np.array(datafr['c'])
        h = np.array(datafr['h'])
        l = np.array(datafr['l'])
        
        peaks_index = argrelmax(c)
        peaks_closes = c[peaks_index]
        peaks_highs = h[peaks_index]

        bottoms_index = argrelmin(c)
        bottoms_closes = c[bottoms_index]
        bottoms_lows = l[bottoms_index]
        
        local_max = peaks_closes.max()
        local_min = bottoms_closes.min()
        zenith = peaks_highs[np.where(peaks_closes==local_max)] # high of local max
        nadir = bottoms_lows[np.where(bottoms_closes==local_min)] # low of local min
        
        return {
            'highest-high': zenith[-1], 
            'lowest-low' : nadir[-1],
            'peaks': {'close': peaks_closes, 'high': peaks_highs},
            'bottoms': {'close': bottoms_closes, 'lows': bottoms_lows}
                }
    
    # ANCHOR fib_levels
    def fib_levels(self, datafr):
        c = np.array(datafr['c'])
        TurningPoints = self.turning_points(datafr)
        max_price = TurningPoints['local_min_max'][0]
        min_price = TurningPoints['local_min_max'][1]
        diff = max_price - min_price
        zenith_index = np.where(c == max_price)
        nadir_index = np.where(c == min_price)

        if zenith_index[-1][-1] > nadir_index[-1][-1]:
            level_0 = max_price
            level_1 = max_price - 0.236*diff
            level_2 = max_price - 0.382*diff
            level_3 = max_price - 0.5*diff
            level_4 = max_price - 0.618*diff
            level_5 = max_price - 0.786*diff
            level_6 = max_price - 0.886*diff
            level_7 = min_price
            level_8 = max_price - 1.27*diff
            
            return {'price_direction':'higer',
                   'fib_leves': [level_0, level_1, level_2, level_3, level_4, 
                    level_5, level_6, level_7, level_8]}

        elif zenith_index[-1][-1] < nadir_index[-1][-1]:
            level_0 = min_price
            level_1 = min_price + 0.236*diff
            level_2 = min_price + 0.382*diff
            level_3 = min_price + 0.5*diff
            level_4 = min_price + 0.618*diff
            level_5 = min_price + 0.786*diff
            level_6 = min_price + 0.886*diff
            level_7 = max_price
            level_8 = min_price + 1.27*diff

            return {'price_direction':'lower',
                   'fib_leves': [level_0, level_1, level_2, level_3, level_4, 
                    level_5, level_6, level_7, level_8]}
    
    # ANCHOR key_level_test
    def key_level_test(self, level, datafr):
        test = [i <= level <= j for i,j in zip(datafr['l'], datafr['h'])]
        return test.count(True)
    
    # ANCHOR resistance_test
    def resistance_test(self, level, datafr, percentage):
        """ 
        Return number of times a key support level has been tested
        Parameters
        ----------
        level: float or int
                Price level

        datafr: dictionary of numpy arrays
            dictionary of candlesticks in which: 'open', 'high', 'low', and 'close' are used as keys

        percentage: float
            used to compute the boundaries of the price area tested for resistance

        Returns
        -------
        Ret: int

            number of times the resistance of the area has tested
        """
        input_ = self.turning_points(datafr)
        peak_highs = input_['peaks']['high']
        peak_closes = input_['peaks']['close']

        a_upr = level*(1 + percentage)
        # upper boundary of area
        a_lwr = level*(1 - percentage)
        # lower boundary of area
        bool_mask = []

        for i,j in zip(peak_highs, peak_closes):
            # arr[i][0] = high, arr[i][1] = close 
            if i > a_lwr and i < a_upr and j > a_lwr and j < a_upr:
                    mask = True
                    # both high and close within area
            elif i > a_lwr and i < a_upr and j < a_lwr:
                    mask = True
                    # high within area but close less than lower bound
            elif i > a_upr and j > a_lwr and j < a_upr:
                    mask = True
                    # close within area but high greater than upper bound
            elif i > a_upr and j < a_lwr:
                    mask = True
                    # close lower than lower bound
                    # high greater than upper bound
            else:
                mask = False
        
        return bool_mask.count(True)
    
    # ANCHOR support_test
    def support_test(self, level, datafr, percentage):
        """ Return number of times a key support level has been tested"""
        input_ = self.turning_points(datafr)
        bottoms_lows = input_['bottoms']['lows']
        bottoms_closes = input_['bottoms']['close']

        a_upr = level*(1 + percentage)
        # upper boundary of area
        a_lwr = level*(1 - percentage)
        # lower boundary of area
        
        bool_mask = []
        for i,j in zip(bottoms_lows, bottoms_closes):
            if i > a_lwr and i < a_upr and j > a_lwr and j < a_upr:
                mask = True
                
            elif i < a_lwr and j > a_lwr and j < a_upr:
                mask = True
                
            elif i > a_lwr and i < a_upr and j > a_upr:
                mask = True
            
            elif (i < a_lwr and j > a_upr):
                mask = True
                
            else:
                mask = False
            bool_mask.append(mask)

        return bool_mask.count(True)
    
    # ANCHOR send_email
    @staticmethod
    def send_email(SUBJECT, BODY):
        """With this function we send out an email with a html body"""
        
        # Create message container - the correct MIME type is multipart/alternative here!
        TO = 'jkanangila@gmail.com'
        FROM ='avinaedi9@gmail.com'
        MESSAGE = MIMEMultipart('alternative')
        MESSAGE['subject'] = SUBJECT
        MESSAGE['To'] = TO
        MESSAGE['From'] = FROM
        
        # Record the MIME type text/html.
        HTML_BODY = MIMEText(BODY, 'html')
        
        # Attach parts into message container. 
        # According to RFC 2046, the last part of a multipart message, in this case 
        # the HTML message, is best and preferred.
        MESSAGE.attach(HTML_BODY)
        
        # The actual sending of the e-mail
        server = smtplib.SMTP('smtp.gmail.com:587')    
        # Credentials (if needed) for sending the mail
        password = "esaie1990"
        
        server.starttls() 
        server.login(FROM,password) 
        server.sendmail(FROM, [TO], MESSAGE.as_string()) 
        server.quit()

        print("%s" % datetime.datetime.now().replace(microsecond=0)
        + " Email Notification Sent to user\n")
    
    # ANCHOR interval_counter
    @staticmethod
    def interval_counter(dt=datetime):
        """ Compute the number of minutes and seconds to the next 5-min interval"""
        # if the number of minutes is either less than 5 or
        # between 5 and 10
        if dt.minute < 5:
            # convert minutes to seconds and substract from
            # the equivalent of5 minute in seconds
            # return integral part i.e the integer
            # and the modulus (rest, already in seconds)
            min_to_sec = 5*60 - (dt.minute*60 + dt.second)
            if min_to_sec < 60:
                return [0, min_to_sec]
            else:
                return [min_to_sec//60, min_to_sec%60]
        
        elif 5 < dt.minute <= 10:
            # convert minutes to seconds and substract from
            # the equivalent of 10 minute in seconds
            min_to_sec = 10*60 - (dt.minute*60 + dt.second)
            if min_to_sec < 60:
                return [0, min_to_sec]
            else:
                return [min_to_sec//60, min_to_sec%60]
        
        # if the number of minutes is greater than 10, apply 
        # same logic as before to the last digit of the number
        elif dt.minute > 10 and int(str(dt.minute)[1]) < 5:
            min_to_sec = 5*60 - (int(str(dt.minute)[1])*60 + dt.second)
            if min_to_sec < 60:
                return [0, min_to_sec]
            else:
                return [min_to_sec//60, min_to_sec%60]
        
        elif dt.minute > 10 and 5 < int(str(dt.minute)[1]) < 10:
            min_to_sec = 10*60 - (int(str(dt.minute)[1])*60 + dt.second)
            if min_to_sec < 60:
                return [0, min_to_sec]
            else:
                return [min_to_sec//60, min_to_sec%60]
    
    # ANCHOR time_to_sec
    @staticmethod
    def time_to_sec(dat):
        """ Convert a time object to seconds"""
        return dat.hour*60*60 + dat.minute*60 + dat.second

    # ANCHOR var_diff
    @staticmethod
    def var_diff(x, y):
        return abs((x - y) / max([x,y]))

    # ANCHOR diff
    @staticmethod
    def diff(x, y):
        return abs(x - y)

    # ANCHOR appendObjtoAX
    @staticmethod
    def appendObjtoAX(ax, x_val, label=None):
        return ax.plot(x_val, label=label, ls='--', lw=0.5)

    # ANCHOR appendCandlePlot
    @staticmethod
    def appendCandlePlot(ax, opens, highs, lows, closes, width=0.6, alpha=0.75):

        return candlestick2_ohlc(ax, opens=opens, highs=highs, lows=lows, closes=closes, 
            colorup=config.color['green'], colordown=config.color['red'], width=width)

    # ANCHOR formatFig
    @staticmethod
    def formatFig(fig, ax, time, path, instrument=str):
        nTime = [PoloniexEchange.unix_converter(i) for i in time]
        xdate = [datetime.datetime.fromtimestamp(i) for i in nTime]
        ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        
        def mydate(x,pos):
            try:
                    return xdate[int(x)]
            except IndexError:
                    return ''
        
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
        
        fig.autofmt_xdate()
        
        
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.title('Historical Data for %s \nFor the period %s to %s' % (instrument, time.iloc[0], time.iloc[-1]))
        plt.tight_layout()
        plt.savefig(path, bbox_inches="tight")
        plt.close(fig)

    # ANCHOR get_decimal_places
    @staticmethod
    def get_decimal_places(current_price):
        return len(str(current_price).replace('.',' ').split()[1])
# !SECTION end of UserDefinedFxns class
