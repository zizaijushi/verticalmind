import time,json,pymysql
import pandas as pd
import numpy as np
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
# from .models import basicinfo,basictree,indexinfo,marketinfo,obos,stockinfo
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.db import connections
from pymysql import connect,cursors
from datetime import datetime,timedelta,date
from xpinyin import Pinyin as pinyin
from hzutils import namespace
from scipy.optimize import minimize


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class indexMidToolsMixin:
    def minus_years(self,d, years):
        """Return a date that's `years` years after the date (or datetime)
        object `d`. Return the same calendar date (month and day) in the
        destination year, if it exists, otherwise use the following day
        (thus changing February 29 to March 1).

        """
        try:
            return d.replace(year=d.year - years)
        except ValueError:
            return d + (date(d.year - years, 1, 1) - date(d.year, 1, 1))

    def getAnomalyData(self,date=None, id=None):
        """

        :param date: Detecate date
        :return: Anomaly dataframe
        """
        cursor = connections['default'].cursor()
        if id is not None:
            sql = "SELECT * FROM (SELECT TB1.*, @R := @R +1 AS RANK FROM(SELECT A.*,B.CN_NAME,B.TABLE_NAME,B.ANOMALY FROM " \
                  "(SELECT TRADE_CODE,DT,COL_NAME FROM market_thresholdanomaly UNION " \
                  "SELECT TRADE_CODE,DT,COL_NAME FROM market_extremumanomaly ORDER BY DT,TRADE_CODE,COL_NAME) A " \
                  "LEFT JOIN market_anomalyref B ON A.TRADE_CODE=B.TRADE_CODE AND A.COL_NAME=B.COL_NAME) TB1,(SELECT @R:= 0) TB2) TB3 WHERE " \
                  "TB3.RANK = '{}'".format(id)
        else:
            if date is None:
                return None
            sql = "SELECT * FROM (SELECT TB1.*, @R := @R +1 AS RANK FROM(SELECT A.*,B.CN_NAME,B.TABLE_NAME,B.ANOMALY FROM " \
                  "(SELECT TRADE_CODE,DT,COL_NAME FROM market_thresholdanomaly UNION " \
                  "SELECT TRADE_CODE,DT,COL_NAME FROM market_extremumanomaly ORDER BY DT,TRADE_CODE,COL_NAME) A " \
                  "LEFT JOIN market_anomalyref B ON A.TRADE_CODE=B.TRADE_CODE AND A.COL_NAME=B.COL_NAME) TB1,(SELECT @R:= 0) TB2) TB3 WHERE " \
                  "TB3.DT = '{0}'".format(date)
        cursor.execute(sql)
        data = pd.DataFrame(dictfetchall(cursor))
        cursor.close()
        return data

    def pandas2jsonlist(self,table,dateCol = None,numCol = None, pctCol = None):
        """This function is trying to convert a normal timeserie to Highcharter friendly
        structure.

        :param table: A pandas Dataframe timeseries
        :param dateCol: Date colume name, convert to timestemp
        :param numCol:
        :param pctCol:
        :return:
        """
        if dateCol is not None:
            table[dateCol] = [time.mktime(x.timetuple()) * 1000 for x in table[dateCol]]
            # table[dataCol] = [x.strftime('%Y-%m-%d') for x in table[dataCol]]
        if numCol is not None:
            if type(numCol) is str:
                numCol = [numCol]
            for col in numCol:
                table[col] = [float(x) for x in table[col]]
        if pctCol is not None:
            if type(pctCol) is str:
                pctCol = [pctCol]
            for col in pctCol:
                table[col] = [float(x)*100 for x in table[col]]
        return table

    def anomalyminichart(self, row, curdate):
        """

        :param row:
        :param curdate:
        :return:
        """
        # Def variables
        tradecode = row['TRADE_CODE']
        tablename = row['TABLE_NAME']
        colname = row['COL_NAME']
        cnname = row['CN_NAME']
        anomaly = row['ANOMALY']

        # Get anomaly data from database
        cursor = connections['default'].cursor()
        begindate = self.minus_years(datetime.strptime(curdate, '%Y-%m-%d').date(), 1).strftime('%Y-%m-%d')
        cursor.execute(
            "SELECT DT,{0} AS VALUE FROM market_{1} WHERE TRADE_CODE = '{2}' AND {0} IS NOT NULL "
            "AND DT >= '{3}' AND DT <= '{4}'".format(colname, tablename, tradecode, begindate, curdate))
        anomalydata = pd.DataFrame(dictfetchall(cursor))
        # Check object asset type and get close price
        cursor.execute("SELECT TRADE_CODE,SEC_NAME,INFO_TABLE FROM market_basicinfo WHERE TRADE_CODE = '{0}' ".
                       format(tradecode))
        info = dictfetchall(cursor)
        secname = info[0]['SEC_NAME']
        closetable = info[0]['INFO_TABLE'].split('info')[0] + 'data'
        cursor.execute(
            "SELECT DT,CLOSE AS VALUE FROM market_{0} WHERE TRADE_CODE = '{1}' AND DT >= '{2}' AND DT <= '{3}'".
                format(closetable, tradecode, min(anomalydata.DT), curdate))
        closedata = pd.DataFrame(dictfetchall(cursor))
        anomalydata = self.pandas2jsonlist(anomalydata, numCol='VALUE', dateCol='DT')
        closedata = self.pandas2jsonlist(closedata, numCol='VALUE', dateCol='DT')
        # Options data
        # ...
        # Get plotlines in yaxis
        plotLines = []
        anomalytext = ""
        if (anomaly == 'threshold'):
            cursor.execute("SELECT UPPER,LOWER FROM market_anomalyref WHERE "
                           "TRADE_CODE = '{0}' AND COL_NAME = '{1}'".format(tradecode, colname))
            threshold = dictfetchall(cursor)
            upper = threshold[0]['UPPER']
            lower = threshold[0]['LOWER']
            lastvalue = str(round(anomalydata['VALUE'].values[-1], 1))
            if upper is not None:
                plotLines.append({'label': {'text': '上阈值'}, 'color': '#A52A2A', 'width': 2,
                                  'dashStyle': 'ShortDash', 'value': upper})
                anomalytext = '指标最新值为' + lastvalue + '，高于阈值' + str(round(upper, 1)) + '。'
            if lower is not None:
                plotLines.append({'label': {'text': '下阈值'}, 'color': '#A52A2A', 'width': 2,
                                  'dashStyle': 'ShortDash', 'value': lower})
                anomalytext = '指标最新值为' + lastvalue + '，低于阈值' + str(round(lower, 1)) + '。'
            anomaly = '阈值异动'

        # Get assettype
        cursor.execute("SELECT SEC_NAME FROM market_basicinfo a INNER JOIN "
                       "(SELECT PARENT_CODE,MAX(DEPTH)FROM market_classtree WHERE "
                       "CHILD_CODE = (SELECT PARENT_CODE FROM `market_classobject` WHERE "
                       "CHILD_CODE = '881001.WI')) b ON A.TRADE_CODE = B.PARENT_CODE")
        assettype = dictfetchall(cursor)[0]['SEC_NAME']
        cursor.close()
        # Build highchart options
        options = {}
        options['title'] = {'text': assettype + "|" + secname + "|" + cnname, 'align': 'left',
                            'style': {'color': '#333333'}}
        options['yAxis'] = [
            {'title': {'text': ''}, 'gridLineWidth': 0, 'labels': {'enable': 0}, 'plotLines': plotLines},
            {'title': {'text': ''}, 'gridLineWidth': 0, 'labels': {'enable': 0}, 'opposite': 1}]
        options['series'] = [{'type': 'line', 'name': cnname, 'data': anomalydata.values.tolist()},
                             {'type': 'line', 'name': secname, 'data': closedata.values.tolist(), 'yAxis': 1}]
        return [options, anomaly, anomalytext]

    def anomalychart(self, row, curdate):

        tradecode = row['TRADE_CODE']
        tablename = row['TABLE_NAME']
        colname = row['COL_NAME']
        cnname = row['CN_NAME']
        anomaly = row['ANOMALY']
        # Get anomaly data from database
        cursor = connections['default'].cursor()
        if anomaly is None or cnname is None or tablename is None:
            cursor.execute("SELECT ANOMALY,CN_NAME,TABLE_NAME FROM market_anomalyref WHERE TRADE_CODE = '{0}' "
                           "AND COL_NAME = '{1}'".format(tradecode,colname))
            parms = dictfetchall(cursor)
            anomaly = parms[0]['ANOMALY']
            cnname = parms[0]['CN_NAME']
            tablename = parms[0]['TABLE_NAME']

        cursor.execute(
            "SELECT DT,{0} AS VALUE FROM market_{1} WHERE TRADE_CODE = '{2}' AND {0} IS NOT NULL "
            "AND DT <= '{3}'".format(colname, tablename, tradecode, curdate))
        anomalydata = pd.DataFrame(dictfetchall(cursor))
        # Check object asset type and get close price
        cursor.execute("SELECT TRADE_CODE,SEC_NAME,INFO_TABLE FROM market_basicinfo WHERE TRADE_CODE = '{0}' ".
                       format(tradecode))
        info = dictfetchall(cursor)
        secname = info[0]['SEC_NAME']
        closetable = info[0]['INFO_TABLE'].split('info')[0] + 'data'
        cursor.execute(
            "SELECT DT,CLOSE AS VALUE FROM market_{0} WHERE TRADE_CODE = '{1}' AND DT >= '{2}' AND DT <= '{3}'".
                format(closetable, tradecode, min(anomalydata.DT), curdate))
        closedata = pd.DataFrame(dictfetchall(cursor))
        anomalydata = self.pandas2jsonlist(anomalydata, numCol='VALUE', dateCol='DT')
        closedata = self.pandas2jsonlist(closedata, numCol='VALUE', dateCol='DT')
        # Options data
        # ...
        # Get plotlines in yaxis
        plotLines = []
        anomalytext = ""
        if (anomaly == 'threshold'):
            cursor.execute("SELECT UPPER,LOWER FROM market_anomalyref WHERE "
                           "TRADE_CODE = '{0}' AND COL_NAME = '{1}'".format(tradecode, colname))
            threshold = dictfetchall(cursor)
            upper = threshold[0]['UPPER']
            lower = threshold[0]['LOWER']
            lastvalue = str(round(anomalydata['VALUE'].values[-1], 1))
            if upper is not None:
                plotLines.append({'label': {'text': '上阈值'}, 'color': '#A52A2A', 'width': 2,
                                  'dashStyle': 'ShortDash', 'value': upper})
                anomalytext = '指标最新值为' + lastvalue + '，高于阈值' + str(round(upper, 1)) + '。'
            if lower is not None:
                plotLines.append({'label': {'text': '下阈值'}, 'color': '#A52A2A', 'width': 2,
                                  'dashStyle': 'ShortDash', 'value': lower})
                anomalytext = '指标最新值为' + lastvalue + '，低于阈值' + str(round(lower, 1)) + '。'
            anomaly = '阈值异动'

        # Get assettype
        cursor.execute("SELECT SEC_NAME FROM market_basicinfo a INNER JOIN "
                       "(SELECT PARENT_CODE,MAX(DEPTH)FROM market_classtree WHERE "
                       "CHILD_CODE = (SELECT PARENT_CODE FROM `market_classobject` WHERE "
                       "CHILD_CODE = '881001.WI')) b ON A.TRADE_CODE = B.PARENT_CODE")
        assettype = dictfetchall(cursor)[0]['SEC_NAME']
        cursor.close()
        # Build highchart options
        options = {}
        options['title'] = {'text': assettype + "|" + secname + "|" + cnname, 'align': 'central',
                            'style': {'color': '#333333'}}
        options['yAxis'] = [
            {'title': {'text': cnname}, 'gridLineWidth': 1, 'labels': {'enable': 0}, 'plotLines': plotLines},
            {'title': {'text': '收盘价'}, 'gridLineWidth': 1, 'labels': {'enable': 0}, 'opposite': 0}]
        options['series'] = [{'type': 'line', 'name': cnname, 'data': anomalydata.values.tolist()},
                             {'type': 'line', 'name': secname, 'data': closedata.values.tolist(), 'yAxis': 1}]
        return [options, anomaly, anomalytext]

    def conditionCheck(self,input):
        key = list(input.keys())[0]
        if input is None or input == "":
            return ""
        else:
            return " AND "+list(input.keys())[0]+" IN ('"+"','".join(input[key])+"')"

    def getCards(self,options):

        options_keys = list(options.keys())
        anomalydata = []
        sig = []
        if('sig' in options_keys):
            sig = options['sig']
            anomalydata = self.getAnomalyData(sig)

        result = []
        if (len(anomalydata.index) == 0):
            result.append(['今天无异动信息', 1])
        else:
            for index, row in anomalydata.iterrows():
                row['RANK'] = str(int(row['RANK']))
                if index % 2 == 0:
                    result.append([self.anomalyminichart(row,sig), 0, 'left', row['RANK']])
                else:
                    result.append([self.anomalyminichart(row,sig), 0, 'right', row['RANK']])
        return result

