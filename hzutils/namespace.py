import pandas as pd
from numpy import array

namespace = [
    ['TURN','换手率'],
    ['TURN_5MA','换手率(5MA)'],
    ['TURN_5MA_PCT_RANK','换手率历史分位(5MA)'],
    ['TURN_PCT_RANK','换手率分位'],
    ['PE_TTM','PE(整体法,TTM)'],
    ['PB_LF','PB(最新财报)'],
    ['PE_TTM_PCT_RANK','PE历史分位(TTM)'],
    ['PB_LF_PCT_RANK','PB历史分位(最新财报)'],
    ['ADJ_CLOSE','复权收盘价'],
    ['AMT','成交额'],
    ['VOLUME','成交量'],
    ['CLOSE','收盘价'],
    ['AMT','总成交额'],
    ['VOLUME','总成交量'],
    ['DIV','股息率'],
    ['DIV_PCT_RANK','股息率历史分位'],
    ['OBOS','超买超卖指标'],
    ['LONG_ORDER','多头排列指标'],
    ['SHORT_ORDER','空头排列指标'],
    ['STRUCTURED_FUND','成交额:分级B/分级A'],
    ['STRUCTURED_FUND_10MA','成交额:分级B/分级A(10MA)'],
    ['LIMIT_RM_NEW_ST_5MA','涨停个股数(剔除次新ST,5MA)'],
    ['TURN_RATIO_50_500','换手率:上证50/中证500(20MA)'],
    ['TURN_RATIO_1000_500','换手率:中证1000/中证500(20MA)'],
    ['SH_CONNECT','沪股通净买入笔数(万,5MA)'],
    ['TURN_PROP','换手率20%个股占比'],
    ['TURN_PROP_5MA','换手率20%个股占比(5MA)'],
    ['ANNUAL_TURN_20MA','年化换手率(20MA)'],
    ['ANNUAL_TURN_5MA','年化换手率(5MA)']
]
