""" Changes:    1.  Program now runs in a continuous loop 
                2.  Added a section to check for major trend and retracement, another to determine 
                    resistance/support, and another one to check minor trends for signals
                3.  Send notification once trade signals have been identified

v6.0.0
"""
# ANCHOR Module import
print(" =================================================================\n" 
        + "|                        SignalBot.v4.0.0                         |\n"
        + "|                            MainLoop                             |"
        + "\n =================================================================\n")
from configuration import *

print("Initialization" + "\n==============" )

print("        %s | Importing modules..." % 
        datetime.datetime.now().replace(microsecond=0))
try:
    import os
    from exchanges import *
    from pause import seconds
    from strategy_TendAlignment import *
#     from tabulate import tabulate
    print("        %s | Modules sucessfully imported\n" % 
            datetime.datetime.now().replace(microsecond=0))
except:
    raise ImportError("Could not find all the required modules")
#***********************************************************************************
#***********************************************************************************
# ANCHOR Save directory
try:
    path1 = os.path.join(os.getcwd(), 'Saves\watchlists')
    if os.path.exists(path1):
        print("        %s | Watchlists save directory already exists..." % 
            datetime.datetime.now().replace(microsecond=0))
        pass
    else:
        os.makedirs(path1)
        print("        %s | Watchlists save directory created." % 
            datetime.datetime.now().replace(microsecond=0))
    print("        Initialization complete")
except:
    print('On %s' % datetime.datetime.now().replace(microsecond=0)
        + " \nAction required: Failed to create save directories\n")
#***********************************************************************************
#***********************************************************************************
# SECTION 1ST LOOP

signalBinance = None
signalOanda = None

while True:
# ANCHOR 1.1. BINANCE
    print("*************" + "\n" + "*  BINANCE  *" + "\n" + "*************")
# ANCHOR 1.1.1 Selection of initial watchlist
    # Determine the list of pairs whose info should be reqested
    # request quoteVolume and volume for each instrument in USDT and BTC market
    print('\nStatus Update:'
                + '\n-------------'
                + '\n    On %s' % 
                datetime.datetime.now().replace(microsecond=0) 
                + "\n    BINANCE Exchange: Trying to decide on"
                + " the initial watchlist...\n")

    list_of_pair = binance.instruments_binance(list_of_pair)
    if list_of_pair['status']=='OK':
        list_of_pair=list_of_pair['data']['both']
    else:
        print(list_of_pair['message'])
        list_of_pair=list_of_pair['data']

# ANCHOR 1.1.2 Using market trend to refine watchlist
    counter_1bnc = 0
    while counter_1bnc < 5:
        try:
            print('\nStatus Update:'
                        + '\n-------------'
                        + '\n    On %s\n    Now requesting' % 
                            datetime.datetime.now().replace(microsecond=0)
                        + ' %s candlesticks from BINANCE servers to ' 
                        % params_binance['longterm']['interval']
                        + ' indentify trending \n    instruments'
                        + 'experiencing a minor pull back...\n')
            
            stp1_bnc = Signal().Step1_Binance(list_of_pair=list_of_pair)
            stp1_bnc = pd.DataFrame(stp1_bnc['data'])
            
            print('\nStatus Update:'
                        + '\n-------------'
                        + '\n    On %s\n    Analysis of' % 
                            datetime.datetime.now().replace(microsecond=0)
                        + ' %s candlesticks on BINANCE completed ' 
                        % params_binance['longterm']['interval']
                        + 'successfully.\n')
            break
        except:
            print('\nAction required: \n\n    On %s | Section 1.1.2' % 
            datetime.datetime.now().replace(microsecond=0) 
            + "\n    Failed to analyse longterm data on BINANCE.\n")
            seconds(30)
            counter_1bnc += 1

