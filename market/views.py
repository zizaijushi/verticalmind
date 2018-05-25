from django.shortcuts import render,render_to_response
from django.http import HttpResponse,JsonResponse
# from .models import basicinfo,basictree,indexinfo,marketinfo,obos,stockinfo
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.base import View
import time
import pandas as pd
from django.db import connections
from pymysql import connect,cursors
from datetime import datetime

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class indexView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,'market/index.html',context={'data':1}
        )

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