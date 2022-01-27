"""Changes: 1.  Removed sma200 from various masks in short-term trend method
            2.  Removed intermediate trend from decision loop in step3
            3.  Added figsize in line 363

v.2.1.1"""
import json
import sys

from exchanges import *
from configuration import *
from pause import seconds

binance = BinanceExchange(**keys['binance'])
bitmex = BitmexExchange(**keys['bitmex-testnet'])
oanda = OandaExchange(**keys['oanda-practice'])
poloniex = PoloniexEchange()

# SECTION 1. Strategy
class Strategy(UserDefinedFxns):
    def __init__(self):
        UserDefinedFxns.__init__(self)
        
    # ANCHOR moving_avg_exp
    def moving_avg_exp(self, datafr, period):
        return datafr['c'].ewm(span=period, adjust=False).mean()
    
    # ANCHOR moving_avg_simp
    def moving_avg_simp(self, datafr, period):
        return datafr['c'].rolling(window=period).mean()
    
    # ANCHOR long_term_trend
    def long_term_trend(self, datafr):
        # input_df = self.CandlesticksData(self.instrument, params=self.params['longterm'])
        ema10 = self.moving_avg_exp(datafr=datafr, period=10)
        # ema20 = self.moving_avg_exp(datafr=datafr, period=10)
        sma50 = self.moving_avg_simp(datafr=datafr, period=50)
        sma100 = self.moving_avg_simp(datafr=datafr, period=100)
        
        # mask1: check that the moving avs are in the corect order i.e 10>20>50>100 or 10<20<50<100
        if ema10.iloc[-1] > sma50.iloc[-1] > sma100.iloc[-1]:
            mask1 = 1 # +1 for uptrend and -1 for downtrend
        elif ema10.iloc[-1] < sma50.iloc[-1] < sma100.iloc[-1]:
            mask1 = -1 # +1 for uptrend | -1 for downtrend | 0 for sideway
        else:
            mask1 = 0
            
        # mask2: check if price has been trading above key MAs for the last 10 periods
            # count nbr of times the test was positive and nbr of times it was negative
            # compare the two values --> greatest value decide the trend
        test_up = [i > j for i,j in zip(datafr['c'][-10:], sma100[-10:])]
        test_dwn = [i < j for i,j in zip(datafr['c'][-10:], sma100[-10:])]
        if round((test_up.count(True)/len(test_up))*100, 2) >= 90:
            mask2 = 1
        elif round((test_dwn.count(True)/len(test_dwn))*100, 2) >= 90:
            mask2 = -1
        else:
            mask2 = 0
            
        # mask3: check if the long term MAs i.e. 50 and 100 are still advancing (MA[i]>MA[i-1])
        if sma50.iloc[-1] > sma50.iloc[-2] and sma100.iloc[-1] > sma100.iloc[-2]:
            mask3 = 1
        elif sma50.iloc[-1] < sma50.iloc[-2] and sma100.iloc[-1] < sma100.iloc[-2]:
            mask3 = -1
        else:
            mask3 = 0
            
        # actual trend
        if mask1 == mask2 == mask3== 1:
            return 'uptrend'
        elif mask1 == mask2 == mask3 == -1:
            return 'downtrend'
        else:
            return 'no_trend'
    
    # ANCHOR intermediate_trend
    def intermediate_trend(self, datafr):
        # input_df = self.CandlesticksData(self.instrument, params=self.params['short'])
        ema21 = self.moving_avg_exp(datafr=datafr, period=21)
        sma50 = self.moving_avg_simp(datafr=datafr, period=50)
        sma100 = self.moving_avg_simp(datafr=datafr, period=100)
        sma200 = self.moving_avg_simp(datafr=datafr, period=200)
        
        # Check if the MAs are in correct order i.e ema21>sma50>sma100>sma200 or ema21<sma50<sma100<sma200
        # notice that sma200 has been added to this test
        if ema21.iloc[-1] > sma50.iloc[-1] > sma100.iloc[-1] > sma200.iloc[-1]:
            mask1 = 1
        elif ema21.iloc[-1] < sma50.iloc[-1] < sma100.iloc[-1] < sma200.iloc[-1]:
            mask1 = -1
        else:
            mask1 = 0
        
        # Check if the price has been trading above or below ema21 for the last 15 hours (30 periods)
        # test passed only for 80 % of samples
        test_up = [i > j for i,j in zip(datafr['c'][-30:], ema21[-30:])]
        test_dwn = [i < j for i,j in zip(datafr['c'][-30:], ema21[-30:])]
        if round((test_up.count(True)/len(test_up))*100, 2) >= 80:
            mask2 = 1
        elif round((test_dwn.count(True)/len(test_dwn))*100, 2) >= 80:
            mask2 = -1
        else:
            mask2 = 0
            
        # Check if long term MAs are advancing or retreating 
        if sma50.iloc[-1] > sma50.iloc[-2] and sma100.iloc[-1] > sma100.iloc[-2] and sma200.iloc[-1] > sma200.iloc[-2]:
            mask3 = 1
        elif sma50.iloc[-1] < sma50.iloc[-2] and sma100.iloc[-1] < sma100.iloc[-2] and sma200.iloc[-1] < sma200.iloc[-2]:
            mask3 = -1
        else:
            mask3 = 0
            
        # actual trend
        if mask1 == mask2 == mask3 == 1:
            return 'uptrend'
        elif mask1 == mask2 == mask3 == -1:
            return 'downtrend'
        else:
            return 'no_trend'
    
    # ANCHOR short_term_trend
    def short_term_trend(self, datafr):
        # input_df = self.CandlesticksData(self.instrument, params=self.params['itermediate'])
        # ema10 = self.moving_avg_exp(datafr=datafr, period=10)
        ema21 = self.moving_avg_exp(datafr=datafr, period=21)
        sma50 = self.moving_avg_simp(datafr=datafr, period=50)
        sma100 = self.moving_avg_simp(datafr=datafr, period=100)
        sma200 = self.moving_avg_simp(datafr=datafr, period=200)
        
        # Check if the MAs are in correct order i.e ema21>sma50>sma100>sma200 or ema21<sma50<sma100<sma200
        # notice that sma200 has been added to this test
        if ema21.iloc[-1] > sma50.iloc[-1] > sma100.iloc[-1]:
            mask1 = 1
        elif ema21.iloc[-1] < sma50.iloc[-1] < sma100.iloc[-1]:
            mask1 = -1
        else:
            mask1 = 0
        
        # Check if the price has been trading above or below ema21 for the last 15 hours (30 periods)
        test_up = [i > j for i,j in zip(datafr['c'][-40:], ema21[-40:])]
        test_dwn = [i < j for i,j in zip(datafr['c'][-40:], ema21[-40:])]
        if round((test_up.count(True)/len(test_up))*100, 2) >= 80:
            mask2 = 1
        elif round((test_dwn.count(True)/len(test_dwn))*100, 2) >= 90:
            mask2 = -1
        else:
            mask2 = 0
            
        # Check if long term MAs are advancing or retreating 
        if sma50.iloc[-1] >= sma50.iloc[-2] and sma100.iloc[-1] >= sma100.iloc[-2]:
            mask3 = 1
        elif sma50.iloc[-1] <= sma50.iloc[-2] and sma100.iloc[-1] <= sma100.iloc[-2]:
            mask3 = -1
        else:
            mask3 = 0
            
        # actual trend
        if mask1 == mask2 == mask3== 1:
            return 'uptrend'
        elif mask1 == mask2 == mask3 == -1:
            return 'downtrend'
        else:
            return 'no_trend'

    # ANCHOR consolidation_check
    def consolidation_check(self, datafr, trend=str):
        """ Determine the presence of consolidation by tracking the order of key 
            moving averages in the provided dataframe
        """
        ema21 = self.moving_avg_exp(datafr=datafr, period=21)
        sma50 = self.moving_avg_simp(datafr=datafr, period=50)
        sma100 = self.moving_avg_simp(datafr=datafr, period=100)
        sma200 = self.moving_avg_simp(datafr=datafr, period=200)
        
        """ Count number of times MAs have been in correct order i.e. 
            ema21>sma50>sma100>sma200 or ema21<sma50<sma100<sma200
        """
        if trend=='uptrend':
            test_up = [i > j > w > z for i,j,w,z in 
                    zip(ema21, sma50, sma100, sma200)]
            if (test_up.count(True)/len(test_up))*100 <= 10:
                # if the test failed for @ least 90% of the sample then there
                # is consolidation
                return True
            else:
                return False

        elif trend=='downtrend':
            test_dwn = [i < j < w < z for i,j,w,z in 
                    zip(ema21, sma50, sma100, sma200)]
            if (test_dwn.count(True)/len(test_dwn))*100 <= 10:
                # if the test failed for @ least 90% of the sample then there
                # is consolidation
                return True
            else:
                return False

        else:
            return 0

    # ANCHOR resistance_level
    def resistance_level(self, datafr, trend):
        # locate and identify values of turning points in the market
        turning_points = self.turning_points(datafr=datafr) 
        # Determine average of peaks-high 
        resistance = turning_points['peaks']['high'].mean()
        # check if the market is in consolidation
        consolidation = self.consolidation_check(datafr=datafr, trend=trend)
        if consolidation:
            # the resistance is halfway between the highest-high and the level determined previously
            return resistance + (turning_points['highest-high'] - resistance)/2 # chng local_min_max to highest-high
        else:
            return 'N/A'

    # ANCHOR support_level
    def support_level(self, datafr, trend):
        # locate and identify values of turning points in the market
        turning_points = self.turning_points(datafr=datafr) 
        # Determine average of local minimums
        support = turning_points['bottoms']['lows'].mean()
        # check if the market is in consolidation
        consolidation = self.consolidation_check(datafr=datafr, trend=trend)
        if consolidation:
            # the support is halfway between the lowest-low and the level determined previously
            return support - (support - turning_points['lowest-low'])/2 # chng local_min_max to highest-high
        else:
            return 'N/A'

    # ANCHOR retracement
    def retracement(self, datafr, timeframe):
        """
        Determine wether or not the actual trend is experiencing a retracement (uptrend) or a pullback (downtrend)

        Parameters
        -----------
            datafr: pandas dataframe where o,h,l,c,v,time are used as keys 
            timeframe: str, the timeframe to be tested. correct values are long_term, intermediate, and short_term
        """
        if timeframe == 'long_term':
            TurningPoints = self.turning_points(datafr[-30:])
        
            # if we're in an uptrend and the actual price is lower than the recent high
            if self.long_term_trend(datafr) == 'uptrend' and datafr['c'].iloc[-1] < TurningPoints['highest-high']:
                # return [TurningPoints['highest-high'], 'uptrend', True]
                return {'target':TurningPoints['highest-high'], 
                        'LT_trend':'uptrend', 
                        'retracement':True}
            
            # if we're in an downtrend and the actual price is higher than the recent low
            elif self.long_term_trend(datafr) == 'downtrend' and datafr['c'].iloc[-1] > TurningPoints['lowest-low']:
                # return [TurningPoints['lowest-low'], 'downtrend', True]
                return {'target':TurningPoints['lowest-low'], 
                        'LT_trend':'downtrend', 
                        'retracement':True}
            else:
                # return [None, None, False]
                return {'target':None, 
                        'LT_trend':None, 
                        'retracement':False}

        elif timeframe == 'intermediate':
            TurningPoints = self.turning_points(datafr[-30:])
        
            # if we're in an uptrend and the actual price is lower than the recent high
            if self.intermediate_trend(datafr) == 'uptrend' and datafr['c'].iloc[-1] < TurningPoints['highest-high']:
                # return [TurningPoints['highest-high'], 'uptrend', True]
                return {'target':TurningPoints['highest-high'], 
                        'LT_trend':'uptrend', 
                        'retracement':True}
            
            # if we're in an downtrend and the actual price is higher than the recent low
            elif self.intermediate_trend(datafr) == 'downtrend' and datafr['c'].iloc[-1] > TurningPoints['lowest-low']:
                # return [TurningPoints['lowest-low'], 'downtrend', True]
                return {'target':TurningPoints['lowest-low'], 
                        'LT_trend':'downtrend', 
                        'retracement':True}
            else:
                # return [None, None, False]
                return {'target':None, 
                        'LT_trend':None, 
                        'retracement':False}
        
        elif timeframe == 'short_term':
            TurningPoints = self.turning_points(datafr[-30:])
            
            # if we're in an uptrend and the actual price is lower than the recent high
            if self.short_term_trend(datafr) == 'uptrend' and datafr['c'].iloc[-1] < TurningPoints['highest-high']:
                # return [TurningPoints['highest-high'], 'uptrend', True]
                return {'target':TurningPoints['highest-high'], 
                        'LT_trend':'uptrend', 
                        'retracement':True}
            
            # if we're in an downtrend and the actual price is higher than the recent low
            elif self.short_term_trend(datafr) == 'downtrend' and datafr['c'].iloc[-1] > TurningPoints['lowest-low']:
                # return [TurningPoints['lowest-low'], 'downtrend', True]
                return {'target':TurningPoints['lowest-low'], 
                        'LT_trend':'downtrend', 
                        'retracement':True}
            else:
                # return [None, None, False]
                return {'target':None, 
                        'LT_trend':None, 
                        'retracement':False}

    # ANCHOR klinePlotter
    def klinePlotter(self, instrument, exchange, refKey, majorTrend, path):
        # refKey used to retrieve timeframe and interval from param_dictionary

        # From appropriate exchange, request: candlesticks and current price for instrument
        # using current price, determine the number of decimal places that will be used to plot the key-level
        if exchange == "Binance":
            ohlc = binance.get_klines(pair=instrument, **params_binance[refKey])
            curr_prc = binance.curr_price(symbol=instrument)
            decimals = self.get_decimal_places(curr_prc)

        elif exchange == "Bitmex":
            ohlc = bitmex.get_klines(instrument=instrument, 
                                            **params_bitmex[refKey])
            curr_prc = bitmex.curr_price(symbol=instrument)
            decimals = self.get_decimal_places(curr_prc)

        elif exchange == "Oanda":
            oanda.CandlesticksData(instrument=instrument, 
                                                params=params_oanda[refKey])
            curr_prc = oanda.curr_price(symbol=instrument)
            decimals = self.get_decimal_places(curr_prc)

        elif exchange == "Poloniex":
            ohlc = poloniex.get_klines(currencyPair=instrument,
                                                                **params_poloniex[refKey])
            curr_prc = poloniex.curr_price(symbol=instrument)
            decimals = self.get_decimal_places(curr_prc)
        
        # place the ohlc data in a dictionary
        quotes = {
                'opens': ohlc[-144:].o,
                'highs': ohlc[-144:].h,
                'lows': ohlc[-144:].l,
                'closes': ohlc[-144:].c
        } 

        # calculate appropriate Moving averages and round-off their values 
        # if values are not rounded off they won't be plotted on top of candlesticks
        ema21 = self.moving_avg_exp(datafr=ohlc, period=21)
        ema21 = [round(i, decimals) for i in ema21]

        sma50 = self.moving_avg_simp(datafr=ohlc, period=50)
        sma50 = [round(i, decimals) for i in sma50]

        sma100 = self.moving_avg_simp(datafr=ohlc, period=100)
        sma100 = [round(i, decimals) for i in sma100]

        sma200 = self.moving_avg_simp(datafr=ohlc, period=200)
        sma200 = [round(i, decimals) for i in sma200]

        # determine wether resistance or support is applicable based on the major trend 
        # and calculate its value thereof
        if majorTrend == "uptrend":
            key_level = self.resistance_level(ohlc[-144:],"uptrend")
            key_level = round(key_level, decimals)
        elif majorTrend == "downtrend":
            key_level = self.support_level(ohlc[-144:],"downtrend")
            key_level = round(key_level, decimals)

        # create canvas object
        fig, ax = plt.subplots()

        # append different plots to the figure
        kline_plot = self.appendCandlePlot(ax, **quotes, width=0.6, alpha=0.75)
        ema21_plot = self.appendObjtoAX(ax, x_val=ema21[-144:], label='ema21')
        sma50_plot = self.appendObjtoAX(ax, x_val=sma50[-144:], label='sma50')
        sma100_plot = self.appendObjtoAX(ax, x_val=sma100[-144:], label='sma100')
        sma200_plot = self.appendObjtoAX(ax, x_val=sma200[-144:], label='sma200')
        key_level_plot = self.appendObjtoAX(ax, x_val=[key_level for i in quotes['closes']], label='resistance')
        txt = plt.text(0, (key_level+5), '%s' % key_level)

        # format the figure
        format_fig = self.formatFig(fig, ax, time=ohlc[-144:].time, instrument=instrument, path=path)
