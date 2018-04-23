from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Dailyreplay

@login_required(login_url='/account/user_login/')
def Dailyreply_list(request):
    name = Dailyreplay.objects.filter(AUTHOR = request.user)
    return render(request,'/object/dailyreplay/dailyreplay_list.html',{'name':name})