class indexView(indexMidToolsMixin,View):
    """
    index page data loading.
    """
    # Read initial index page data
    def get(self, request, *args, **kwargs):
        # dateinput = request.GET.get('date')
        options = {'sig': datetime.today().strftime('%Y-%m-%d')}
        value = indexMidToolsMixin.getCards(options)
        return render(
            request, 'market/index.html',
            context={'result': value}
        )

    # Update index page data
    def put(self, request, *args, **kwargs):
        options = request.PUT.get('options')

        # if order == 'date':     # Add one day card at once.
        #     sig = (datetime.strptime(sig, '%Y-%m-%d').date() - timedelta(days=1)).strftime('%Y-%m-%d')
        #     carddata = indexMidToolsMixin.getCards(self, sig)
        # if order == 'rank':     # Add last 20 card at once.

        value = indexMidToolsMixin.getCards(options)
        return JsonResponse({'result': value})

    # Create a new card list by search
    def post(self, request, *args, **kwargs):
        options = request.POST.getlist('options')

        value = indexMidToolsMixin.getCards(options)

        return JsonResponse({'result': value})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class minifullswitchView(View):
    """
    Switch between mini and full chart in index page.
    """
    def get(self, request, *args, **kwargs):
        date = request.PUT.get('date')
        rankid = request.GET.get('rankid')
        charttype = request.GET.get('charttype')

        date = (datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=1)).strftime('%Y-%m-%d')
        row = indexMidToolsMixin.getAnomalyData(self, date, id=rankid).loc[0]
        chartdata = []

        if charttype == 'mini':
            chartdata = indexMidToolsMixin.anomalyminichart(self, row, date)
        if charttype == 'full':
            chartdata = indexMidToolsMixin.anomalychart(self, row, date)
        return JsonResponse({'chartdata': chartdata})


