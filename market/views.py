from django.shortcuts import render,render_to_response
from django.http import HttpResponse,JsonResponse
# from .models import basicinfo,basictree,indexinfo,marketinfo,obos,stockinfo
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.base import View
import time,json
import pandas as pd
from django.db import connections
from pymysql import connect,cursors
from datetime import datetime,timedelta,date
from xpinyin import Pinyin as pinyin

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
                  "SELECT TRADE_CODE,DT,COL_NAME FROM market_extremumanomaly ORDER BY DT,TRADE_CODE,COL_NAME) A "\
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

    def indexGetCards(self,curdate):
        anomalydata = self.getAnomalyData(curdate)

        carddata = []
        if (len(anomalydata.index) == 0):
            carddata.append(['今天无异动信息', 1])
        else:
            for index, row in anomalydata.iterrows():
                row['RANK'] = str(int(row['RANK']))
                if index % 2 == 0:
                    carddata.append([self.anomalyminichart(row,curdate), 0, 'left', row['RANK']])
                else:
                    carddata.append([self.anomalyminichart(row,curdate), 0, 'right', row['RANK']])
        return carddata

class indexView(indexMidToolsMixin,View):
    def get(self, request, *args, **kwargs):
        # Get last date in the page
        lastdate = request.GET.get('lastdate')
        if lastdate is None or lastdate == '':
            # Initial page required data
            curdate = datetime.today().strftime('%Y-%m-%d')
            # curdate = '2018-05-29'
            # Get data
            carddata = indexMidToolsMixin.indexGetCards(self, curdate)
            return render(
                request, 'market/index.html',
                context={'carddata': carddata, 'curdate': curdate}
            )
        else:
            # Interactive data
            curdate = (datetime.strptime(lastdate,'%Y-%m-%d').date() - timedelta(days=1)).strftime('%Y-%m-%d')
            charttype = request.GET.get('charttype')
            # Add card or show large chart
            if charttype is None or charttype == '':
                search = request.GET.get('search')
                if search is None or search == '':
                    # Get data
                    carddata = indexMidToolsMixin.indexGetCards(self, curdate)
                    return JsonResponse({'carddata': carddata, 'curdate': curdate})
                else:
                    return JsonResponse({'data':1})
            else:
                rankid = request.GET.get('rankid')
                row = indexMidToolsMixin.getAnomalyData(self,curdate,id = rankid).loc[0]
                chartdata = []
                if charttype == '0':
                    chartdata = indexMidToolsMixin.anomalyminichart(self, row, curdate)
                elif charttype == '1':
                    chartdata = indexMidToolsMixin.anomalychart(self, row, curdate)
                return JsonResponse({'chartdata':chartdata})

    def post(self, request, *args, **kwargs):
        return JsonResponse({"data":1})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class keywordsView(indexMidToolsMixin,View):
    def post(self, request, *args, **kwargs):
        cursor = connections['default'].cursor()
        infotable = request.POST.getlist('infotable[]')
        if type(infotable) is not list:
            infotable = [infotable]
        infotable = "','".join(infotable)
        if infotable is None:
            sql = "SELECT TRADE_CODE,SEC_NAME,PINYIN,PINYIN_INIT,TRADE_CODE AS SYMBOL FROM market_basicinfo"
        else:
            sql = "SELECT TRADE_CODE,SEC_NAME,PINYIN,PINYIN_INIT,TRADE_CODE AS SYMBOL FROM market_basicinfo WHERE INFO_TABLE IN ('{}')".format(infotable)
        cursor.execute(sql)
        keywords = pd.DataFrame(dictfetchall(cursor))
        temp = keywords[['TRADE_CODE','SYMBOL']].rename(columns = {'SYMBOL':'VALUE'})
        colname = [x for x in list(keywords.columns.values) if x not in ['TRADE_CODE','SYMBOL']]
        for n in colname:
            temp = pd.concat([temp,keywords[['TRADE_CODE',n]].rename(columns = {n:'VALUE'})],axis=0)
        keywords = temp.values.tolist()
        cursor.close()
        return JsonResponse({'keywords':keywords})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class cleandataMixin:
    def pandas2jsonlist(self,table,dataCol = None,numCol = None, pctCol = None):
        if dataCol is not None:
            table[dataCol] = [time.mktime(x.timetuple()) * 1000 for x in table[dataCol]]
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

