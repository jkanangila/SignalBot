""" Features:   1. From the watchlist, request 5 klines every 5 minutes interval;
                2. Check for a breakout above/bellow resistance/support line;
                3. Send email notification and save results as csv.
v1.0.0
"""
import datetime

print(" =================================================================\n" 
        + "|                        SignalBot.v3.0.0                         |\n"
      + "|                       AlertSystem.v1.0.0                        |"
        + "\n =================================================================\n")

print("%s | Initialization" % 
        datetime.datetime.now().replace(microsecond=0))

print("\n        Importing modules...")
#==================================================================================
# ANCHOR Import statements
import os

from configuration import *
from exchanges import *
from pause import seconds

from strategy_TendAlignment import *
from watchlistConfg import *

print("            Modules sucessfully imported\n")
#==================================================================================

# ANCHOR Save directory
print("\n        Creating save directory...")
try:
    path = os.path.join(os.getcwd(), 'Saves\AlertSystem')
    if os.path.exists(path):
        print("            Directory already exists...\n")
        pass
    else:
        os.makedirs(path)
        print("            Directory created.\n")
    print("%s | Program successfully Initialized" % 
            datetime.datetime.now().replace(microsecond=0))
except:
    print('On %s' % datetime.datetime.now().replace(microsecond=0)
        + " \nAction required: Failed to create save files directory\n")
#==================================================================================

signalCopyBnc = None 
signalCopyBtx = None
signalCopyOdn = None
signalCopyPlx = None

# ANCHOR Main while loop
while True:
    if datetime.datetime.now().minute in range(0,60,5):
        # SECTION 1: Binance
        print("Binance Exchange" + "\n----------------")
        counter = 0
        while counter < 5:
            try:
                # Create exchange-instance
                binance = BinanceExchange(**keys['binance']) # chng instance
                signal = {'instrument':[], 'signal':[]}

        # SECTION 1.1: Descision loop
                for instrument in list(watchlistBinance.index.values): # chng watchlist
                    try:
                        current_price = binance.curr_price(symbol=instrument)  
                        ohlc = binance.get_klines(pair=instrument, 
                                                        **params_binance['short'])
                        ohlc = ohlc[:-1]
                        retracement = Strategy().retracement(datafr=ohlc, 
                                                                timeframe='short_term')
                        if (current_price > watchlistBinance.loc[instrument]['price_level'] 
                        and retracement[2] == True
                        and retracement[1] == 'uptrend'
                        and watchlistBinance.loc[instrument]['res/supp'] == 1): # chng watchlist
                            signal['instrument'].append(instrument)
                            signal['signal'].append(1)
                        
                        else:
                            signal['instrument'].append(instrument)
                            signal['signal'].append(0)
                        
                        seconds(0.250) 
                    except:
                        continue
                maskBull = [i==1 for i in signal['signal']]

                signal = pd.DataFrame(signal)
                signalBull = signal[maskBull]
        # !SECTION End of section 1.1

        # SECTION 1.2: Notification
                if signal.equals(signalCopyBnc): # NOTE if actual datafr is equal to last iteration's: (sleep)
                    print("on %s | Binance - 1.2" % datetime.datetime.now().replace(microsecond=0)
                            + "\n    Status update: No change detected from last iteration.")
                    break

                else: # NOTE if the 2 datafr are not similar
                    # ANCHOR Bullish descision section
                    if len(signalBull) > 0: # NOTE if bull signals are idenfied: send email and save as csv
                        # Email notification
                        body = signalBull.to_html()
                        subject = "Binance: Bullish Signals Identified!" #***
                        try:
                            UserDefinedFxns().send_email(SUBJECT=subject, BODY=body)
                        except:
                            print('\n\nOn %s | Section ... \n    Email' % 
                            datetime.datetime.now().replace(microsecond=0)
                            + ' Email Notification Status: Failed...\n') 
                        # save watchlist to csv
                        try:
                            _str = ('Binance - BullishSignals - %s.csv' %
                            datetime.datetime.strftime(datetime.datetime.now(), "%b-%d %H-%M-%S"))
                            nPath = os.path.join(path, _str)
                            signalBull.to_csv(nPath) 

                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Data saved @ %s \n" % os.getcwd()) 
                        except:
                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Failed to save" + " DataFrame\n")
                    else: # NOTE if no bull signals were identified
                        print("on %s | Binance - 1.2" % datetime.datetime.now().replace(microsecond=0)
                                + "\n    Status update: No bullish signal...") 
                    
                    signalCopyBnc = signal
                    break
            except:
                print('\nOn %s | Section 1' % 
                        datetime.datetime.now().replace(microsecond=0) 
                        + "\n\n    Action required: Exception occured during request/handling of data"
                        + " from Binance's servers."
                        + "\n    Retrying...\n")
                seconds(30)
                counter += 1
