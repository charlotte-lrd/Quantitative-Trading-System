
import pandas as pd
import time
import datetime
import math



def Fairy(data,initial_cash,max_lot):
#初始化当前天数、总资产、活动金额、手数(做空为负，做多为正）
    total_cash = initial_cash
    total_lot = 0
    cash_account = initial_cash
    #n1:data;n2:result
    n1 = 0
    n2 = 0
    df_result = pd.DataFrame(columns = ['date','high','low','close','deal','cash_account','total_lot','total_cash'])
    if n2 == 0:
        high = data[(data['trade_time']<data['trade_time'][n1]+datetime.timedelta(days= 1))&(data['trade_time']>=data['trade_time'][n1])]['high'].max()
        low = data[(data['trade_time']<data['trade_time'][n1]+datetime.timedelta(days= 1))&(data['trade_time']>=data['trade_time'][n1])]['low'].min()
        close = data[(data['trade_time']<data['trade_time'][n1]+datetime.timedelta(days= 1))&(data['trade_time']>=data['trade_time'][n1])].iloc[-1]['close']
        df_result.loc[n2] = [datetime.datetime.strftime(data.index[n1],"%Y-%m-%d"),high,low,close,0,cash_account,total_lot,total_cash]
        n1 = len(data[data['trade_time']<data['trade_time'][n1]+datetime.timedelta(days= 1)])
        n2 = n2 + 1
    if n2 != 0:
        while n1 < len(data):
            deal = 0
            high = df_result.iloc[n2-1]['high']
            low = df_result.iloc[n2-1]['low']
            close = df_result.iloc[n2-1]['close']
            #position:多仓1，空仓0
            #价格突破上轨:是1否0
            setupbuy_index = 0
            #价格跌破下轨：是1否0
            setupsell_index = 0
            #日内数据
            data_deal = data[(data.index < data.index[n1]+datetime.timedelta(days= 1))&(data.index >= data.index[n1])]
            #获得日内最高价、最低价、开盘价、收盘价
            high = data_deal['high'].max()
            low = data_deal['low'].min()
            opening = data_deal.iloc[1]['open']
            close = data_deal.iloc[-1]['close']
            #获得上轨（昨日最高价）、下轨（昨日最低价）
            ydata_deal = data[(data.index < data.index[n1])&(data.index >= data.index[n1]+datetime.timedelta(days= -1))]
            top_rail = ydata_deal['high'].max()
            bottom_rail = ydata_deal['low'].min()
            for i in range(0,len(data_deal)):
                if data_deal.iloc[i]['high'] > top_rail:
                    setupbuy_index = 1
                if data_deal.iloc[i]['high'] < bottom_rail:
                    setupsell_index = 1
                total_cash = cash_account + total_lot * data_deal.iloc[i]['high']
                #平仓策略:
                if (high > top_rail and data_deal.iloc[i]['high'] <= opening )or(low < bottom_rail and data_deal.iloc[i]['high'] >= opening):
                    deal += abs(total_lot)
                    cash_account = cash_account + total_lot * data_deal.iloc[i]['high']
                    total_lot = 0
                #开仓策略                
                else:
                    #突破上轨做多
                    if data_deal.iloc[i]['high'] > top_rail:
                        total_lot += max_lot
                        deal += max_lot
                        cash_account -= max_lot * (data_deal.iloc[i]['high'])
                        position = 1
                    #跌破下轨做空
                    if data_deal.iloc[i]['high'] < bottom_rail:
                        total_lot -= max_lot
                        deal += max_lot
                        cash_account += max_lot * (data_deal.iloc[i]['high'])
                        position = 0
            df_result.loc[n2] = [datetime.datetime.strftime(data.index[n1],"%Y-%m-%d"),high,low,close,deal,cash_account,total_lot,total_cash]  
            n2 += 1
            n1 = n1 + len(data_deal)
        return df_result[['date','total_lot','total_cash']]


