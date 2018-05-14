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

class getdataMixin:
    def get_obosinfo(self):
        cursor = connections['default'].cursor()
        cursor.execute(
            "SELECT DISTINCT C.TRADE_CODE,C.SEC_NAME FROM (SELECT A.TRADE_CODE,B.SEC_NAME FROM market_obos A LEFT JOIN market_indexinfo B ON A.TRADE_CODE = B.TRADE_CODE) C")
        obos_code = dictfetchall(cursor)
        return {'obos_code':obos_code}

    def get_obosdata(self,trade_code):
        cursor = connections['default'].cursor()
        cursor.execute(
            "SELECT DT,VALUE FROM market_obos WHERE TRADE_CODE = %s",
            [trade_code])
        obos_data = pd.DataFrame(dictfetchall(cursor))
        cursor.execute(
            "SELECT DT,CLOSE FROM market_marketinfo WHERE TRADE_CODE = %s",
            [trade_code])
        close_data = pd.DataFrame(dictfetchall(cursor))
        obos_data['DT'] = [time.mktime(x.timetuple())*1000 for x in obos_data['DT']]
        obos_data['VALUE'] = [float(x)*100 for x in obos_data['VALUE']]
        close_data['DT'] = [time.mktime(x.timetuple()) * 1000 for x in close_data['DT']]
        close_data['CLOSE'] = [float(x) for x in close_data['CLOSE']]
        close_data = close_data[['DT','CLOSE']]
        obos_data_json = obos_data.values.tolist()
        close_data_json = close_data.values.tolist()
        cursor.close()
        return {'obos_data':obos_data_json,'close_data':close_data_json}

class marketView(getdataMixin,View):
    def get(self, request, *args, **kwargs):
        new_obosinfo = getdataMixin.get_obosinfo(self)
        obos_select = new_obosinfo['obos_code'][0]['TRADE_CODE_id']
        obos_select_name = new_obosinfo['obos_code'][0]['SEC_NAME']
        new_obosdata = getdataMixin.get_obosdata(self, obos_select)
        return render(
            request,
            'market.html',
            context={'obos_select' : obos_select_name,**new_obosinfo, **new_obosdata}
        )

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class obosView(getdataMixin,View):
    def post(self, request, *args, **kwargs):
        selected_trade_code = request.POST['obos_selected']
        new_obosdata = getdataMixin.get_obosdata(self,selected_trade_code)
        return JsonResponse(new_obosdata)

    @method_decorator(csrf_exempt)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)