# !SECTION End of section 1.2
# !SECTION End of binance
#==================================================================================================================

# SECTION 2: Bitmex
        print("Bitmex Exchange" + "\n---------------")
        counter = 0
        while counter < 5:
            try:
                # Create exchange-instance
                bitmex = BitmexExchange(**keys['bitmex-live']) # chng instance
                signal = {'instrument':[], 'signal':[]}

        # SECTION 2.1: Descision loop
                for instrument in list(watchlistBitmex.index.values): # chng watchlist
                    try:
                        current_price = bitmex.curr_price(symbol=instrument) 
                        ohlc = bitmex.get_klines(instrument=instrument, 
                                                **params_bitmex['short']) # chng client and fxn
                        retracement = Strategy().retracement(datafr=ohlc, 
                                                                timeframe='short_term')
                        if (current_price > watchlistBitmex.loc[instrument]['price_level'] 
                        and retracement[2] == True
                        and retracement[1] == 'uptrend'
                        and watchlistBitmex.loc[instrument]['res/supp'] == 1): # chng watchlist
                            signal['instrument'].append(instrument)
                            signal['signal'].append(1)
                        
                        elif (current_price < watchlistBitmex.loc[instrument]['price_level'] 
                        and retracement[2] == True
                        and retracement[1] == 'downtrend'
                        and watchlistBitmex.loc[instrument]['res/supp'] == -1): # chng watchlist
                            signal['instrument'].append(instrument)
                            signal['signal'].append(-1)
                        else:
                            signal['instrument'].append(instrument)
                            signal['signal'].append(0)
                        
                        seconds(0.250)
                    except:
                        continue
                maskBull = [i==1 for i in signal['signal']]
                maskBear = [i==-1 for i in signal['signal']]

                signal = pd.DataFrame(signal)
                signalBull = signal[maskBull]
                signalBear = signal[maskBear]
        # !SECTION End of section 2.1

        # SECTION 2.2: Notification
                if signal.equals(signalCopyBtx): # NOTE if actual datafr is equal to last iteration's: (sleep)
                    print("on %s | Bitmex - 2.2" % datetime.datetime.now().replace(microsecond=0)
                            + "\n    Status update: No change detected from last iteration.") # chng message
                    break

                else: # NOTE if the 2 datafr are not similar
                    # ANCHOR Bullish descision section
                    if len(signalBull) > 0: # NOTE if bull signals were idenfied: send email and save as csv
                        # Email notification
                        body = signalBull.to_html()
                        subject = "Bitmex: Bullish Signals Identified!" #***
                        try:
                            UserDefinedFxns().send_email(SUBJECT=subject, BODY=body)
                        except:
                            print('\n\nOn %s | Section 2.2 \n    Email' % 
                            datetime.datetime.now().replace(microsecond=0)
                            + ' Email Notification Status: Failed...\n') # chng message
                        # save watchlist to csv
                        try:
                            _str = ('Bitmex - BullishSignals - %s.csv' %
                            datetime.datetime.strftime(datetime.datetime.now(), "%b-%d %H-%M-%S"))
                            nPath = os.path.join(path, _str)
                            signalBull.to_csv(nPath)

                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Data saved @ %s \n" % os.getcwd()) # exchange name
                        except:
                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Failed to save" + " DataFrame\n")

                    else: # NOTE if no bull signals were identified
                        print("on %s | Bitmex - 2.2" % datetime.datetime.now().replace(microsecond=0)
                                + "\n    Status update: No bullish trade signal.")

                    # ANCHOR Bearish descision section
                    if len(signalBear) > 0: # NOTE if bearish signals were idenfied: send email and save as csv
                        # Email notification
                        body = signalBear.to_html()
                        subject = "Bitmex: Bearish Signals Identified!" #****
                        try:
                            UserDefinedFxns().send_email(SUBJECT=subject, BODY=body)
                        except:
                            print('\n\nOn %s | Section 2.2 \n    Email' % 
                            datetime.datetime.now().replace(microsecond=0)
                            + ' Email Notification Status: Failed...\n') # chng message
                        # save watchlist to csv
                        try:
                            _str = ('Bitmex - Bearish - %s.csv' %
                            datetime.datetime.strftime(datetime.datetime.now(), "%b-%d %H-%M-%S"))
                            nPath = os.path.join(path, _str)
                            signalBear.to_csv(nPath)  # exchange name
                        
                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Data saved @ %s \n" % os.getcwd()) # exchange name
                        except:
                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Failed to save" + " DataFrame\n")
                    
                    else: # NOTE if no bull signals were identified
                        print("on %s | Bitmex - 2.2" % datetime.datetime.now().replace(microsecond=0)
                                + "\n    Status update: No bearish trade signal.") # exchange name
                    
                    signalCopyBtx = signal
                    break
            except:
                print('\nOn %s | Section 2' % 
                        datetime.datetime.now().replace(microsecond=0) 
                        + "\n\n    Action required: Exception occured during request/handling of data"
                        + " from Bitmex's servers."
                        + "\n    Retrying...\n")
                seconds(30)
                counter += 1
        # !SECTION End of section 2.2
        #!SECTION End of bitmex section
        #==================================================================================================================

        # SECTION 3: Oanda
        print("Oanda Exchange" + "\n--------------")
        counter = 0
        while counter < 5:
            try:
                # Create exchange-instance
                oanda = OandaExchange(**keys['oanda-live']) # chng instance
                signal = {'instrument':[], 'signal':[]}

        # SECTION 3.1: Descision loop
                for instrument in list(watchlistOanda.index.values): # chng watchlist
                    try:
                        current_price = oanda.curr_price(symbol=instrument) 
                        ohlc = oanda.CandlesticksData(instrument=instrument, 
                                                        params=params_oanda['short']) # chng client and fxn
                        ohlc = ohlc[:-1]
                        retracement = Strategy().retracement(datafr=ohlc, 
                                                                timeframe='short_term')
                        if (current_price > watchlistOanda.loc[instrument]['price_level'] 
                        and retracement[2] == True
                        and retracement[1] == 'uptrend'
                        and watchlistOanda.loc[instrument]['res/supp'] == 1): # chng watchlist
                            signal['instrument'].append(instrument)
                            signal['signal'].append(1)
                        
                        elif (current_price < watchlistOanda.loc[instrument]['price_level'] 
                        and retracement[2] == True
                        and retracement[1] == 'downtrend'
                        and watchlistOanda.loc[instrument]['res/supp'] == -1): # chng watchlist
                            signal['instrument'].append(instrument)
                            signal['signal'].append(-1)
                        
                        else:
                            signal['instrument'].append(instrument)
                            signal['signal'].append(0)
                        
                        seconds(0.250)
                    except:
                        continue

                maskBull = [i==1 for i in signal['signal']]
                maskBear = [i==-1 for i in signal['signal']]

                signal = pd.DataFrame(signal)
                signalBull = signal[maskBull]
                signalBear = signal[maskBear]
        # !SECTION End of section 3.1

        # SECTION 3.2: Notification
                if signal.equals(signalCopyOdn): # NOTE if actual datafr is equal to last iteration's: (sleep)
                    print("on %s | Oanda - 3.2" % datetime.datetime.now().replace(microsecond=0)
                            + "\n    Status update: No change detected from last iteration.") # chng message
                    break

                else: # NOTE if the 2 datafr are not similar
                    # ANCHOR Bullish descision section
                    if len(signalBull) > 0: # NOTE if bull signals were idenfied: send email and save as csv
                        # Email notification
                        body = signalBull.to_html()
                        subject = "OANDA: Bullish Signals Identified!" #***
                        try:
                            UserDefinedFxns().send_email(SUBJECT=subject, BODY=body)
                        except:
                            print('\n\nOn %s | Section 3.2 \n    Email' % 
                            datetime.datetime.now().replace(microsecond=0)
                            + ' Email Notification Status: Failed...\n') # chng message
                        # save watchlist to csv
                        try:
                            _str = ('Oanda - BullishSignals - %s.csv' %
                            datetime.datetime.strftime(datetime.datetime.now(), "%b-%d %H-%M-%S"))
                            nPath = os.path.join(path, _str)
                            signalBull.to_csv(nPath)  # exchange name

                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Data saved @ %s \n" % os.getcwd()) # exchange name
                        except:
                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Failed to save" + " DataFrame\n")

                    else: # NOTE if no bull signals were identified
                        print("on %s | Oanda - 3.2" % datetime.datetime.now().replace(microsecond=0)
                                + "\n    Status update: No bullish trade signal.")

                    # ANCHOR Bearish descision section
                    if len(signalBear) > 0: # NOTE if bearish signals were idenfied: send email and save as csv
                        # Email notification
                        body = signalBear.to_html()
                        subject = "OANDA: Bearish Signals Identified!" #****
                        try:
                            UserDefinedFxns().send_email(SUBJECT=subject, BODY=body)
                        except:
                            print('\n\nOn %s | Section 3.2 \n    Email' % 
                            datetime.datetime.now().replace(microsecond=0)
                            + ' Email Notification Status: Failed...\n') # chng message
                        # save watchlist to csv
                        try:
                            _str = ('Oanda - Bearish - %s.csv' %
                            datetime.datetime.strftime(datetime.datetime.now(), "%b-%d %H-%M-%S"))
                            nPath = os.path.join(path, _str)
                            signalBear.to_csv(nPath)  # exchange name

                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Data saved @ %s \n" % os.getcwd()) # exchange name
                        except:
                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Failed to save" + " DataFrame\n")

                    else: # NOTE if no bull signals were identified
                        print("on %s | Oanda - 3.2" % datetime.datetime.now().replace(microsecond=0)
                                + "\n    Status update: No trade signal.")
                    
                    signalCopyOdn = signal
                    break
            except:
                print('\nOn %s | Section 3' % 
                        datetime.datetime.now().replace(microsecond=0) 
                        + "\n\n    Action required: Exception occured during request/handling of data"
                        + " from Oanda's servers."
                        + "\n    Retrying...\n")
                seconds(30)
                counter += 1
        # !SECTION End of section 3.2
        # !SECTION End of Oanda loop
        #==================================================================================================================

        # SECTION 4: Poloniex
        print("Poloniex Exchange" + "\n-----------------")
        counter = 0
        while counter < 5:
            try:
                # Create exchange-instance
                poloniex = PoloniexEchange() # chng instance
                signal = {'instrument':[], 'signal':[]}

        # SECTION 4.1: Descision loop
                for instrument in list(watchlistPoloniex.index.values): # chng watchlist
                    try:
                        current_price = poloniex.curr_price(symbol=instrument) 
                        ohlc = poloniex.get_klines(currencyPair=instrument,
                                                    **params_poloniex['short']) # chng client and fxn
                        ohlc = ohlc[:-1] 
                        retracement = Strategy().retracement(datafr=ohlc, 
                                                                timeframe='short_term')
                        if (current_price > watchlistPoloniex.loc[instrument]['price_level'] 
                        and retracement[2] == True
                        and retracement[1] == 'uptrend'
                        and watchlistPoloniex.loc[instrument]['res/supp'] == 1): # chng watchlist
                            signal['instrument'].append(instrument)
                            signal['signal'].append(1)
                        
                        elif (current_price < watchlistPoloniex.loc[instrument]['price_level'] 
                        and retracement[2] == True
                        and retracement[1] == 'downtrend'
                        and watchlistPoloniex.loc[instrument]['res/supp'] == -1): # chng watchlist
                            signal['instrument'].append(instrument)
                            signal['signal'].append(-1)
                        else:
                            signal['instrument'].append(instrument)
                            signal['signal'].append(0)
                        
                        seconds(0.250)
                    except:
                        continue

                maskBull = [i==1 for i in signal['signal']]
                maskBear = [i==-1 for i in signal['signal']]

                signal = pd.DataFrame(signal)
                signalBull = signal[maskBull]
                signalBear = signal[maskBear]
        # !SECTION End of section 4.1

        # SECTION 4.2: Notification
                if signal.equals(signalCopyPlx): # NOTE if actual datafr is equal to last iteration's: (sleep)
                    print("on %s | Poloniex - 4.2" % datetime.datetime.now().replace(microsecond=0)
                            + "\n    Status update: No change detected from last iteration.") # chng message

                    actual_time = datetime.datetime.now()
                    _min,_sec = UserDefinedFxns().interval_counter(actual_time)
                    time_to_sleep = _min*60 + _sec
                    wake_up = actual_time + datetime.timedelta(seconds=time_to_sleep)

                    print("\n    Scheduled shutdown"
                            + "\n    Next request will happen"
                            + "  @ %s.\n" % wake_up.replace(microsecond=0))

                    seconds(time_to_sleep)
                    break

                else: # NOTE if the 2 datafr are not similar
                    # ANCHOR Bullish descision section
                    if len(signalBull) > 0: # NOTE if bull signals were idenfied: send email and save as csv
                        # Email notification
                        body = signalBull.to_html()
                        subject = "Poloniex: Bullish Signals Identified!" #***
                        try:
                            UserDefinedFxns().send_email(SUBJECT=subject, BODY=body)
                        except:
                            print('\n\nOn %s | Section 4.2 \n    Email' % 
                            datetime.datetime.now().replace(microsecond=0)
                            + ' Email Notification Status: Failed...\n') # chng message
                        # save watchlist to csv
                        try:
                            _str = ('Poloniex - BullishSignals - %s.csv' %
                            datetime.datetime.strftime(datetime.datetime.now(), "%b-%d %H-%M-%S"))
                            nPath = os.path.join(path, _str)
                            signalBull.to_csv(nPath)  # exchange name

                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Data saved @ %s \n" % os.getcwd()) # exchange name
                        except:
                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Failed to save" + " DataFrame\n")

                    else: # NOTE if no bull signals were identified
                        print("on %s | Poloniex - 4.2" % datetime.datetime.now().replace(microsecond=0)
                                + "\n    Status update: No bullish trade signal.") #***

                    # ANCHOR Bearish descision section
                    if len(signalBear) > 0: # NOTE if bearish signals were idenfied: send email and save as csv
                        # Email notification
                        body = signalBear.to_html()
                        subject = "Poloniex: Bearish Signals Identified!" #****
                        try:
                            UserDefinedFxns().send_email(SUBJECT=subject, BODY=body)
                        except:
                            print('\n\nOn %s | Section ... \n    Email' % 
                            datetime.datetime.now().replace(microsecond=0)
                            + ' Email Notification Status: Failed...\n') # chng message
                        # save watchlist to csv
                        try:
                            _str = ('Poloniex - Bearish - %s.csv' %
                            datetime.datetime.strftime(datetime.datetime.now(), "%b-%d %H-%M-%S"))
                            nPath = os.path.join(path, _str)
                            signalBear.to_csv(nPath)  # exchange name

                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Data saved @ %s \n" % os.getcwd()) # exchange name
                        except:
                            print("%s" % datetime.datetime.now().replace(microsecond=0)
                                            + " \n    Failed to save" + " DataFrame\n")
                    
                        # NOTE After deciding on bear signals for the last exchange, sleep till the interval is complete
                        actual_time = datetime.datetime.now()
                        _min,_sec = UserDefinedFxns().interval_counter(actual_time)
                        time_to_sleep = _min*60 + _sec
                        wake_up = actual_time + datetime.timedelta( seconds=time_to_sleep)

                        print("\n    Scheduled shutdown"
                                + "\n    Next request will happen"
                                + "  @ %s.\n" % wake_up.replace(microsecond=0))

                    else: # NOTE if no bearish signals were identified
                        print("on %s | Poloniex - 4.2" % datetime.datetime.now().replace(microsecond=0)
                                + "\n    Status update: No bearish trade signal.") # exchange name
                        
                        # NOTE After deciding on bear signals for the last exchange, sleep till the interval is complete
                        actual_time = datetime.datetime.now()
                        _min,_sec = UserDefinedFxns().interval_counter(actual_time)
                        time_to_sleep = _min*60 + _sec
                        wake_up = actual_time + datetime.timedelta( seconds=time_to_sleep)

                        print("\n    Scheduled shutdown"
                                + "\n    Next request will happen"
                                + "  @ %s.\n" % wake_up.replace(microsecond=0))
                    
                    signalCopyPlx = signal
                    break
            except:
                print('\nOn %s | Section 4' % 
                        datetime.datetime.now().replace(microsecond=0) 
                        + "\n\n    Action required: Exception occured during request/handling of data"
                        + " from Poloniex's servers."
                        + "\n    Retrying...\n")
                seconds(30)
                counter += 1
        # !SECTION End of section 4.2
        #!SECTION End of Poloniex section
        #==================================================================================================================
    else:
        actual_time = datetime.datetime.now()
        _min,_sec = UserDefinedFxns().interval_counter(actual_time)
        time_to_sleep = _min*60 + _sec
        wake_up = actual_time + datetime.timedelta( seconds=time_to_sleep)

        print("\n    Scheduled shutdown"
                + "\n    Next request will happen"
                + "  @ %s.\n" % wake_up.replace(microsecond=0))
        seconds(time_to_sleep)
        continue