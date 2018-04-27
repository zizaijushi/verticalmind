from django.shortcuts import render,get_object_or_404,render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

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
                return render_to_response('object/report/report_post.html',{
                    'oid':request.POST['object']
                })
            except:
                return HttpResponse('-1')
        else:
            return HttpResponse('-2')
    else:
        report_form = ReportForm()
        report_objects = request.user.UserObject.all()
        return  render(request,'object/report/report_post.html',{
            'report_form':report_form,'report_objects':report_objects,'oid':0
        })

@login_required(login_url='/account/user_login/')
def object_list(request,object_id):
    object = Objects.objects.get(id=object_id)
    reports = Report.objects.filter(AUTHOR=request.user,OBJECT=object_id)
    paginator = Paginator(reports,5)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
    current_reports = current_page.object_list
    return render(request,'object/object_list.html',{
        'reports':current_reports,'object':object,'page':current_page
    })

def report(request,id,slug):
    report = get_object_or_404(Report,id=id,SLUG=slug)
    return render(request,'object/report/report.html',{
        'report':report
    })

@login_required(login_url='/account/user_login')
@csrf_exempt
def report_edit(request,report_id):
    if request.method == 'GET':
        old_report = Report.objects.get(id=report_id)
        if request.user != old_report.AUTHOR:
            return HttpResponse('-3')
        report_form = ReportForm(initial={'TITAL':old_report.TITLE})
        report_objects = request.user.UserObject.all()
        return render(request,'object/report/report_edit.html',{
            'old_report':old_report,'report_objects':report_objects,'report_form':report_form,
            'old_object':old_report.OBJECT
        })
    if request.method == 'POST':
        new_report = Report.objects.get(id=report_id)
        report_form = ReportForm(data=request.POST)
        if report_form.is_valid():
            cd = report_form.cleaned_data
            try:
                new_report.TITLE = cd['TITLE']
                new_report.OBJECT = request.user.Objects.get(id=request.POST['object'])
                new_report.BODY = cd['BODY']
                new_report.save()
                return render_to_response('object/report/report_post.html',{
                    'oid':request.POST['object']
                })
            except:
                return HttpResponse('-1')
        else:
            return HttpResponse('-2')