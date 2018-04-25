from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from .models import UserObject,Objects,Report
from .form import UserObjectForm,ReportForm

@login_required(login_url='/account/user_login/')
@csrf_exempt
def object_manage(request):
    if request.method == 'GET':
        name = UserObject.objects.filter(USER = request.user)
        unlistobject = Objects.objects.exclude(id__in=[x['OBJECT'] for x in list(name.values('OBJECT'))])
        return render(request, 'object/object_manage.html', {'name': name, 'unlistobject': unlistobject})
    if request.method == 'POST':
        addname = request.POST['addname']
        object = Objects.objects.get(NAME=addname)
        UserObject.objects.create(USER=request.user,OBJECT=object)
        return HttpResponse('1')

@login_required(login_url='/account/user_login/')
@csrf_exempt
@require_POST
def object_manage_del(request):
    if request.method == 'POST':
        delid = request.POST['delid']
        UserObject.objects.filter(id=delid).delete()
        return HttpResponse('1')

@login_required(login_url='/account/user_login/')
@csrf_exempt
def report_post(request):
    if request.method == 'POST':
        report_form = ReportForm(data=request.POST)
        if report_form.is_valid():
            # cd = report_form.cleaned_data
            try:
                new_report = report_form.save(commit=False)
                new_report.AUTHOR = request.user
                new_report.OBJECT = request.user.Objects.get(id=request.POST['object'])
                new_report.save()
                return HttpResponse('1')
            except:
                return HttpResponse('2')
        else:
            return HttpResponse('3')
    else:
        report_form = ReportForm()
        report_objects = request.user.UserObject.all()
        return  render(request,'object/report/report_post.html',{
            'report_form':report_form,'report_objects':report_objects
        })