# !SECTION end of Strategy class

# SECTION 2. Signal
class Signal(Strategy):

    def __init__(self):
        Strategy.__init__(self)
    
    # SECTION 2.1. STEP 1 - Long term trends
    # ANCHOR Step1_Binance
    def Step1_Binance(self, list_of_pair):
        binance_watchlst = {'symbol': [], 'long_term':[]}
        response = {}
        error_message = ""
        
        for instrument in list_of_pair:
            # call out ohlc data for selected instruments
            ohlc = binance.get_klines(pair=instrument, 
                        **params_binance['longterm'])
            ohlc = ohlc[:-1]
            if len(ohlc) < 110:
                continue
            else:
                # determine the longterm trend and wether or not there is a retracement
                # taking place
                try:
                    test = self.retracement(datafr=ohlc, timeframe='long_term')
                except:
                    print('On %s | Binance exchange \nCould not analyse data for %s\nMoving on...' % 
                    (datetime.datetime.now().replace(microsecond=0), instrument))
                binance_watchlst['symbol'].append(instrument)
                binance_watchlst['long_term'].append(test)
                seconds(0.25)

        # create a boolean mask to  slice the watchlist
        mask = [i['retracement'] for i in binance_watchlst['long_term']]
        binance_watchlst = pd.DataFrame(binance_watchlst)
        binance_watchlst = binance_watchlst[mask]
        binance_watchlst.set_index('symbol', inplace=True)

        if len(binance_watchlst) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(binance_watchlst.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response

    # ANCHOR Step1_Bitmex
    def Step1_Bitmex(self, list_of_symbols):
        bitmex_watchlst = {'symbol': [], 'long_term':[]} 
        response = {}
        error_message = ""

        for instrument in list_of_symbols: 
            # call out ohlc data for selected instruments
            ohlc = bitmex.get_klines(instrument=instrument, 
                                    **params_bitmex['longterm']) 

            # determine the longterm trend and wether or not there is a retracement
            # taking place
            try:
                test = self.retracement(datafr=ohlc, timeframe='long_term')
            except:
                print('On %s | Bitmex exchange \nCould not analyse data for %s\nMoving on...' % 
                (datetime.datetime.now().replace(microsecond=0), instrument))
            bitmex_watchlst['symbol'].append(instrument)
            bitmex_watchlst['long_term'].append(test) 
            seconds(0.25)

        # create a boolean mask to  slice the watchlist
        mask = [i['retracement'] for i in bitmex_watchlst['long_term']] 
        bitmex_watchlst = pd.DataFrame(bitmex_watchlst) 
        bitmex_watchlst = bitmex_watchlst[mask]
        bitmex_watchlst.set_index('symbol', inplace=True)
        
        if len(bitmex_watchlst) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(bitmex_watchlst.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response
    
    # ANCHOR Step1_Oanda
    def Step1_Oanda(self, list_of_instruments):
        oanda_watchlst = {'symbol': [], 'long_term':[]}
        response = {}
        error_message = ""

            # TODO add a loop to decide on list_of_instruments 
        for instrument in list_of_instruments: 
            # call out ohlc data for selected instruments
            ohlc = oanda.CandlesticksData(instrument=instrument, 
                        params=params_oanda['longterm']) 
            ohlc = ohlc[:-1]
            # determine the longterm trend and wether or not there is a retracement
            # taking place
            try:
                test = self.retracement(datafr=ohlc, timeframe='long_term')
            except:
                print('On %s | Oanda exchange \nCould not analyse data for %s\nMoving on...' % 
                (datetime.datetime.now().replace(microsecond=0), instrument))
            oanda_watchlst['symbol'].append(instrument)
            oanda_watchlst['long_term'].append(test) 
            seconds(0.25)

        # create a boolean mask to  slice the watchlist
        mask = [i['retracement'] for i in oanda_watchlst['long_term']] 
        oanda_watchlst = pd.DataFrame(oanda_watchlst) 
        oanda_watchlst = oanda_watchlst[mask]
        oanda_watchlst.set_index('symbol', inplace=True)
        
        if len(oanda_watchlst) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(oanda_watchlst.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response

    # ANCHOR Step1_Poloniex
    def Step1_Poloniex(self, list_of_tickers):
        poloniex_watchlst = {'symbol': [], 'long_term':[]}
        response = {}
        error_message = ""

        for instrument in list_of_tickers:
            # call out ohlc data for selected instruments
            ohlc = poloniex.get_klines(currencyPair=instrument,
                                        **params_poloniex['longterm'])
            ohlc = ohlc[:-1]
            if len(ohlc) < 110:
                continue
            else:
                # determine the longterm trend and wether or not there is a retracement
                # taking place
                try:
                    test = self.retracement(datafr=ohlc, timeframe='long_term')
                except:
                    print('On %s | Poloniex exchange \nCould not analyse data for %s\nMoving on...' % 
                    (datetime.datetime.now().replace(microsecond=0), instrument))
                poloniex_watchlst['symbol'].append(instrument)
                poloniex_watchlst['long_term'].append(test)
                seconds(0.25)

        # create a boolean mask to  slice the watchlist
        mask = [i['retracement'] for i in poloniex_watchlst['long_term']]
        poloniex_watchlst = pd.DataFrame(poloniex_watchlst)
        poloniex_watchlst = poloniex_watchlst[mask]
        poloniex_watchlst.set_index('symbol', inplace=True)
        
        if len(poloniex_watchlst) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(poloniex_watchlst.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response
    # !SECTION end of section 2.1

    # SECTION 2.2. STEP 2 - Resitances, supports, and rewards
    # ANCHOR Step2_descision_loop
    def step2_descision_loop(self, datafr, instrument, list_of_levels,
                                    list_of_rewards, list_of_risks,
                                        list_of_ratios, trend, Watchlist):
                                        
        if trend == 'uptrend':
            # determine the key level using the resistance_level method
            # from the Strategy module
            key_level = self.resistance_level(datafr=datafr[-144:], trend=trend)

            if isinstance(key_level, float):
            # if the level has been test more than 4 times keep value else discard
                if self.key_level_test(level=key_level, datafr=datafr) > 4:
                    reward = self.var_diff(Watchlist['long_term'].loc[instrument]['target'], key_level)
                    trn_points = self.turning_points(datafr[-40:-1])
                    lwst_point = trn_points['lowest-low']
                    risk = self.var_diff(key_level, lwst_point)
                    risk_v_rwrd = reward/risk
                    list_of_risks.append(round(risk*100, 2))
                    list_of_ratios.append(round(risk_v_rwrd, 2))
                    list_of_levels.append(key_level)
                    list_of_rewards.append(round(reward*100, 2))

                else:
                    list_of_levels.append('N/A')
                    list_of_rewards.append('N/A')
                    list_of_risks.append('N/A')
                    list_of_ratios.append('N/A')
            else:
                list_of_levels.append('N/A')
                list_of_rewards.append('N/A')
                list_of_risks.append('N/A')
                list_of_ratios.append('N/A')

        elif trend == 'downtrend':
            # determine the key level using the support_level method
            # from the Strategy module
            key_level = self.support_level(datafr=datafr[-144:], trend=trend)

            if isinstance(key_level, float):
                # if the level has been test more than 4 times keep value else discard
                if self.key_level_test(level=key_level, datafr=datafr) > 4:
                    reward = self.var_diff(Watchlist['long_term'].loc[instrument]['target'], key_level)
                    trn_points = self.turning_points(datafr[-40:-1])
                    hgst_point = trn_points['highest-high']
                    risk = self.var_diff(key_level, hgst_point)
                    risk_v_rwrd = reward/risk
                    list_of_risks.append(round(risk*100, 2))
                    list_of_ratios.append(round(risk_v_rwrd, 2))
                    list_of_levels.append(key_level)
                    list_of_rewards.append(round(reward*100, 2))
                else:
                    list_of_levels.append('N/A')
                    list_of_rewards.append('N/A')
                    list_of_risks.append('N/A')
                    list_of_ratios.append('N/A')
            else:
                list_of_levels.append('N/A')
                list_of_rewards.append('N/A')
                list_of_risks.append('N/A')
                list_of_ratios.append('N/A')

        else:
            list_of_levels.append('N/A')
            list_of_rewards.append('N/A')
            list_of_risks.append('N/A')
            list_of_ratios.append('N/A')

    # ANCHOR Step2_binance
    def Step2_binance(self, watchlist, timeFrame="short"):
        list_of_levels = []
        list_of_rewards = []
        list_of_risks = []
        list_of_ratios = []
        df_object=watchlist.copy()
        response = {}
        error_message = ""

        for instrument in df_object.index.values:
            try:
                if timeFrame == "intermediate": 
                    datafr = binance.get_klines(pair=instrument, **params_binance['itermediate'])
                    datafr2 = datafr
                else: 
                    datafr = binance.get_klines(pair=instrument, **params_binance['short'])
                    datafr2 = datafr[-120:-1]
            except:
                print("\nAction required: An Exception has occured\n\n"
                "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
                    +" During request of %s data for currency pair '%s' from Binance"
                            % (timeFrame, instrument))
                list_of_levels.append('N/A')
                list_of_rewards.append('N/A')
                list_of_risks.append('N/A')
                list_of_ratios.append('N/A')
                continue
            # datafr2 = datafr[-120:-1]
            trend = df_object['long_term'].loc[instrument]['LT_trend']

            self.step2_descision_loop(datafr=datafr2, trend=trend,
                                instrument=instrument,
                                list_of_levels=list_of_levels,
                                list_of_rewards=list_of_rewards,
                                list_of_risks=list_of_risks,
                                list_of_ratios=list_of_ratios,
                                Watchlist=df_object)
            seconds(0.25)
            
        mask = [isinstance(i, float) for i in list_of_levels]
        df_object['Key level'] = list_of_levels
        df_object['Reward'] = list_of_rewards
        df_object['Risk'] = list_of_risks
        df_object['Reward vs. Risk'] = list_of_ratios
        df_object['Trend (1d)'] = [df_object['long_term'].loc[instrument]['LT_trend']
                                                    for instrument in df_object.index.values]
        df_object=df_object[mask]
        side = []
        for trend in df_object['Trend (1d)']:
            if trend=="uptrend":
                side.append('LONG')
            else:
                side.append('SHORT')
        df_object['Side'] = side
        df_object = df_object[['Trend (1d)', 'Side', 'Key level','Reward', 
                                                'Risk', 'Reward vs. Risk']]
        
        if len(df_object) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(df_object.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response

    # ANCHOR Step2_bitmex
    def Step2_bitmex(self, watchlist, timeFrame="short"):
        list_of_levels = []
        list_of_rewards = []
        list_of_risks = []
        list_of_ratios = []
        df_object=watchlist.copy()
        response = {}
        error_message = ""

        for instrument in df_object.index.values:
            try:
                if timeFrame == "intermediate": 
                    datafr = bitmex.get_klines(instrument=instrument, **params_bitmex['itermediate'])
                    datafr2 = datafr
                else: 
                    datafr = bitmex.get_klines(instrument=instrument, **params_bitmex['short'])
                    datafr2 = datafr[-120:-1]
            except:
                print("\nAction required: An Exception has occured\n\n"
                "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
                    +" During request of %s data for currency pair '%s' from Bitmex"
                            % (timeFrame, instrument))
                list_of_levels.append('N/A')
                list_of_rewards.append('N/A')
                list_of_risks.append('N/A')
                list_of_ratios.append('N/A')
                continue

            # datafr2 = datafr[-120:-1]
            trend = df_object['long_term'].loc[instrument]['LT_trend']

            self.step2_descision_loop(datafr=datafr2, trend=trend,
                                instrument=instrument,
                                list_of_levels=list_of_levels,
                                list_of_rewards=list_of_rewards,
                                list_of_risks=list_of_risks,
                                list_of_ratios=list_of_ratios,
                                Watchlist=df_object)
            seconds(0.25)
            
        mask = [isinstance(i, float) for i in list_of_levels]
        df_object['Key level'] = list_of_levels
        df_object['Reward'] = list_of_rewards
        df_object['Risk'] = list_of_risks
        df_object['Reward vs. Risk'] = list_of_ratios
        df_object['Trend (1d)'] = [df_object['long_term'].loc[instrument]['LT_trend']
                                                    for instrument in df_object.index.values]
        df_object=df_object[mask]
        side = []
        for trend in df_object['Trend (1d)']:
            if trend=="uptrend":
                side.append('LONG')
            else:
                side.append('SHORT')
        df_object['Side'] = side
        df_object = df_object[['Trend (1d)', 'Side', 'Key level','Reward', 
                                                'Risk', 'Reward vs. Risk']]
        
        if len(df_object) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(df_object.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response

    # ANCHOR Step2_oanda
    def Step2_oanda(self, watchlist, timeFrame="short"):
        list_of_levels = []
        list_of_rewards = []
        list_of_risks = []
        list_of_ratios = []
        df_object=watchlist.copy()
        response = {}
        error_message = ""

        for instrument in df_object.index.values:
            try:
                if timeFrame == "intermediate": 
                    datafr = oanda.CandlesticksData(instrument=instrument, params=params_oanda['itermediate'])
                    datafr2 = datafr
                else: 
                    datafr = oanda.CandlesticksData(instrument=instrument, params=params_oanda['short'])
                    datafr2 = datafr[-120:-1]
            except:
                print("\nAction required: An Exception has occured\n\n"
                "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
                    +" During request of %s data for currency pair '%s' from Oanda"
                            % (timeFrame, instrument))
                list_of_levels.append('N/A')
                list_of_rewards.append('N/A')
                list_of_risks.append('N/A')
                list_of_ratios.append('N/A')
                continue

            # datafr2 = datafr[-120:-1]
            trend = df_object['long_term'].loc[instrument]['LT_trend']

            self.step2_descision_loop(datafr=datafr2, trend=trend,
                                instrument=instrument,
                                list_of_levels=list_of_levels,
                                list_of_rewards=list_of_rewards,
                                list_of_risks=list_of_risks,
                                list_of_ratios=list_of_ratios,
                                Watchlist=df_object)
            seconds(0.25)
            
        mask = [isinstance(i, float) for i in list_of_levels]
        df_object['Key level'] = list_of_levels
        df_object['Reward'] = list_of_rewards
        df_object['Risk'] = list_of_risks
        df_object['Reward vs. Risk'] = list_of_ratios
        df_object['Trend (1d)'] = [df_object['long_term'].loc[instrument]['LT_trend']
                                                    for instrument in df_object.index.values]
        df_object=df_object[mask]
        side = []
        for trend in df_object['Trend (1d)']:
            if trend=="uptrend":
                side.append('LONG')
            else:
                side.append('SHORT')
        df_object['Side'] = side
        df_object = df_object[['Trend (1d)', 'Side', 'Key level','Reward', 
                                                'Risk', 'Reward vs. Risk']]
        
        if len(df_object) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(df_object.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response

    # ANCHOR Step2_poloniex
    def Step2_poloniex(self, watchlist, timeFrame="short"):
        list_of_levels = []
        list_of_rewards = []
        list_of_risks = []
        list_of_ratios = []
        df_object=watchlist.copy()
        response = {}
        error_message = ""

        for instrument in df_object.index.values:
            try:
                if timeFrame == "intermediate": 
                    datafr = poloniex.get_klines(currencyPair=instrument, **params_poloniex['itermediate'])
                    datafr2 = datafr
                else: 
                    datafr = poloniex.get_klines(currencyPair=instrument, **params_poloniex['short'])
                    datafr2 = datafr[-120:-1]
            except:
                print("\nAction required: An Exception has occured\n\n"
                "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
                    +" During request of %s data for currency pair '%s' from Poloniex"
                            % (timeFrame, instrument))
                list_of_levels.append('N/A')
                list_of_rewards.append('N/A')
                list_of_risks.append('N/A')
                list_of_ratios.append('N/A')
                continue
            # datafr2 = datafr[-120:-1]
            trend = df_object['long_term'].loc[instrument]['LT_trend']

            self.step2_descision_loop(datafr=datafr2, trend=trend,
                                instrument=instrument,
                                list_of_levels=list_of_levels,
                                list_of_rewards=list_of_rewards,
                                list_of_risks=list_of_risks,
                                list_of_ratios=list_of_ratios,
                                Watchlist=df_object)
            seconds(0.25)
            
        mask = [isinstance(i, float) for i in list_of_levels]
        df_object['Key level'] = list_of_levels
        df_object['Reward'] = list_of_rewards
        df_object['Risk'] = list_of_risks
        df_object['Reward vs. Risk'] = list_of_ratios
        df_object['Trend (1d)'] = [df_object['long_term'].loc[instrument]['LT_trend']
                                                    for instrument in df_object.index.values]
        df_object=df_object[mask]
        side = []
        for trend in df_object['Trend (1d)']:
            if trend=="uptrend":
                side.append('LONG')
            else:
                side.append('SHORT')
        df_object['Side'] = side
        df_object = df_object[['Trend (1d)', 'Side', 'Key level','Reward', 
                                                'Risk', 'Reward vs. Risk']]
        
        if len(df_object) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(df_object.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response

    # # ANCHOR Step2 - old-version
    # def Step2(self, datafr, trend):
    #     datafr2 = datafr[-120:]

    #     if trend == 'uptrend':
    #         # determine the key level using the resistance_level method
    #         # from the Strategy module
    #         key_level = self.resistance_level(datafr=datafr2, trend=trend)
            
    #         if isinstance(key_level, float):
    #         # if the level has been test more than 4 times keep value else discard
    #             if self.key_level_test(level=key_level, datafr=datafr2) > 4:
    #                 return key_level
    #             else:
    #                 return 'N/A'
    #         else:
    #             return 'N/A'

    #     elif trend == 'downtrend':
    #         # determine the key level using the support_level method
    #         # from the Strategy module
    #         key_level = self.support_level(datafr=datafr2, trend=trend)

    #         if isinstance(key_level, float):
    #             # if the level has been test more than 4 times keep value else discard
    #             if self.key_level_test(level=key_level, datafr=datafr2) > 4:
    #                 return key_level
    #             else:
    #                 return 'N/A'
    #         else:
    #             return 'N/A'

    #     else:
    #         return 'N/A'
# !SECTION End of step 2 section

# SECTION 2.3 STEP 3: Trade signals
    # ANCHOR Step3_binance
    def Step3_binance(self, watchlist):
        output = []
        # list_of_risks = []
        # list_of_ratios = []
        df_object = watchlist.copy()
        response = {}
        error_message = ""

        for instrument in df_object.index.values:
            # try:
            #     ohlc2 = binance.get_klines(pair=instrument, **params_binance['itermediate']) # ***
            # except:
            #     print("\nAction required: An Exception has occured\n\n"
            #         "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
            #             +" During request of intermediate data for currency pair '%s' from Binance"
            #                     % instrument) # ***
            #     output.append(0)
            #     # list_of_risks.append(0)
            #     # list_of_ratios.append(0)
            #     continue
                
            try:
                ohlc3 = binance.get_klines(pair=instrument, **params_binance['short']) # ***
            except:
                print("\nAction required: An Exception has occured\n\n"
                    "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
                        +" During request of short-term data for currency pair '%s' from Binance"
                                % instrument) # ***
                output.append(0)
                # list_of_risks.append(0)
                # list_of_ratios.append(0)
                continue
                    
            s_trend = self.short_term_trend(ohlc3)
            # i_trend = self.intermediate_trend(ohlc2)
            trn_points = self.turning_points(ohlc3[-40:-1])
            curr_prc = binance.curr_price(symbol=instrument) # ***
            l_trend = df_object['Trend (1d)'].loc[instrument]
            key_level = df_object['Key level'].loc[instrument]
            max_peak = trn_points['highest-high'] # most recent high
            lwst_point = trn_points['lowest-low'] # most recent low

            if (curr_prc > key_level
            and curr_prc >= max_peak
            and max_peak > key_level
            and s_trend==l_trend=='uptrend'):
                # risk = self.var_diff(key_level, lwst_point)
                # risk_v_rwrd = df_object['Reward'].loc[instrument]/risk
                output.append(1)
                # list_of_risks.append(round(risk, 2))
                # list_of_ratios.append(round(risk_v_rwrd, 2))
                

            elif (curr_prc < key_level
            and curr_prc <= lwst_point
            and lwst_point < key_level
            and s_trend==l_trend=='downtrend'):
                # risk = self.var_diff(key_level, lwst_point)
                # risk_v_rwrd = df_object['Reward'].loc[instrument]/risk
                output.append(-1)
                # list_of_risks.append(round(risk, 2))
                # list_of_ratios.append(round(risk_v_rwrd, 2))

            else:
                output.append(0)
                # list_of_risks.append(0)
                # list_of_ratios.append(0)
            seconds(0.25)
        
        mask = [i in [1,-1] for i in output]
        df_object['Signals'] = output
        # df_object['Risk'] = list_of_risks
        # df_object['Risk_v_Reward'] = list_of_ratios
        df_object=df_object[mask]
        
        if len(df_object) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(df_object.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response

    # ANCHOR Step3_bitmex
    def Step3_bitmex(self, watchlist):
        output = []
        # list_of_risks = []
        # list_of_ratios = []
        df_object = watchlist.copy()
        response = {}
        error_message = ""

        for instrument in df_object.index.values:
            # try:
            #     ohlc2 = bitmex.get_klines(instrument=instrument, **params_bitmex['itermediate']) # ***
            # except:
            #     print("\nAction required: An Exception has occured\n\n"
            #         "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
            #             +" During request of intermediate data for currency pair '%s' from Bitmex"
            #                     % instrument) # ***
            #     output.append(0)
            #     # list_of_risks.append(0)
            #     # list_of_ratios.append(0)
            #     continue
                
            try:
                ohlc3 = bitmex.get_klines(instrument=instrument, **params_bitmex['short']) # ***
            except:
                print("\nAction required: An Exception has occured\n\n"
                    "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
                        +" During request of short-term data for currency pair '%s' from Bitmex"
                                % instrument) # ***
                output.append(0)
                # list_of_risks.append(0)
                # list_of_ratios.append(0)
                continue
                    
            s_trend = self.short_term_trend(ohlc3)
            # i_trend = self.intermediate_trend(ohlc2)
            trn_points = self.turning_points(ohlc3[-40:-1])
            curr_prc = bitmex.curr_price(symbol=instrument) # ***
            l_trend = df_object['Trend (1d)'].loc[instrument]
            key_level = df_object['Key level'].loc[instrument]
            max_peak = trn_points['highest-high']
            lwst_point = trn_points['lowest-low']

            if (curr_prc > key_level
            and curr_prc >= max_peak
            and max_peak > key_level
            and s_trend==l_trend=='uptrend'):
                # risk = self.var_diff(key_level, lwst_point)
                # risk_v_rwrd = df_object['Reward'].loc[instrument]/risk
                output.append(1)
                # list_of_risks.append(round(risk, 2))
                # list_of_ratios.append(round(risk_v_rwrd, 2))
                

            elif (curr_prc < key_level
            and curr_prc <= lwst_point
            and lwst_point < key_level
            and s_trend==l_trend=='downtrend'):
                # risk = self.var_diff(key_level, lwst_point)
                # risk_v_rwrd = df_object['Reward'].loc[instrument]/risk
                output.append(-1)
                # list_of_risks.append(round(risk, 2))
                # list_of_ratios.append(round(risk_v_rwrd, 2))

            else:
                output.append(0)
                # list_of_risks.append(0)
                # list_of_ratios.append(0)
            seconds(0.25)
        
        mask = [i in [1,-1] for i in output]
        df_object['Signals'] = output
        # df_object['Risk'] = list_of_risks
        # df_object['Risk_v_Reward'] = list_of_ratios
        df_object=df_object[mask]
        
        if len(df_object) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(df_object.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response

    # ANCHOR Step3_oanda
    def Step3_oanda(self, watchlist):
        output = []
        # list_of_risks = []
        # list_of_ratios = []
        df_object = watchlist.copy()
        response = {}
        error_message = ""

        for instrument in df_object.index.values:
            # try:
            #     ohlc2 = oanda.CandlesticksData(instrument=instrument, 
            #                                         params=params_oanda['itermediate']) # ***
            # except:
            #     print("\nAction required: An Exception has occured\n\n"
            #         "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
            #             +" During request of intermediate data for currency pair '%s' from Oanda"
            #                     % instrument) # ***
            #     output.append(0)
            #     # list_of_risks.append(0)
            #     # list_of_ratios.append(0)
            #     continue
                
            try:
                ohlc3 = oanda.CandlesticksData(instrument=instrument, 
                                                            params=params_oanda['short']) # ***
            except:
                print("\nAction required: An Exception has occured\n\n"
                    "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
                        +" During request of short-term data for currency pair '%s' from Oanda"
                                % instrument) # ***
                output.append(0)
                # list_of_risks.append(0)
                # list_of_ratios.append(0)
                continue
                    
            s_trend = self.short_term_trend(ohlc3)
            # i_trend = self.intermediate_trend(ohlc2)
            trn_points = self.turning_points(ohlc3[-40:-1])
            curr_prc = oanda.curr_price(symbol=instrument) # ***
            l_trend = df_object['Trend (1d)'].loc[instrument]
            key_level = df_object['Key level'].loc[instrument]
            max_peak = trn_points['highest-high']
            lwst_point = trn_points['lowest-low']

            if (curr_prc > key_level
            and curr_prc >= max_peak
            and max_peak > key_level
            and s_trend==l_trend=='uptrend'):
                # risk = self.var_diff(key_level, lwst_point)
                # risk_v_rwrd = df_object['Reward'].loc[instrument]/risk
                output.append(1)
                # list_of_risks.append(round(risk, 2))
                # list_of_ratios.append(round(risk_v_rwrd, 2))
                

            elif (curr_prc < key_level
            and curr_prc <= lwst_point
            and lwst_point < key_level
            and s_trend==l_trend=='downtrend'):
                # risk = self.var_diff(key_level, lwst_point)
                # risk_v_rwrd = df_object['Reward'].loc[instrument]/risk
                output.append(-1)
                # list_of_risks.append(round(risk, 2))
                # list_of_ratios.append(round(risk_v_rwrd, 2))

            else:
                output.append(0)
                # list_of_risks.append(0)
                # list_of_ratios.append(0)
            seconds(0.25)
        
        mask = [i in [1,-1] for i in output]
        df_object['Signals'] = output
        # df_object['Risk'] = list_of_risks
        # df_object['Risk_v_Reward'] = list_of_ratios
        df_object=df_object[mask]
        
        if len(df_object) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(df_object.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response

    # ANCHOR Step3_poloniex
    def Step3_poloniex(self, watchlist):
        output = []
        # list_of_risks = []
        # list_of_ratios = []
        df_object = watchlist.copy()
        response = {}
        error_message = ""

        for instrument in df_object.index.values:
            # try:
            #     ohlc2 = poloniex.get_klines(currencyPair=instrument, 
            #                                             **params_poloniex['itermediate']) # ***
            # except:
            #     print("\nAction required: An Exception has occured\n\n"
            #         "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
            #             +" During request of intermediate data for currency pair '%s' from Poloniex"
            #                     % instrument) # ***
            #     output.append(0)
            #     # list_of_risks.append(0)
            #     # list_of_ratios.append(0)
            #     continue
                
            try:
                ohlc3 = poloniex.get_klines(currencyPair=instrument,
                                                                **params_poloniex['short']) # ***
            except:
                print("\nAction required: An Exception has occured\n\n"
                    "    On %s\n    Error " % datetime.datetime.now().replace(microsecond=0)
                        +" During request of short-term data for currency pair '%s' from Poloniex"
                                % instrument) # ***
                output.append(0)
                # list_of_risks.append(0)
                # list_of_ratios.append(0)
                continue
                    
            s_trend = self.short_term_trend(ohlc3)
            # i_trend = self.intermediate_trend(ohlc2)
            trn_points = self.turning_points(ohlc3[-40:-1])
            curr_prc = poloniex.curr_price(symbol=instrument) # ***
            l_trend = df_object['Trend (1d)'].loc[instrument]
            key_level = df_object['Key level'].loc[instrument]
            max_peak = trn_points['highest-high']
            lwst_point = trn_points['lowest-low']

            if (curr_prc > key_level
            and curr_prc >= max_peak
            and max_peak > key_level
            and s_trend==l_trend=='uptrend'):
                # risk = self.var_diff(key_level, lwst_point)
                # risk_v_rwrd = df_object['Reward'].loc[instrument]/risk
                output.append(1)
                # list_of_risks.append(round(risk, 2))
                # list_of_ratios.append(round(risk_v_rwrd, 2))
                

            elif (curr_prc < key_level
            and curr_prc <= lwst_point
            and lwst_point < key_level
            and s_trend==l_trend=='downtrend'):
                # risk = self.var_diff(key_level, lwst_point)
                # risk_v_rwrd = df_object['Reward'].loc[instrument]/risk
                output.append(-1)
                # list_of_risks.append(round(risk, 2))
                # list_of_ratios.append(round(risk_v_rwrd, 2))

            else:
                output.append(0)
                # list_of_risks.append(0)
                # list_of_ratios.append(0)
            seconds(0.25)
        
        mask = [i in [1,-1] for i in output]
        df_object['Signals'] = output
        # df_object['Risk'] = list_of_risks
        # df_object['Risk_v_Reward'] = list_of_ratios
        df_object=df_object[mask]
        
        if len(df_object) != 0 and error_message == "":
            response['status'] = 'OK'
            response['data'] = json.loads(df_object.to_json())
            response['message'] = ''
        else:
            response['status'] = 'ERROR'
            response['data'] = {}
            response['message'] = error_message

        return response
# !SECTION End of section 2.3
# !SECTION end of Signal class