class keywordsView(indexMidToolsMixin,View):
    """
    Keyboard monitor function background.
    """
    def get(self, request, *args, **kwargs):
        infotable = request.GET.getlist('infotable[]')
        cursor = connections['default'].cursor()

        if infotable is None or infotable == []:
            keywords = pd.DataFrame(namespace)
        else:
            if type(infotable) is not list:
                infotable = [infotable]
            infotable = "','".join(infotable)

            sql = "SELECT TRADE_CODE,INFO_TABLE,SEC_NAME,PINYIN,PINYIN_INIT,TRADE_CODE AS SYMBOL FROM market_basicinfo WHERE INFO_TABLE IN ('{}')".format(
                infotable)
            cursor.execute(sql)
            keywords = pd.DataFrame(dictfetchall(cursor))
            temp = keywords[['TRADE_CODE', 'INFO_TABLE', 'SEC_NAME', 'SYMBOL']].rename(columns={'SYMBOL': 'VALUE'})
            colname = [x for x in list(keywords.columns.values) if
                       x not in ['TRADE_CODE', 'SYMBOL', 'INFO_TABLE', 'SEC_NAME']]
            for n in colname:
                temp = pd.concat(
                    [temp, keywords[['TRADE_CODE', 'INFO_TABLE', 'SEC_NAME', n]].rename(columns={n: 'VALUE'})], axis=0)
            keywords = temp.dropna()
        # get keyboard recodes
        cursor.execute("SELECT * FROM market_keyboardrecode")
        recode = pd.DataFrame(dictfetchall(cursor))
        cursor.close()

        keywords = keywords.to_json(orient='records')
        recode = recode.to_json(orient='records')
        return JsonResponse({'keywords':keywords,'recode':recode})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