class getdataMixin(cleandataMixin):
    def get_obosinfo(self):
        cursor = connections['default'].cursor()
        cursor.execute(
            "SELECT DISTINCT C.TRADE_CODE,C.SEC_NAME FROM (SELECT A.TRADE_CODE,B.SEC_NAME FROM market_obos A LEFT JOIN market_indexinfo B ON A.TRADE_CODE = B.TRADE_CODE) C")
        obos_code = dictfetchall(cursor)
        cursor.close()
        return {'obos_code':obos_code}

    def get_pricedata(self,trade_code,cols = ['OPEN','CLOSE','LOW','HIGH'], remove_suspended = True, begindate = None, enddate = None):
        cursor = connections['default'].cursor()
        if type(cols) is str:
            cols = [cols]
        cols = list(set(cols) & set(['OPEN','CLOSE','LOW','HIGH']))
        if begindate is None:
            begindate = '1990-01-01'
        if enddate is None:
            enddate = datetime.now().strftime('%Y-%m-%d')
        if remove_suspended:
            sql = "SELECT DT,{0} FROM market_marketinfo WHERE TRADE_CODE = '{1}' AND AMT > 0 AND DT >= '{2}' AND DT <= '{3}'".format(
                ','.join(['{0}*FACTOR AS {0}'.format(x) for x in cols]),trade_code,begindate,enddate)
        else:
            sql = "SELECT DT,{0} FROM market_marketinfo WHERE TRADE_CODE = '{1}' AND DT >= '{2}' AND DT <= '{3}'".format(
                ','.join(['{0}*FACTOR AS {0}'.format(x) for x in cols]),trade_code,begindate,enddate)
        cursor.execute(sql)
        close_data = pd.DataFrame(dictfetchall(cursor))

        if bool(set(cols) & set(['CLOSE'])):
            close_data['CLOSE'] = close_data['CLOSE'].fillna(method='ffill')
            close_data.dropna(subset=['CLOSE'])
        if bool(set(cols) & set(['OPEN','HIGH','LOW'])):
            close_data[list(set(cols) & set(['OPEN','HIGH','LOW']))] = \
                close_data[list(set(cols) & set(['OPEN','HIGH','LOW']))].\
                    apply(lambda x: x.fillna(value=close_data['CLOSE']),0)
        close_data = cleandataMixin.pandas2jsonlist(self, close_data,numCol=cols,dataCol='DT')
        close_data = close_data[['DT']+cols]
        close_data_json = close_data.values.tolist()
        cursor.close()
        return {'name':'后复权价格','data':close_data_json}

    def get_volumedata(self,trade_code,cols = ['VOLUME','AMT'], remove_suspended = True,begindate = None,enddate = None):
        cursor = connections['default'].cursor()
        if type(cols) is str:
            cols = [cols]
        cols = list(set(cols) & set(['VOLUME','AMT']))
        if begindate is None:
            begindate = '1990-01-01'
        if enddate is None:
            enddate = datetime.now().strftime('%Y-%m-%d')
        if remove_suspended:
            sql = "SELECT DT,{0} FROM market_marketinfo WHERE TRADE_CODE = '{1}' AND AMT > 0 AND DT >= '{2}' AND DT <= '{3}'".format(
                ','.join(cols),trade_code,begindate,enddate)
        else:
            sql = "SELECT DT,{0} FROM market_marketinfo WHERE TRADE_CODE = '{1}' AND DT >= '{2}' AND DT <= '{3}'".format(
                ','.join(cols),trade_code,begindate,enddate)
        cursor.execute(sql)
        volume_data = pd.DataFrame(dictfetchall(cursor))

        volume_data.dropna()
        volume_data = cleandataMixin.pandas2jsonlist(self, volume_data,numCol=cols,dataCol='DT')
        volume_data = volume_data[['DT']+cols]
        volume_data_json = volume_data.values.tolist()
        cursor.close()
        return {'name':'成交','data':volume_data_json}

    def get_mktcapdata(self,trade_code,cols = ['MKT_CAP_ARD'],begindate = None,enddate = None):
        cursor = connections['default'].cursor()
        if type(cols) is str:
            cols = [cols]
        cols = list(set(cols) & set(['MKT_CAP_ARD']))
        if begindate is None:
            begindate = '1990-01-01'
        if enddate is None:
            enddate = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT DT,{0} FROM market_marketinfo WHERE TRADE_CODE = '{1}' AND DT >= '{2}' AND DT <= '{3}'".format(
            ','.join(cols),trade_code,begindate,enddate))
        mkt_data = pd.DataFrame(dictfetchall(cursor))

        mkt_data.dropna()
        mkt_data = cleandataMixin.pandas2jsonlist(self, mkt_data,numCol=cols,dataCol='DT')
        mkt_data = mkt_data[['DT']+cols]
        mkt_data_json = mkt_data.values.tolist()
        cursor.close()
        return {'name':'成交','data':mkt_data_json}

    def get_obosdata(self,trade_code,begindate = None,enddate = None):
        cursor = connections['default'].cursor()
        if begindate is None:
            begindate = '1990-01-01'
        if enddate is None:
            enddate = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(
            "SELECT DT,VALUE FROM market_obos WHERE TRADE_CODE = %s AND DT >= %s AND DT <= %s",
            [trade_code,begindate,enddate])
        obos_data = pd.DataFrame(dictfetchall(cursor))
        obos_data = cleandataMixin.pandas2jsonlist(self, obos_data,numCol=None,pctCol='VALUE',dataCol='DT')
        obos_data_json = obos_data.values.tolist()
        cursor.close()
        return {'name':'超买超卖','data':obos_data_json}

    def get_volatilitydata(self):
        conn = connect(host='rm-uf67kg347rhjfep5c1o.mysql.rds.aliyuncs.com', user='hongze_admin', password='hongze_2018',
                       port=3306, db='stock', charset='utf8mb4', cursorclass=cursors.DictCursor)
        indexmarket = pd.read_sql(
            "SELECT A.TRADE_CODE,A.SEC_NAME,B.DT,B. CLOSE,B.AMT FROM `market_indexinfo` A "
            "LEFT JOIN market_marketinfo B ON A.TRADE_CODE = B.TRADE_CODE WHERE B.DT = "
            "(SELECT MAX(DT) FROM market_marketinfo) AND "
            "A.TRADE_CODE IN (SELECT CHILD_CODE FROM `market_basictree` WHERE `PARENT_CODE` = 'COMPOSITE')",
            con=conn)
        conn.close()
        indexmarket = cleandataMixin.pandas2jsonlist(self,indexmarket,dataCol=None,numCol=['CLOSE','AMT'])
        old_name = indexmarket.columns.values.tolist()
        indexmarket['ID'] = range(1,len(indexmarket.index)+1)
        indexmarket = indexmarket[['ID']+old_name]
        indexmarket = indexmarket.values.tolist()
        return {'data':indexmarket}


