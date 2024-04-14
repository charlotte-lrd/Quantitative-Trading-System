import pandas as pd
import numpy as np
import datetime
def R_breaker(data,loss_price=30,initial_cash=50000,service_charge=15,max_lot=2):
    #loss_price:止损比例
    #initial_cash:投入
    #service_charge:手续费/手
    #deposit_rate:保证金比率/手
    #max_lot:最大交易手数
    #初始化总资产、活动金额、保证金金额、手数(做空为负，做多为正）、当前天数、结果表
    total_cash = initial_cash
    cash_account = initial_cash
    deposit_cash = 0
    total_lot = 0
    #n1:data;n2:result
    n1 = 0
    n2 = 0
    df_result = pd.DataFrame(columns = ['date','high','low','close','deal','cash_account','total_lot','total_cash'])
    if n2==0:
        high = data[data['trade_time']< data['trade_time'][n1]+datetime.timedelta(days= 1)]['high'].max()
        low =  data[data['trade_time']< data['trade_time'][n1]+datetime.timedelta(days= 1)]['low'].min()
        close = data[data['trade_time']<data['trade_time'][n1]+datetime.timedelta(days= 1)].iloc[-1]['close']
        df_result.loc[n2] = [datetime.datetime.strftime(data['trade_time'][n1],"%Y-%m-%d"),high,low,close,0,cash_account,total_lot,total_cash]
        n1 = len(data[data['trade_time']<data['trade_time'][n1]+datetime.timedelta(days= 1)])
        n2 = n2 + 1
    if n2 != 0:
        while n1<len(data):
            deal = 0
            high = df_result.iloc[n2-1]['high']
            low = df_result.iloc[n2-1]['low']
            close = df_result.iloc[n2-1]['close']
            pivot = (high + low + close) / 3  # 枢轴点
            breakbuy = high + 2 * (pivot - low) # 突破买入价
            setupsell = pivot + (high - low) # 观察卖出价
            revsell = 2 * pivot - low# 反转卖出价
            revbuy =  2 * pivot - high # 反转买入价
            setupbuy = pivot - (high - low), # 观察买入价
            breaksell = low - 2 * (high - pivot)  # 突破卖出价
            #position:多仓：1，空仓：0
            #超过观察卖出价:是1否0
            setupsell_index = 0
            #跌破观察买入价：是1否0
            setupbuy_index = 0
            #日内数据
            data_deal = data[(data['trade_time']<data['trade_time'][n1]+datetime.timedelta(days= 1))&(data['trade_time']>=data['trade_time'][n1])]
            #获得日内最高价、最低价、收盘价
            high = data_deal['high'].max()
            low = data_deal['low'].min()
            close = data_deal.iloc[-1]['close']
            for i in range(0,len(data_deal)):
                #检查是否超过观察卖出价或者跌破观察买入价
                if data_deal.iloc[i]['high'] > setupsell:
                    setupsell_index = 1
                if data_deal.iloc[i]['high'] < setupbuy:
                    setupbuy_index = 1
                #检查止损
                #当前总资产
                total_cash = cash_account + total_lot*data_deal.iloc[i]['high']
                loss = (initial_cash - total_cash)/initial_cash*100
                #超过止损点,平仓
                if loss > loss_price:
                    cash_account = cash_account + total_lot * data_deal.iloc[i]['high'] - abs(total_lot)*service_charge
                    deal += abs(total_lot)
                    total_lot = 0
                 #未超过止损点
                else:
                    #空仓时
                    if total_lot == 0:
                        #价格超过突破买入价
                        if data_deal.iloc[i]['high']>breakbuy:
                            #做多
                            total_lot += max_lot
                            deal += max_lot
                            cash_account -= max_lot * (data_deal.iloc[i]['high'] + service_charge)
                            position = 1
                        #价格低过突破卖出价
                        if (data_deal.iloc[i]['high']<breaksell):
                            #做空
                            total_lot -= max_lot
                            deal += max_lot
                            cash_account += max_lot * (data_deal.iloc[i]['high'] - service_charge)
                            position = 0 
                    #持仓时
                    else:
                        #如果做多仓
                        if position:
                            #如果日内价格已超过观察卖出价
                            if setupsell_index:
                                #如果跌破反转卖出价,则先平仓再做空
                                if data_deal.iloc[i]['high'] < revsell:
                                    #平仓
                                    cash_account += total_lot*(data_deal.iloc[i]['high']-service_charge)
                                    deal += abs(total_lot)
                                    total_lot = 0
                                    #做空
                                    position = 0
                                    total_lot -= max_lot
                                    deal += abs(total_lot)
                                    cash_account += max_lot * (data_deal.iloc[i]['high'] - service_charge)
                        #如果做空仓
                        else:
                            #如果日内最低价已跌破观察买入价
                            if setupbuy_index:
                            #如果突破反转买入价，先平仓再做多
                                if data_deal.iloc[i]['high'] > revbuy:
                                    #平仓
                                    cash_account -= abs(total_lot)*(data_deal.iloc[i]['high']+service_charge)
                                    deal += abs(total_lot)
                                    total_lot = 0
                                    #做多
                                    position = 1
                                    total_lot += max_lot
                                    deal += max_lot
                                    cash_account -= max_lot * (data_deal.iloc[i]['high']+service_charge)
            total_cash = cash_account + total_lot*close   
            df_result.loc[n2] = [datetime.datetime.strftime(data['trade_time'][n1],"%Y-%m-%d"),high,low,close,deal,cash_account,total_lot,total_cash]  
            n2 += 1
            n1 = n1 + len(data_deal)
        return df_result[['date','total_lot','total_cash']]



