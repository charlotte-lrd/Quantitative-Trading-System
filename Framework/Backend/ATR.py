#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import math
import csv
import scipy
import datetime


# In[ ]:


def ATR(data,N=20,k=10,initial_cash = 400000):
    #数据处理：获得日收盘价
    tmp = get_data(ts_code,start_time,end_time,'D')
    dic = dict(zip(tmp['trade_date'].apply(lambda x:x.date()),tmp['pre_close']))
    data['pre_close'] = data['trade_time'].apply(lambda x:dic[x.date()])
    #删除含na的列
    data = data.dropna(axis=1).reset_index(drop=True)
    #计算TR-index
    for i in range(len(data)):
        data.loc[i,'TR']=max(data.iloc[i]['high']-data.iloc[i]['low'],abs(data.iloc[i]['high']-data.iloc[i]['pre_close']),abs(data.iloc[i]['pre_close']-data.iloc[i]['low']))
    #计算UP DOWN ATR ;新建Unit
    data['Up'] = data['high'].rolling(k).max()
    data['Down'] = data['low'].rolling(k).min()
    data['ATR'] = data['TR'].rolling(N).mean()
    data['Up']=data['Up'].shift(axis=0,periods=1)
    data['Down'] = data['Down'].shift(1)
    data['Unit'] = 0
    data = data.dropna(axis=0).reset_index(drop=True)
    #删除缺失值
    data = data.dropna(axis=0).reset_index(drop=True)
    #计算Unit
    prev_price = data['close'][0]
    for i in range(len(data)):
        if i==0:
            if data['close'][i] > data['Up'][i]:
                prev_price = data['close'][i]
                data.loc[i,'Unit'] += 1
            else:
                if data['close'][i] < data['close'][i]:
                    prev_price = data['close'][i]
                    data.loc[i,'Unit'] -= 1
        else:
            if data['Unit'][i-1] == 0:
                if data['close'][i] > data['Up'][i]:
                    prev_price = data['close'][i]
                    data.loc[i,'Unit'] = data['Unit'][i-1]+1
                else:
                    if data['close'][i] < data['Down'][i]:
                        prev_price = data['close'][i]
                        data.loc[i,'Unit'] = data['Unit'][i-1] - 1

            if data['Unit'][i-1] > 0:
                if data['close'][i] > prev_price + 0.5*data['ATR'][i]:
                    data.loc[i,'Unit'] = data['Unit'][i-1] + 1
                    prev_price = data['close'][i]
                else:
                    if data['close'][i] < prev_price - 2*data['ATR'][i]:
                        data.loc[i,'Unit'] = 0
                    else:
                        if data['close'][i] < data['Down'][i]:
                            data.loc[i,'Unit'] = 0
            if data['Unit'][i-1] < 0:
                if data['close'][i] < prev_price - 0.5*data['ATR'][i]:
                    data.loc[i,'Unit'] = data['Unit'][i-1] - 1
                    prev_price = data['close'][i]
                else:
                    if data['close'][i] > prev_price + 2*data['ATR'][i]:
                        data.loc[i,'Unit'] = 0
                    else:
                        if data['close'][i] > data['Up'][i]:
                            data.loc[i,'Unit'] = 0
    #计算value
    data['value'] = data['Unit']*data['close']
    data['value'] = data['value'].cumsum()+initial_cash
    #返回结果
    tmp1 = data[['trade_time','Unit','value']]
    tmp1 = tmp1.rename(columns = dict(zip(['trade_time','Unit','value'],['trade_time','total_lot','total_cash'])))
    return tmp1

