from django.shortcuts import render,render_to_response
from django.http import HttpResponse,JsonResponse
# from .models import basicinfo,basictree,indexinfo,marketinfo,obos,stockinfo
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json,time
import pandas as pd
from datetime import datetime
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

@csrf_exempt
def market(request):
    if request.method == 'GET':
        cursor = connections['default'].cursor()
        cursor.execute(
            "SELECT DISTINCT C.TRADE_CODE_id,C.SEC_NAME FROM (SELECT A.TRADE_CODE_id,B.SEC_NAME FROM market_obos A LEFT JOIN market_indexinfo B ON A.TRADE_CODE_id = B.TRADE_CODE_id) C")
        obos_code = dictfetchall(cursor)
        # obos_code = obos.objects.values('TRADE_CODE').distinct()
        obos_select = obos_code[0]['TRADE_CODE_id']
        obos_select_name = obos_code[0]['SEC_NAME']
        cursor.execute(
            "SELECT DT,VALUE FROM market_obos WHERE TRADE_CODE_id = %s",
            [obos_select])
        obos_data = pd.DataFrame(dictfetchall(cursor))
        cursor.execute(
            "SELECT DT,CLOSE FROM market_marketinfo WHERE TRADE_CODE_id = %s",
            [obos_select])
        close_data = pd.DataFrame(dictfetchall(cursor))
        # obos_data = pd.DataFrame(list(obos.objects.filter(TRADE_CODE=obos_select['TRADE_CODE']).values('DT', 'VALUE')))
        obos_data['DT'] = [time.mktime(x.timetuple())*1000 for x in obos_data['DT']]
        obos_data['VALUE'] = [float(x)*100 for x in obos_data['VALUE']]
        # obos_data['CLOSE'] = obos_data['CLOSE'].fillna(method='ffill')
        close_data['DT'] = [time.mktime(x.timetuple()) * 1000 for x in close_data['DT']]
        close_data['CLOSE'] = [float(x) for x in close_data['CLOSE']]
        close_data = close_data[['DT','CLOSE']]
        obos_data_json = obos_data.values.tolist()
        close_data_json = close_data.values.tolist()
        cursor.close()
        return render(
            request,
            'market.html',
            context={'obos_code': obos_code, 'obos_select': obos_select_name, 'obos_data': obos_data_json,'close_data':close_data_json}
        )
    # obos_data = obos.objects.filter(TRADE_CODE__name = obos_code)

@csrf_exempt
@require_POST
def obosview(request):
    if request.method == 'POST':
        cursor = connections['default'].cursor()
        obos_select = request.POST['obos_selected']
        cursor.execute(
            "SELECT DT,VALUE FROM market_obos WHERE TRADE_CODE_id = %s",
            [obos_select])
        obos_data = pd.DataFrame(dictfetchall(cursor))
        cursor.execute(
            "SELECT DT,CLOSE FROM market_marketinfo WHERE TRADE_CODE_id = %s",
            [obos_select])
        close_data = pd.DataFrame(dictfetchall(cursor))
        # obos_data = pd.DataFrame(list(obos.objects.filter(TRADE_CODE=obos_select['TRADE_CODE']).values('DT', 'VALUE')))
        obos_data['DT'] = [time.mktime(x.timetuple())*1000 for x in obos_data['DT']]
        obos_data['VALUE'] = [float(x)*100 for x in obos_data['VALUE']]
        # obos_data['CLOSE'] = obos_data['CLOSE'].fillna(method='ffill')
        close_data['DT'] = [time.mktime(x.timetuple()) * 1000 for x in close_data['DT']]
        close_data['CLOSE'] = [float(x) for x in close_data['CLOSE']]
        close_data = close_data[['DT','CLOSE']]
        obos_data_json = obos_data.values.tolist()
        close_data_json = close_data.values.tolist()
        cursor.close()
        return JsonResponse({'obos_data':obos_data_json,'close_data':close_data_json})