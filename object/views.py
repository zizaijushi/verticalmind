from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .models import UserObject,Objects
from .form import UserObjectForm

@login_required(login_url='/account/user_login/')
@csrf_exempt
def object_manage(request):
    name = UserObject.objects.filter(USER = request.user)
    unlistobject = Objects.objects.exclude()
    return render(request,'/object/object_manage.html',{'name':name})