# ANCHOR Binance - Identify resistance/supports
    if len(stp1_bnc) != 0:
        counter_1bnc = 0
        while counter_1bnc < 5:
            try:
                print('\nStatus Update:'
                            + '\n-------------'
                            + '\n    On %s\n    Now requesting' % 
                                datetime.datetime.now().replace(microsecond=0)
                            + ' %s candlesticks from BINANCE servers to ' 
                            % params_binance['itermediate']['interval']
                            + 'indentify resistance/support \n    for '
                            + 'selected instruments...\n')

                stp2_bnc = Signal().Step2_binance(watchlist=stp1_bnc, timeFrame='intermediate')
                stp2_bnc = pd.DataFrame(stp2_bnc['data'])
                
                print('\nStatus Update:'
                            + '\n-------------'
                            + '\n    On %s\n    Analysis of' % 
                                datetime.datetime.now().replace(microsecond=0)
                            + ' %s candlesticks on BINANCE completed ' 
                            % params_binance['longterm']['interval']
                            + 'successfully.\n')
                
                try:
                    _str = ('Binance - Watchlist - %s.csv' %
                    datetime.datetime.strftime(datetime.datetime.now(), "%b-%d %H-%M-%S"))
                    nPath = os.path.join(path1, _str)
                    stp2_bnc.to_csv(nPath) 

                    print("        %s" % datetime.datetime.now().replace(microsecond=0)
                                    + " \n        Watchlist saved @ %s \n" % nPath) 
                except:
                    print("Action required: Binance - KeyLevels" + "\n---------------"
                    "\n        %s" % datetime.datetime.now().replace(microsecond=0)
                                    + " | Failed to export" + " watchlist.\n")
                break
            except:
                print('\nAction required: \n\n    On %s | Section 1.1.2' % 
                datetime.datetime.now().replace(microsecond=0) 
                + "\n    Failed to identify key levels on BINANCE.\n")
                seconds(30)
                counter_1bnc += 1
    else:
        print('\nStatus Updated: \n    On %s | Section 3' % 
                datetime.datetime.now().replace(microsecond=0) 
                + "\n    Analysis of lomg term data on Binance"
                + " returned an empty set. Moving on...")
        pass

# ANCHOR 1.3. OANDA
    print("*************" + "\n" + "*   OANDA   *" + "\n" + "*************")
    
    counter_1ond = 0 # oanda counter in 1st loop
    while counter_1ond < 5:
        try:
            print('\nStatus Update:'
                        + '\n-------------'
                        + '\n    On %s\n    Now requesting' % 
                            datetime.datetime.now().replace(microsecond=0)
                        + ' %s candlesticks from Oanda servers to ' 
                        % params_oanda['longterm']['granularity']
                        + 'indentify trending \n    instruments'
                        + ' experiencing a minor pull back...\n')

            stp1_ond = Signal().Step1_Oanda(list_of_instruments=list_of_instruments)
            stp1_ond = pd.DataFrame(stp1_ond['data'])
            
            print('\nStatus Update:'
                        + '\n-------------'
                        + '\n    On %s\n    Analysis of' % 
                            datetime.datetime.now().replace(microsecond=0)
                        + ' %s candlesticks on OANDA completed ' 
                        % params_oanda['longterm']['granularity']
                        + 'successfully.\n')
            break
        except:
            print('\nAction required: \n\n    On %s | Section 1.3' % 
            datetime.datetime.now().replace(microsecond=0) 
            + "\n    Failed to analyse longterm data on OANDA.\n")
            seconds(30)
            counter_1ond += 1

# ANCHOR Oanda - Identify resistance/supports
    if len(stp1_ond) != 0:
        counter_1ond = 0 # oanda counter in 1st loop
        while counter_1ond < 5:
            try:
                print('\nStatus Update:'
                            + '\n-------------'
                            + '\n    On %s\n    Now requesting' % 
                                datetime.datetime.now().replace(microsecond=0)
                            + ' %s candlesticks from OANDA servers to ' 
                            % params_oanda['itermediate']['granularity']
                            + 'indentify resistance/support \n    for '
                            + 'selected instruments...\n')

                stp2_ond = Signal().Step2_oanda(watchlist=stp1_ond, timeFrame='intermediate')
                stp2_ond = pd.DataFrame(stp2_ond['data'])

                print('\nStatus Update:'
                            + '\n-------------'
                            + '\n    On %s\n    Analysis of' % 
                                datetime.datetime.now().replace(microsecond=0)
                            + ' %s candlesticks on OANDA completed ' 
                            % params_oanda['itermediate']['granularity']
                            + 'successfully.\n')

                try:
                    _str = ('OANDA - Watchlist - %s.csv' %
                    datetime.datetime.strftime(datetime.datetime.now(), "%b-%d %H-%M-%S"))
                    nPath = os.path.join(path1, _str)
                    stp2_ond.to_csv(nPath) 

                    print("        %s" % datetime.datetime.now().replace(microsecond=0)
                                    + " \n        Watchlist saved @ %s \n" % nPath) 
                except:
                    print("Action required: OANDA - KeyLevels" + "\n---------------"
                    "\n        %s" % datetime.datetime.now().replace(microsecond=0)
                                    + " | Failed to export" + " watchlist.\n")
                break
            except:
                print('\nAction required: \n\n    On %s | Section 1.3' % 
                datetime.datetime.now().replace(microsecond=0) 
                + "\n    Failed to identify key levels on OANDA.\n")
                seconds(30)
                counter_1ond += 1
    else:
        print('\nStatus Updated: \n    On %s | Section 3' % 
                datetime.datetime.now().replace(microsecond=0) 
                + "\n    Analysis of long term data on Oanda"
                + " returned an empty set.")
        pass