######################################################FUND!##############################################

def Calc_log_Yield_Holding(lst):
    return (np.log(lst[-1]/lst[0]))


def Reg_GROWTH_VALUE_Sharpe_Constrained_rolling(ind, df):
    df = df.iloc[list(map(int, ind))].reset_index(drop=True)

    def residuals_Sharpe(b):
        return np.var(
            df['log_Yield_NAV_adj'] - np.sum(df[['log_Yield_GROWTH', 'log_Yield_VALUE']].values * b[None, :], axis=1))

    b0 = np.zeros(2)

    bounds = [(0, np.inf) for i in range(2)]
    constraint = ({'type': 'eq', 'fun': lambda b: np.sum(b) - 1})
    res = minimize(residuals_Sharpe, b0, method='SLSQP', bounds=bounds, constraints=constraint,
                   options={'ftol': 1e-25, 'disp': False})
    return res.x[0]

class getdataFundSampMixin():
    def get_fundinfo(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")

        basic_info_samp = pd.read_sql(
            "select `CODE`,`FUND_FULLNAME`,`FUND_SETUPDATE`,`FUND_INVESTTYPE` from Fund_STOCKS_Index where CODE = %(samp_code)s",
            conn_FUND, params={'samp_code': samp_code})
        return basic_info_samp.values.tolist()

    def get_fm_info(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")

        fm_info = pd.read_sql(
            "select `CODE`,`fund_fundmanager`,`fund_manager_startdate`,`servie_annulized_yield` from Fund_FM where CODE = %(samp_code)s",
            conn_FUND, params={'samp_code': samp_code})
        return fm_info.values.tolist()

    def get_fm_cv(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")

        fm_cv = pd.read_sql(
            "select `fund_manager_cv` from Fund_FM where CODE = %(samp_code)s",
            conn_FUND, params={'samp_code': samp_code})
        return fm_cv.values.tolist()

    def get_fund_scale_unit(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")

        fund_scale = pd.read_sql(
            "select `rptdate`,`fundnetasset(e4)` as `fundnetasset(e8)` from Fund_STOCKS_Details_Assets where CODE = %(samp_code)s",
            conn_FUND, params={'samp_code': samp_code})
        fund_scale['fundnetasset(e8)'] = fund_scale['fundnetasset(e8)']/1e+4
        fund_unittotal = pd.read_sql(
            "select `rptdate`,`unit_total` as `unit_total(e8)` from Fund_STOCKS_UnitTotal where CODE = %(samp_code)s",
            conn_FUND, params={'samp_code': samp_code})
        fund_unittotal['unit_total(e8)'] = fund_unittotal['unit_total(e8)']/1e+8

        fund_scale['rptdate'] = [time.mktime((datetime.strptime(x.strftime('%Y-%m-%d %H:%M:%S'),
                                                 '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).timetuple())*1000 for x in fund_scale['rptdate'].tolist()]
        fund_unittotal['rptdate'] = [time.mktime((datetime.strptime(x.strftime('%Y-%m-%d %H:%M:%S'),
                                                 '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).timetuple())*1000 for x in fund_unittotal['rptdate'].tolist()]
        fund_scale_unit = pd.merge_asof(fund_scale, fund_unittotal, on='rptdate').dropna()

        return {'fund_scale': [[x[0],x[1]] for x in fund_scale_unit.values.tolist()], 'fund_unittotal': [[x[0],x[2]] for x in fund_scale_unit.values.tolist()]}

    def get_fund_nav_mkt(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")
        conn_stock = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                     passwd='hzinsights2015', db='stock', charset="utf8")
        fund_nav = pd.read_sql(
            "select `rptdate`,`NAV_adj` from Fund_STOCKS_NavADJ where CODE = %(samp_code)s",
            conn_FUND, params={'samp_code': samp_code})

        fund_mkt = pd.read_sql(
            "select `DT` as `rptdate`,`CLOSE` from indexcloseprice where `TRADE_CODE` = '881001.WI'",
            conn_stock)

        # setupdate_samp = pd.read_sql(
        #     "select `FUND_SETUPDATE` from Fund_STOCKS_Index where CODE = %(samp_code)s",
        #     conn_FUND, params={'samp_code': samp_code}).values.item()

        fund_nav_mkt = pd.merge(fund_nav, fund_mkt, on='rptdate')
        fund_nav_mkt['rptdate'] = [time.mktime((datetime.strptime(x.strftime('%Y-%m-%d %H:%M:%S'),
                                                 '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).timetuple())*1000 for x in fund_nav_mkt['rptdate'].tolist()]
        fund_nav_mkt['CLOSE'] = fund_nav_mkt['NAV_adj']/fund_nav_mkt['CLOSE']
        return {'fund_nav': [[x[0],x[1]] for x in fund_nav_mkt.values.tolist()], 'fund_mkt': [[x[0],x[2]] for x in fund_nav_mkt.values.tolist()]}

    def get_fund_details_assets(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")
        tmp_assets_last = pd.read_sql(
            "select `stocktonav(%)`,`bondtonav(%)`,`fundtonav(%)`,`warranttonav(%)`,`cashtonav(%)`,`othertonav(%)` from Fund_STOCKS_Details_Assets where `rptdate` = (select max(`rptdate`) from Fund_STOCKS_Details_Assets) and CODE = '{}'".format(
                samp_code), conn_FUND)
        tmp_assets_last = tmp_assets_last.T
        tmp_assets_last['col'] = ['股票', '债券', '基金', '权证', '现金', '其他']
        tmp_assets_last.index = range(tmp_assets_last.shape[0])
        tmp_assets_last.columns = ['value', 'name']
        dic = tmp_assets_last.T.to_dict()
        res = []
        for value in dic.items():
            res.append(value[1])
        return res

    def get_fund_details_stocks(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")
        tmp_stocks_last = pd.read_sql(
            "select `stock_name`,`marketvalueofstockholdings(e4)` from Fund_Details_Stocks where `rptdate` = (select max(`rptdate`) from Fund_Details_Stocks) and CODE = '{}'".format(
                samp_code), conn_FUND)
        net_assets_last = pd.read_sql(
            "select `fundnetasset(e4)` from Fund_STOCKS_Details_Assets where `rptdate` = (select max(`rptdate`) from Fund_STOCKS_Details_Assets) and CODE = '{}'".format(
                samp_code), conn_FUND).values.item()
        tmp_stocks_last = tmp_stocks_last.sort_values('marketvalueofstockholdings(e4)', ascending=False).reset_index(drop=True)
        tmp_stocks_last = tmp_stocks_last.loc[0:9, ]
        tmp_stocks_last['marketvalueofstockholdings(e4)'] = tmp_stocks_last['marketvalueofstockholdings(e4)']/net_assets_last*100
        tmp_stocks_last.columns = ['name', 'value']
        dic = tmp_stocks_last.T.to_dict()
        res = []
        for value in dic.items():
            res.append(value[1])
        return res

    def get_fund_MDD(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")
        fund_MDD = pd.read_sql(
            "select `rptdate`,`CODE`,`最大回撤率(%)` from `Fund_STOCKS_NavADJ_MDD` where `FUND_INVESTTYPE` = (select `FUND_INVESTTYPE` from `Fund_STOCKS_NavADJ_MDD` where CODE = '{}' LIMIT 1)".format(
                samp_code), conn_FUND)

        fund_MDD_mean = fund_MDD.groupby(['rptdate'])['最大回撤率(%)'].mean().reset_index()
        fund_MDD_samp = fund_MDD.loc[fund_MDD['CODE'] == samp_code, ['rptdate','最大回撤率(%)']].reset_index(drop=True)
        fund_MDD_samp = pd.merge(fund_MDD_samp, fund_MDD_mean, on='rptdate')
        fund_MDD_samp['rptdate'] = [time.mktime((datetime.strptime(x.strftime('%Y-%m-%d %H:%M:%S'),
                                                 '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).timetuple())*1000 for x in fund_MDD_samp['rptdate'].tolist()]

        return {'fund_MDD_samp': [[x[0],x[1]] for x in fund_MDD_samp.values.tolist()], 'fund_MDD_mean': [[x[0],x[2]] for x in fund_MDD_samp.values.tolist()]}

    def get_fund_dist_log_yield(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")
        conn_stock = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                     passwd='hzinsights2015', db='stock', charset="utf8")
        Holding_Period = 252

        fund_nav = pd.read_sql(
            "select `rptdate`,`NAV_adj` from Fund_STOCKS_NavADJ where CODE = %(samp_code)s",
            conn_FUND, params={'samp_code': samp_code})

        fund_mkt = pd.read_sql(
            "select `DT` as `rptdate`,`CLOSE` from indexcloseprice where `TRADE_CODE` = '881001.WI'",
            conn_stock)
        fund_nav = pd.merge(fund_nav, fund_mkt, on='rptdate')
        fund_nav['Yield_Holding_rolling'] = fund_nav['NAV_adj'].rolling(window=Holding_Period).apply(Calc_log_Yield_Holding).reset_index()['NAV_adj']
        fund_nav['Yield_Holding_rolling_mkt'] = fund_nav['CLOSE'].rolling(window=Holding_Period).apply(Calc_log_Yield_Holding).reset_index()['CLOSE']
        fund_nav = fund_nav[['rptdate','Yield_Holding_rolling','Yield_Holding_rolling_mkt']].dropna().reset_index(drop=True)
        return {'log_yield_fund': [x[1] for x in fund_nav.values.tolist()], 'log_yield_mkt': [x[2] for x in fund_nav.values.tolist()]}

    def get_fund_a_b(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")
        fund_a_b = pd.read_sql(
            "select `rptdate`,`Alpha_rolling`,`Beta_rolling` from `Fund_STOCKS_NavADJ_a_b` where CODE = '{}'".format(
                samp_code), conn_FUND)

        fund_a_b['rptdate'] = [time.mktime((datetime.strptime(x.strftime('%Y-%m-%d %H:%M:%S'),
                                                 '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).timetuple())*1000 for x in fund_a_b['rptdate'].tolist()]
        return {'fund_a': [[x[0],x[1]] for x in fund_a_b.values.tolist()], 'fund_b': [[x[0],x[2]] for x in fund_a_b.values.tolist()]}

    def fund_reg(self,samp_code):
        conn_FUND = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                    passwd='hzinsights2015', db='FUND', charset="utf8")
        conn_stock = pymysql.connect(host='58eaf271802cb.sh.cdb.myqcloud.com', port=4104, user='root',
                                     passwd='hzinsights2015', db='stock', charset="utf8")
        fund_nav = pd.read_sql("select `rptdate`,`NAV_adj` from Fund_STOCKS_NavADJ where CODE = %(samp_code)s",
                               conn_FUND, params={'samp_code': samp_code})

        MKT = pd.read_sql(
            "select `DT` as `rptdate`,`CLOSE` as 'MKT' from indexcloseprice where `TRADE_CODE` = '881001.WI'",
            conn_stock)
        IndexClosePrice = pd.read_sql(
            "SELECT `DT` as `rptdate`,`TRADE_CODE`,`CLOSE` from indexcloseprice where TRADE_CODE in ('GROWTH','VALUE')",
            conn_stock)
        GROWTH = IndexClosePrice.loc[IndexClosePrice['TRADE_CODE'] == 'GROWTH', ['rptdate', 'CLOSE']].reset_index(drop=True)
        GROWTH.columns = ['rptdate', 'GROWTH']
        VALUE = IndexClosePrice.loc[IndexClosePrice['TRADE_CODE'] == 'VALUE', ['rptdate', 'CLOSE']].reset_index(drop=True)
        VALUE.columns = ['rptdate', 'VALUE']

        fund_nav = pd.merge(fund_nav, MKT, how='left', on='rptdate')
        fund_nav = pd.merge(fund_nav, GROWTH, how='left', on='rptdate')
        fund_nav = pd.merge(fund_nav, VALUE, how='left', on='rptdate')
        fund_nav = fund_nav.sort_values('rptdate').reset_index(drop=True)

        fund_nav['Year'] = [x.isocalendar()[0] for x in fund_nav['rptdate']]
        fund_nav['WeekNumber'] = [x.isocalendar()[1] for x in fund_nav['rptdate']]

        fund_nav['log_Yield_NAV_adj'] = np.log(fund_nav['NAV_adj'].shift(0) / fund_nav['NAV_adj'].shift(1))
        fund_nav['log_Yield_MKT'] = np.log(fund_nav['MKT'] / (fund_nav['MKT'].shift()[1:]))
        fund_nav['log_Yield_GROWTH'] = np.log(fund_nav['GROWTH'] / (fund_nav['GROWTH'].shift()[1:]))
        fund_nav['log_Yield_VALUE'] = np.log(fund_nav['VALUE'] / (fund_nav['VALUE'].shift()[1:]))
        fund_nav = fund_nav.groupby(['Year', 'WeekNumber'])['log_Yield_NAV_adj', 'log_Yield_MKT', 'log_Yield_GROWTH', 'log_Yield_VALUE'].sum().reset_index()
        fund_nav[['log_Yield_NAV_adj', 'log_Yield_GROWTH', 'log_Yield_VALUE']] = fund_nav[['log_Yield_NAV_adj', 'log_Yield_GROWTH','log_Yield_VALUE']].values - fund_nav['log_Yield_MKT'][:, None]
        fund_nav = fund_nav[['Year', 'WeekNumber', 'log_Yield_NAV_adj', 'log_Yield_GROWTH', 'log_Yield_VALUE']]
        fund_nav['ind'] = range(len(fund_nav))

        win = 12
        Reg_GROWTH_VALUE_Sharpe_Constrained = fund_nav['ind'].rolling(window=win, center=False).apply(lambda x: Reg_GROWTH_VALUE_Sharpe_Constrained_rolling(x, fund_nav)).reset_index()
        Reg_GROWTH_VALUE_Sharpe_Constrained = Reg_GROWTH_VALUE_Sharpe_Constrained.rename(columns={'ind': 'Coef_GROWTH'})
        Reg_GROWTH_VALUE_Sharpe_Constrained = pd.concat([fund_nav.loc[:, fund_nav.columns != 'ind'], Reg_GROWTH_VALUE_Sharpe_Constrained['Coef_GROWTH']],axis=1).dropna().reset_index(drop=True)
        Reg_GROWTH_VALUE_Sharpe_Constrained['Coef_VALUE'] = 1 - Reg_GROWTH_VALUE_Sharpe_Constrained['Coef_GROWTH']
        Reg_GROWTH_VALUE_Sharpe_Constrained['rptdate'] = [datetime.strptime(str(x[0]) + str(x[1]) + '5', "%Y%W%w") for x in Reg_GROWTH_VALUE_Sharpe_Constrained[['Year', 'WeekNumber']].values]
        Reg_GROWTH_VALUE_Sharpe_Constrained['rptdate'] = [time.mktime((datetime.strptime(x.strftime('%Y-%m-%d %H:%M:%S'),
                                                 '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).timetuple())*1000 for x in Reg_GROWTH_VALUE_Sharpe_Constrained['rptdate'].tolist()]
        return {'fund_GROWTH': [[x[-1],x[-3]] for x in Reg_GROWTH_VALUE_Sharpe_Constrained.values.tolist()], 'fund_VALUE': [[x[-1],x[-2]] for x in Reg_GROWTH_VALUE_Sharpe_Constrained.values.tolist()]}

class fund(getdataFundSampMixin,View):
    template_name = "market/fund.html"

    def get(self,request, *args, **kwargs):
        return render(request,'market/fund.html',context={'data':1})
    def post(self, request, *args, **kwargs):
        # samp_code = self.kwargs['fundcode']
        samp_code = request.POST.get('fcode')

        # samp_code = request.GET.get('fcode')
        basic_info_samp = getdataFundSampMixin.get_fundinfo(self,samp_code)
        fm_info_samp = getdataFundSampMixin.get_fm_info(self,samp_code)
        fm_cv_samp = getdataFundSampMixin.get_fm_cv(self,samp_code)
        scale_unit_samp = getdataFundSampMixin.get_fund_scale_unit(self,samp_code)
        nav_mkt_samp = getdataFundSampMixin.get_fund_nav_mkt(self,samp_code)
        lastest_details_assets_samp = getdataFundSampMixin.get_fund_details_assets(self,samp_code)
        lastest_details_stocks_samp = getdataFundSampMixin.get_fund_details_stocks(self,samp_code)
        MDD_samp = getdataFundSampMixin.get_fund_MDD(self,samp_code)
        dist_log_yield_samp = getdataFundSampMixin.get_fund_dist_log_yield(self,samp_code)
        a_b_samp = getdataFundSampMixin.get_fund_a_b(self,samp_code)
        style_samp = getdataFundSampMixin.fund_reg(self,samp_code)
        return JsonResponse({'basic_info_samp': basic_info_samp,
                             'fm_info_samp': fm_info_samp,
                             'fm_cv_samp': fm_cv_samp,
                             'scale_unit_samp': scale_unit_samp,
                             'nav_mkt_samp': nav_mkt_samp,
                             'lastest_details_assets_samp': lastest_details_assets_samp,
                             'lastest_details_stocks_samp': lastest_details_stocks_samp,
                             'MDD_samp': MDD_samp,
                             'dist_log_yield_samp': dist_log_yield_samp,
                             'a_b_samp': a_b_samp,
                             'style_samp': style_samp})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)