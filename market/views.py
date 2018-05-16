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

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def index(request):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1
    return render(
        request,'index.html',context={'num_visits':num_visits}
    )
class cleandataMixin:
    def pandas2jsonlist(self,table,dataCol = 'DT',numCol = 'VALUE', pctCol = None):
        if dataCol is not None:
            table[dataCol] = [time.mktime(x.timetuple()) * 1000 for x in table[dataCol]]
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
        return {'obos_code':obos_code}

    def get_singleclosedata(self,trade_code):
        cursor = connections['default'].cursor()
        cursor.execute(
            "SELECT DT,CLOSE FROM market_marketinfo WHERE TRADE_CODE = %s",
            [trade_code])
        close_data = pd.DataFrame(dictfetchall(cursor))
        close_data = cleandataMixin.pandas2jsonlist(self, close_data,numCol='CLOSE')
        close_data = close_data[['DT','CLOSE']]
        close_data_json = close_data.values.tolist()
        return {'name':'收盘价','data':close_data_json}

    def get_obosdata(self,trade_code):
        cursor = connections['default'].cursor()
        cursor.execute(
            "SELECT DT,VALUE FROM market_obos WHERE TRADE_CODE = %s",
            [trade_code])
        obos_data = pd.DataFrame(dictfetchall(cursor))
        obos_data = cleandataMixin.pandas2jsonlist(self, obos_data,numCol=None,pctCol='VALUE')
        obos_data_json = obos_data.values.tolist()
        cursor.close()
        return {'obos_value':obos_data_json}

    def get_volatilitydata(self):
        conn = connect(host='rm-uf67kg347rhjfep5c1o.mysql.rds.aliyuncs.com', user='hongze_admin', password='hongze_2018',
                       port=3306, db='stock', charset='utf8mb4', cursorclass=cursors.DictCursor)
        indexmarket = pd.read_sql(
            "SELECT A.TRADE_CODE,A.SEC_NAME,B.DT,B. CLOSE,B.AMT FROM `market_indexinfo` A "
            "LEFT JOIN market_marketinfo B ON A.TRADE_CODE = B.TRADE_CODE WHERE B.DT = (SELECT MAX(DT) FROM market_marketinfo) AND "
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
        new_obosinfo = getdataMixin.get_obosinfo(self)
        obos_select = new_obosinfo['obos_code'][0]['TRADE_CODE']
        obos_select_name = new_obosinfo['obos_code'][0]['SEC_NAME']
        new_obosdata = getdataMixin.get_obosdata(self, obos_select)
        new_obosdata_close = getdataMixin.get_singleclosedata(self, obos_select)['data']

        return render(
            request,
            'market.html',
            context={'obos_select' : obos_select_name,**new_obosinfo, **new_obosdata,'obos_close':new_obosdata_close}
        )

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class obosView(getdataMixin,View):
    def post(self, request, *args, **kwargs):
        selected_trade_code = request.POST['obos_selected']
        new_obosdata = getdataMixin.get_obosdata(self,selected_trade_code)
        new_obosdata_close = getdataMixin.get_singleclosedata(self, selected_trade_code)['data']
        return JsonResponse({**new_obosdata,'obos_close':new_obosdata_close})

    @method_decorator(csrf_exempt)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class volatilityRowView(getdataMixin,View):
    def post(self,request, *args, **kwargs):
        selected_row = request.POST['TRADE_CODE']
        row_data = getdataMixin.get_singleclosedata(self,selected_row)
        return JsonResponse(row_data)

    @method_decorator(csrf_exempt)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class volatilityView(getdataMixin,View):
    def get(self,request, *args, **kwargs):
        volatilitydata = getdataMixin.get_volatilitydata(self)
        return JsonResponse(volatilitydata)