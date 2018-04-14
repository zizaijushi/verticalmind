from django.shortcuts import render
from django.http import HttpResponse
from .models import basicinfo,basictree,indexinfo,marketinfo,obos
from django.views.decorators.csrf import csrf_exempt
import json

def index(request):

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    return render(
        request,'index.html',context={'num_visits':num_visits}
    )

def market(request):
    obos_code = obos.objects.values('TRADE_CODE').distinct()
    obos_select = obos_code[0]

    obos_data = obos.objects.filter(TRADE_CODE__exact=obos_select['TRADE_CODE']).values('VALUE','DT')

    if request.method == 'POST':
        print("good")
        data = json.loads(request.body)
        obos_select = data['obos_select']
        obos_data = obos.objects.filter(TRADE_CODE__exact=obos_select['TRADE_CODE']).values('VALUE','DT')

    # obos_data = obos.objects.filter(TRADE_CODE__name = obos_code)

    # print( obos_data)

    return render(
        request,
        'market.html',
        context={'obos_code':obos_code,'obos_select':obos_select,'obos_data':obos_data}
    )


def glxu(request):
    data = [
        [111,111],
        [222,222]
    ]

    return render(
        request,
        'glxu.html',
        {
            'data':data
        }
    )