class marketView(getdataMixin,View):
    def get(self, request, *args, **kwargs):
        # 超买超卖初始图
        new_obosinfo = getdataMixin.get_obosinfo(self)
        obos_init = new_obosinfo['obos_code'][0]
        new_obosdata = getdataMixin.get_obosdata(self, obos_init['TRADE_CODE'])
        new_obosclose = getdataMixin.get_pricedata(
            self, obos_init['TRADE_CODE'],cols=['CLOSE'],
            begindate=datetime.fromtimestamp(int(new_obosdata['data'][0][0]/1000)).strftime('%Y-%m-%d'))


        return render(
            request,
            'market.html',
            context={
                'obos_select':obos_init['SEC_NAME'],**new_obosinfo, 'obos_data':new_obosdata, 'obos_close':new_obosclose
            }
        )

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class obosView(getdataMixin,View):
    def post(self, request, *args, **kwargs):
        obos_selected = request.POST['obos_selected']
        new_obosdata = getdataMixin.get_obosdata(self,obos_selected)
        new_obosclose = getdataMixin.get_pricedata(self, obos_selected)
        return JsonResponse({'obos_data':new_obosdata,'obos_close':new_obosclose})

    @method_decorator(csrf_exempt)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class volatilityRowView(getdataMixin,View):
    def post(self,request, *args, **kwargs):
        selected_row = request.POST['TRADE_CODE']
        row_data = getdataMixin.get_pricedata(self,selected_row)
        return JsonResponse(row_data)

    @method_decorator(csrf_exempt)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class volatilityView(getdataMixin,View):
    def get(self,request, *args, **kwargs):
        volatilitydata = getdataMixin.get_volatilitydata(self)
        return JsonResponse(volatilitydata)