# ANCHOR If no instrument was selected in previous step
    if len(stp1_ond) == 0 and len(stp1_bnc) == 0:
        print('\nStatus Updated: \n    On %s | Section 2' % 
        datetime.datetime.now().replace(microsecond=0) 
        + "\n    Analysis of longterm data on all markets"
        + " returned empty sets. \n\nNext requests will happen"
        + " @ 24:00:00 UTC\n")
                    
        # 24h: sleep the code till 24:00:00 - time utc
        actual_time_utc = datetime.datetime.now(datetime.timezone.utc)
        actual_time_utc_sec = UserDefinedFxns().time_to_sec(actual_time_utc)

        time_to_wake_up = datetime.time(hour=23, minute=59, second=59)
        time_to_wake_up_sec = UserDefinedFxns().time_to_sec(time_to_wake_up)

        time_to_sleep = time_to_wake_up_sec - actual_time_utc_sec

        seconds(time_to_sleep)
        print('Retrying to decide on trends accross all markets') 
        continue
    else:
        pass
# !SECTION 

# SECTION 2nd LOOP: Trade signal generation     
    while True:
        # Return to the begining of loop 1 if it is 12 o'clock a.m utc
        if (datetime.datetime.now(datetime.timezone.utc).hour == 0
        and datetime.datetime.now(datetime.timezone.utc).minute < 2):
            print("Retrying to decide on Long-Term Trends accorss"
            + "all Platforms...")
            print('Leaving 2nd LOOP loop')
            break            
        else:
            pass

        # run this section every 5 minutes
        if datetime.datetime.now().minute in range(0,60,5):
# ANCHOR 3.1. BINANCE
            if len(stp2_bnc) != 0:
                counter_3bnc = 0
                while counter_3bnc < 5:
                    try:
                        print('\nOn %s | Section 3.1 \nRequesting' % 
                            datetime.datetime.now().replace(microsecond=0)
                        + ' short-term data from BINANCE servers...\n')
                        
                        stp3_bnc = Signal().Step3_binance(watchlist=stp2_bnc)
                        stp3_bnc = pd.DataFrame(stp3_bnc['data'])

                        print('\nOn %s | Section 3.1 \nAnalysis of' % 
                            datetime.datetime.now().replace(microsecond=0)
                        + ' short-term data on BINANCE completed successfully!\n'
                        + "%s instruments selected for next step.\n" % 
                        len(binance_watchlst3['symbol']))
                        break
                    except:
                        print('\nAction required: \n\n    On %s | Section 3.1' % 
                        datetime.datetime.now().replace(microsecond=0) 
                        + "\n    Failed to analyse short-term data on BINANCE.\n")
                        seconds(30)
                        counter_3bnc += 1
                # reset the first counter before going to the next loop. This will insure 
                # the exception section to run smoothly 
            else:
                print('\nOn %s | Section 3.1 \nAnalysis' % 
                                datetime.datetime.now().replace(microsecond=0)
                            + " of 'intermediate' data on BINANCE yielded an empy set. Further "
                            + 'iterations on this exchange halted!\n    Moving on...\n')
                pass

# ANCHOR 3.3. OANDA
            if len(stp2_ond) != 0:
                counter_3ond = 0
                while counter_3ond < 5:
                    try:
                        # request short-term candlesticks if previous analysis yielded resutls
                        print('\nOn %s | Section 3.3 \nRequesting' % 
                            datetime.datetime.now().replace(microsecond=0)
                        + ' short-term data from OANDA servers...\n')
                        
                        stp3_ond = Signal().Step3_oanda(watchlist=stp2_ond)
                        stp3_ond = pd.DataFrame(stp3_ond['data'])

                        print('\nOn %s | Section 3.3 \nAnalysis of' % 
                            datetime.datetime.now().replace(microsecond=0)
                        + ' short-term data on OANDA completed successfully!\n'
                        + "%s instruments selected for next step.\n" % 
                        len(oanda_watchlst3['symbol']))
                        break
                    except:
                        print('\nAction required: \n\n    On %s | Section 3.3' % 
                        datetime.datetime.now().replace(microsecond=0) 
                        + "\n    Failed to analyse short-term data on OANDA.\n")
                        seconds(30)
                        counter_3ond += 1
                # reset the first counter before going to the next loop. This will insure 
                # the exception section to run smoothly 
                counter_3ond = 0
            else:
                print('\nOn %s | Section 3.3 \nAnalysis' % 
                                datetime.datetime.now().replace(microsecond=0)
                            + " of 'intermediate' data on OANDA yielded an empy set. Further "
                            + 'iterations on this exchange halted!\n    Moving on...\n')
                pass

# ANCHOR If no instrument was selected in previous step
            if len(stp2_ond) == 0 and len(stp2_bnc) == 0:
                print('\nStatus Updated: \n    On %s | Section 2' % 
                datetime.datetime.now().replace(microsecond=0) 
                + "\n    Analysis of intermediate data on all markets"
                + " returned empty sets. \n\nNext requests will happen"
                + " @ 24:00:00 UTC\n")
                            
                # 24h: sleep the code till 24:00:00 - time utc
                actual_time_utc = datetime.datetime.now(datetime.timezone.utc)
                actual_time_utc_sec = UserDefinedFxns().time_to_sec(actual_time_utc)

                time_to_wake_up = datetime.time(hour=23, minute=59, second=59)
                time_to_wake_up_sec = UserDefinedFxns().time_to_sec(time_to_wake_up)

                time_to_sleep = time_to_wake_up_sec - actual_time_utc_sec

                seconds(time_to_sleep)
                print('Retrying to decide on trends accross all markets') 
                break
            else:
                pass

        else:
            actual_time = datetime.datetime.now()

            _min,_sec = UserDefinedFxns().interval_counter(actual_time)
            time_to_sleep = _min*60 + _sec
            wake_up = actual_time + datetime.timedelta( seconds=time_to_sleep)
            print('\nStatus Updated: \n    On %s | Section 3' % 
            datetime.datetime.now().replace(microsecond=0) 
            + "\n    Scheduled shutdown. Normal operations to resume"
            + "  @ %s.\n" % wake_up.replace(microsecond=0))
            
            seconds(time_to_sleep)
            continue
# !SECTION 

# SECTION Notification section
        if stp3_bnc.equals(signalBinance):
            print("Binance: No change detected from previous iteration")
        else:
            print('\nStatus Updated: \n    On %s | Section 4.1' % 
                    datetime.datetime.now().replace(microsecond=0) 
                                    + "\n    BINANCE: Identified"
                                            + " Trade Signals\n")

            body = stp3_bnc.to_html()
            subject = "Binance: Trade Signals"
            signalBinance = stp3_bnc.copy()

            try:
                UserDefinedFxns().send_email(SUBJECT=subject, BODY=body)
            except:
                print('\n\nOn %s | Section 4.1 \n    Email' % 
                datetime.datetime.now().replace(microsecond=0)
                + ' Notification: Status Failed...\n')

        if stp3_ond.equals(signalOanda):
            print("Oanda: No change detected from previous iteration")
        else:
            print('\nStatus Updated: \n    On %s | Section 4.1' % 
                    datetime.datetime.now().replace(microsecond=0) 
                                    + "\n    BINANCE: Identified"
                                            + " Trade Signals\n")

            body = stp3_ond.to_html()
            subject = "Oanda: Trade Signals"
            signalOanda = stp3_ond.copy()

            try:
                UserDefinedFxns().send_email(SUBJECT=subject, BODY=body)
            except:
                print('\n\nOn %s | Section 4.1 \n    Email' % 
                datetime.datetime.now().replace(microsecond=0)
                + ' Notification: Status Failed...\n')
#!SECTION 
